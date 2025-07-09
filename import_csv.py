import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crime_prediction.settings')
django.setup()

import random
import pandas as pd
from datetime import datetime
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth import get_user_model
from crimeapp.models import CrimeReport, CrimeCategory, Location

# Django setup


User = get_user_model()

# Load CSV
df = pd.read_csv('crime_data.csv')

# Crime type to category ID map
crime_type_to_id = {
    'Theft': 1,
    'Assault': 2,
    'Fraud': 3,
    'Cybercrime': 4,
    'Homicide': 5,
    'Robbery': 6,
    'Kidnapping': 7,
    'Vandalism': 8
}

for i, row in df.iterrows():
    try:
        # Parse the date
        occurred_date = datetime.strptime(row['start_date'], '%d-%m-%Y %H:%M')
        
        # Find existing location
        try:
            location = Location.objects.get(
                latitude=round(float(row['latitude']), 6),
                longitude=round(float(row['longitude']), 6)
            )
        except Location.DoesNotExist:
            print(f"❌ Location not found for coordinates: {row['latitude']}, {row['longitude']}")
            continue
        
        # Get crime category
        category_id = crime_type_to_id.get(row['crime_type'])
        if not category_id:
            print(f"Skipping unknown crime_type: {row['crime_type']}")
            continue
        
        category = CrimeCategory.objects.get(id=category_id)
        
        # Generate report ID
        report_id = f"CR{i+1:04d}"
        
        # Set severity and priority
        severity = int(row['severity_level'])
        is_high = severity >= 4
        
        # Create the crime report
        CrimeReport.objects.create(
            id=report_id,
            crime_category=category,
            location=location,
            ward=row['ward'],
            description=f"Imported crime of type {row['crime_type']}",
            date_occurred=occurred_date,
            status='reported',
            severity_level=severity,
            is_high_priority=is_high
        )
        
        print(f"✅ Inserted crime report {report_id} for location {location}")
    except Exception as e:
        print(f"❌ Error at row {i}: {str(e)}")

print("🎉 Import complete!")
