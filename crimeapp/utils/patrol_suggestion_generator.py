import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
from django.utils import timezone

from crimeapp.models import PatrolSuggestions, Location

SEVERITY_MAP = {
    'Homicide': 5,
    'Kidnapping': 4,
    'Assault': 4,
    'Robbery': 4,
    'Cybercrime': 3,
    'Fraud': 3,
    'Theft': 2,
    'Vandalism': 2
}

DISTRICT_MAP = {
    'Thiruvananthapuram': 'TVM',
    'Kollam': 'KL',
    'Pathanamthitta': 'PTA',
    'Alappuzha': 'ALP',
    'Kottayam': 'KT',
    'Idukki': 'IDK',
    'Ernakulam': 'EKM',
    'Thrissur': 'TSR',
    'Palakkad': 'PKD',
    'Malappuram': 'MLP',
    'Kozhikode': 'KK',
    'Wayanad': 'WND',
    'Kannur': 'KN',
    'Kasaragod': 'KSD',
}

def get_severity_label(score):
    if score >= 4.5:
        return "High"
    elif score >= 3.5:
        return "Medium"
    else:
        return "Low"

def generate_patrol_suggestions():
    try:
        from django.conf import settings
        import os

        # Load data
        csv_path = os.path.join(settings.BASE_DIR, "crimeapp", "model", "crime_dataset.csv")
        df = pd.read_csv(csv_path, parse_dates=['start_date'], dayfirst=True)

        df['severity'] = df['crime_type'].map(SEVERITY_MAP)
        df['district'] = df['district'].replace(DISTRICT_MAP)
        df.dropna(subset=['severity'], inplace=True)

        df['hour'] = df['start_date'].dt.hour
        df['date'] = df['start_date'].dt.date
        df['time_window'] = (df['hour'] // 6).astype(int)

        agg = df.groupby(['district', 'ward', 'date', 'time_window']).agg({
            'severity': ['max', 'count']
        }).reset_index()
        agg.columns = ['district', 'ward', 'date', 'time_window', 'max_severity', 'crime_count']
        agg.sort_values(by=['district', 'ward', 'date'], inplace=True)

        agg['severity_lag1'] = agg.groupby(['district', 'ward'])['max_severity'].shift(1)
        agg['severity_avg'] = agg.groupby(['district', 'ward'])['max_severity'].transform(lambda x: x.expanding().mean())
        agg.dropna(inplace=True)

        features = ['district', 'ward', 'time_window', 'crime_count', 'severity_lag1', 'severity_avg']
        target = 'max_severity'

        X = agg[features]
        y = agg[target]

        cat_features = ['district', 'ward']
        num_features = ['time_window', 'crime_count', 'severity_lag1', 'severity_avg']

        preprocessor = ColumnTransformer([
            ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features),
            ('num', StandardScaler(), num_features)
        ])

        model = Pipeline([
            ('prep', preprocessor),
            ('reg', GradientBoostingRegressor(n_estimators=100, random_state=42))
        ])

        X_train, _, y_train, _ = train_test_split(X, y, test_size=0.15, shuffle=False)
        model.fit(X_train, y_train)

        latest = agg.groupby(['district', 'ward']).last().reset_index()
        latest['date'] = datetime.now().date()
        latest['time_window'] = datetime.now().hour // 6
        latest['severity_lag1'] = latest['max_severity']
        latest['severity_avg'] = latest['severity_avg']

        predict_features = latest[features]
        predictions = model.predict(predict_features)

        train_preds = model.predict(X_train)
        residuals = np.abs(y_train - train_preds)

        residual_df = pd.DataFrame({
            'district': X_train['district'].values,
            'residual': residuals
        })

        district_confidence = residual_df.groupby('district')['residual'].mean().reset_index()
        district_confidence['confidence'] = 100 - (district_confidence['residual'] / district_confidence['residual'].max() * 100)
        district_confidence.drop(columns='residual', inplace=True)

        latest['predicted_severity'] = predictions
        latest = latest.merge(district_confidence, on='district', how='left')

        suggestions = latest.sort_values(['district', 'predicted_severity'], ascending=[True, False]) \
                            .groupby('district') \
                            .first() \
                            .reset_index()

        time_threshold = timezone.now() - timedelta(hours=6)
        created, updated, skipped = 0, 0, 0

        for _, row in suggestions.iterrows():
            district = row['district']
            ward = int(row['ward'])
            severity = float(row['predicted_severity'])
            confidence = float(row['confidence'])

            try:
                location = Location.objects.get(district=district, ward=ward)

                existing = PatrolSuggestions.objects.filter(
                    location=location,
                    suggested_on__gte=time_threshold
                ).first()

                if existing:
                    existing.predicted_crime_type = "Not specified"
                    existing.severity_level = get_severity_label(severity)
                    existing.suggested_patrols = 1
                    existing.assigned_patrols = 0
                    existing.severity = severity
                    existing.confidence_level = confidence
                    existing.save()
                    updated += 1
                else:
                    PatrolSuggestions.objects.create(
                        location=location,
                        predicted_crime_type="Not specified",
                        severity_level=get_severity_label(severity),
                        suggested_patrols=1,
                        assigned_patrols=0,
                        severity=severity,
                        confidence_level=confidence,
                    )
                    created += 1
            except Location.DoesNotExist:
                skipped += 1
            except Exception as e:
                print("⚠️ Error:", e)

        return f"Created: {created}, Updated: {updated}, Skipped: {skipped}"

    except Exception as e:
        return f"🚨 Error generating suggestions: {e}"
