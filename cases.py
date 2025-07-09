import os
import django
import random
from datetime import datetime
from django.db.models import Q
from geopy.distance import geodesic
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crime_prediction.settings")
django.setup()

from django.contrib.auth import get_user_model
from crimeapp.models import CrimeCategory, Location, CrimeReport, PoliceStation, PoliceProfile

User = get_user_model()

# Map crime_type to CrimeCategory ID
crime_types = CrimeCategory.objects.all()
crime_type_to_id = {cat.name: cat.id for cat in crime_types}

import pandas as pd
df = pd.read_csv("crime_data.csv")

for i, row in df.iterrows():
    try:
        occurred_date = datetime.strptime(row['start_date'], '%d-%m-%Y %H:%M')
        if not timezone.is_aware(occurred_date):
            occurred_date = timezone.make_aware(occurred_date)

        # Find nearest police station in same district
        stations = PoliceStation.objects.filter(district=row['district'])
        if not stations.exists():
            print(f"⚠️ No stations in {row['district']} — skipping row {i}")
            continue

        current_loc = (row['latitude'], row['longitude'])
        nearest_station = min(stations, key=lambda s: geodesic(current_loc, (s.latitude, s.longitude)).km)

        # Get or create location
        location, _ = Location.objects.get_or_create(
            district=row['district'],
            area=row['block'],
            ward=row['ward'],
            latitude=row['latitude'],
            longitude=row['longitude'],
            defaults={'risk_level': 3}
        )

        # Crime category
        category_id = crime_type_to_id.get(row['crime_type'])
        if not category_id:
            print(f"Skipping unknown crime_type: {row['crime_type']}")
            continue
        category = CrimeCategory.objects.get(id=category_id)

        # Officer assignment
        officers = User.objects.filter(police_station=nearest_station)
        assigned_officer = random.choice(list(officers)) if officers.exists() else None

        # Create and save CrimeReport instance
        report = CrimeReport(
            crime_category=category,
            location=location,
            ward=row['ward'],
            description='Imported from CSV',
            date_occurred=occurred_date,
            status='reported',
            severity_level=int(row['severity_level']),
            reported_by=assigned_officer,
            assigned_officer=assigned_officer,
            reporting_station=nearest_station
        )
        report.save()  # This will trigger ID, priority, and timezone logic

        print(f"✅ Inserted: {report.id} ({category.name}) in {row['district']}")

    except Exception as e:
        print(f"❌ Error at row {i}: {e}")
