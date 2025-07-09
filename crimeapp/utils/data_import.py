# utils/data_import.py
import csv

from datetime import datetime
from django.utils import timezone
from crimeapp.models import CrimeReport, CrimeCategory, Location, PoliceStation
from django.contrib.auth import get_user_model

User = get_user_model()

def import_crime_data(csv_file_path):
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                # Get or create related objects
                category, _ = CrimeCategory.objects.get_or_create(name=row['crime_type'])
                location, _ = Location.objects.get_or_create(
                    district=row['district'],
                    block=row['block'],
                    defaults={'ward': row['ward'], 'latitude': row['latitude'], 'longitude': row['longitude']}
                )
                station, _ = PoliceStation.objects.get_or_create(name=row['assigned_police_station'])
                
                # Convert date format
                occurred_date = datetime.strptime(row['start_date'], '%d-%m-%Y %H:%M')
                
                # Create CrimeReport
                CrimeReport.objects.create(
                    crime_category=category,
                    location=location,
                    ward=row['ward'],
                    description=f"Automatically imported crime of type {row['crime_type']}",
                    date_occurred=occurred_date,
                    status='closed' if row['crime_type'] in ['Fraud', 'Vandalism'] else 'solved',
                    severity_level=int(row['severity_level']),
                    reporting_station=station,
                    is_high_priority=int(row['severity_level']) >= 4
                )
            except Exception as e:
                print(f"Error importing row {row}: {str(e)}")