import sys
import os
import django

# Point to the project root
sys.path.append("C:/Users/USER/ProjectMain")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crime_prediction.settings")
django.setup()


import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from datetime import datetime
import warnings
from crimeapp.models import PatrolSuggestions, Location
from datetime import datetime,timezone
from django.utils import timezone
from datetime import timedelta

warnings.filterwarnings("ignore")

# ---------------------------
# Configuration
# ---------------------------
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

# ---------------------------
# Load and Prepare Data
# ---------------------------
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # points to project root
csv_path = os.path.join(base_dir, "model", "crime_dataset.csv")
df = pd.read_csv(csv_path, parse_dates=['start_date'], dayfirst=True)
df['severity'] = df['crime_type'].map(SEVERITY_MAP)
district_map = {
    'Ernakulam': 'EKM',
    'Kottayam': 'KT',
    'Alappuzha': 'ALP',
    'Idukki': 'IdK',
    'Thrissur': 'TSR',
    'Malappuram': 'MLP',
    'Kannur': 'KN',
    'Pathanamthitta': 'PTA',
    'Kasaragod': 'KSD',
    'Thiruvananthapuram': 'TVM',
    'Kozhikode': 'KK',
    'Kollam': 'KL',
    'Palakkad': 'PKD',
    'Wayanad': 'WND'
}

df['district'] = df['district'].replace(district_map)


# Drop unmapped types
df.dropna(subset=['severity'], inplace=True)

# Time features
df['hour'] = df['start_date'].dt.hour
df['date'] = df['start_date'].dt.date
df['time_window'] = (df['hour'] // 6).astype(int)

# Aggregate to ward-date-window level
agg = df.groupby(['district', 'ward', 'date', 'time_window']).agg({
    'severity': ['max', 'count']
}).reset_index()
agg.columns = ['district', 'ward', 'date', 'time_window', 'max_severity', 'crime_count']

# Lag & trend features
agg.sort_values(by=['district', 'ward', 'date'], inplace=True)
agg['severity_lag1'] = agg.groupby(['district', 'ward'])['max_severity'].shift(1)
agg['severity_avg'] = agg.groupby(['district', 'ward'])['max_severity'].transform(lambda x: x.expanding().mean())

# Drop initial rows with NaNs
agg.dropna(inplace=True)

# ---------------------------
# Model Training
# ---------------------------
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

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, shuffle=False)
model.fit(X_train, y_train)

# ---------------------------
# Prediction Phase
# ---------------------------
# Use last known values per (district, ward) group for prediction
latest = agg.groupby(['district', 'ward']).last().reset_index()
latest['date'] = datetime.now().date()
latest['time_window'] = datetime.now().hour // 6

# Reuse lag and avg
latest['severity_lag1'] = latest['max_severity']
latest['severity_avg'] = latest['severity_avg']

predict_features = latest[features]
predictions = model.predict(predict_features)

# Estimate confidence as inverse of std dev of residuals per district
train_preds = model.predict(X_train)
residuals = np.abs(y_train - train_preds)

residual_df = pd.DataFrame({
    'district': X_train['district'].values,
    'residual': residuals
})

# Average residual per district (lower = higher confidence)
district_confidence = residual_df.groupby('district')['residual'].mean().reset_index()
district_confidence['confidence'] = 100 - (district_confidence['residual'] / district_confidence['residual'].max() * 100)
district_confidence.drop(columns='residual', inplace=True)

# Add predictions
latest['predicted_severity'] = predictions

# Merge confidence scores
latest = latest.merge(district_confidence, on='district', how='left')

# ---------------------------
# Suggest Wards per District
# ---------------------------
suggestions = latest.sort_values(['district', 'predicted_severity'], ascending=[True, False]) \
                    .groupby('district') \
                    .first() \
                    .reset_index()


print("\n🚨 Surveillance Deployment Suggestions for next 6 hours🚨 \n")

# Sort the DataFrame in descending order by confidence
sorted_suggestions = suggestions.sort_values(by='confidence', ascending=False)

# Iterate and print with signals
for _, row in sorted_suggestions.iterrows():
    confidence = row['confidence']

    # Define signal based on confidence level
    if confidence >= 80:
        signal = "🔴"
    elif confidence >= 50:
        signal = "🟠"
    elif confidence >= 20:
        signal = "🟡"
    else:
        signal = "⚪"

    # Print the results with signals
    print(f"District: {row['district']}")
    print(f"  ➤ Deploy in Ward: {row['ward']}")
    print(f"  ➤ Predicted Crime Severity: {row['predicted_severity']:.2f}")
    print(f"  ➤ Confidence Level: {confidence:.1f}%  {signal}\n")
def get_severity_label(score):
    if score >= 4.5:
        return "High"
    elif score >= 3.5:
        return "Medium"
    else:
        return "Low"

district_map = {
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
time_threshold = timezone.now() - timedelta(hours=6)


for _, row in sorted_suggestions.iterrows():
    district = row['district']
    ward = int(row['ward'])
    severity = float(row['predicted_severity'])
    confidence = float(row['confidence'])

    try:
        location = Location.objects.get(district=district, ward=ward)

        # Try to get existing suggestion for this location within the last 6 hours
        existing_suggestion = PatrolSuggestions.objects.filter(
            location=location,
            suggested_on__gte=time_threshold
        ).first()

        if existing_suggestion:
            # Update existing suggestion
            existing_suggestion.predicted_crime_type = "Not specified"
            existing_suggestion.severity_level = get_severity_label(severity)
            existing_suggestion.suggested_patrols = 1
            existing_suggestion.assigned_patrols = 0
            existing_suggestion.severity = severity
            existing_suggestion.confidence_level = confidence
            existing_suggestion.save()
            print(f"🔄 Updated: {existing_suggestion}")

        else:
            # Create new suggestion
            suggestion = PatrolSuggestions.objects.create(
                location=location,
                predicted_crime_type="Not specified",
                severity_level=get_severity_label(severity),
                suggested_patrols=1,
                assigned_patrols=0,
                severity=severity,
                confidence_level=confidence,
            )
            print(f"✅ Created: {suggestion}")

    except Location.DoesNotExist:
        print(f"❌ Location not found: {district} - Ward {ward}")

    except Exception as e:
        print(f"🚨 ERROR during save: {e}")