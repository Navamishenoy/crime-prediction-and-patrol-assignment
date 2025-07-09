import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crime_prediction.settings")
django.setup()

from django.contrib.auth import get_user_model
from crimeapp.models import PoliceStation, PoliceProfile
from datetime import date
import random

User = get_user_model()

# Fetch police stations from specific districts
target_districts = ["Ernakulam", "Thiruvananthapuram"]
stations = list(PoliceStation.objects.filter(district__in=target_districts).order_by('?')[:8])

first_names = ["Arun", "Ravi", "Sneha", "Akhil", "Neena", "Rahul", "Meera", "Vishnu", "Mathew", "Fahad", "Anil", "Ajith", "Suresh", "Vijay"]
last_names = ["Kumar", "Varma", "Joseph", "Nair", "Pillai", "Thomas", "Usman", "Rajan", "S", "Suresh", "Menon"]

designations = ["CI", "SI", "ASI"]
created_users = 0
count = 0

for station in stations:
    officers_per_station = random.randint(4, 8)

    for _ in range(officers_per_station):
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        username = f"{fname.lower()}{lname.lower()}{count}"
        email = f"{username}@kps.com"

        # ✅ Create user with proper names
        user = User.objects.create_user(
            username=username,
            password="police4321",
            email=email,
            first_name=fname,
            last_name=lname,
            role="POLICE",
            police_station=station
        )

        # Joining date logic
        doj = date(
            year=random.randint(2020, 2024),
            month=random.randint(1, 12),
            day=random.randint(1, 28)
        )

        badge = f"B{random.randint(1000,9999)}{count}"
        phone = f"9447{random.randint(100000, 999999)}"

        PoliceProfile.objects.create(
            user=user,
            badge_number=badge,
            designation=random.choice(designations),
            date_of_joining=doj,
            phone_number=phone,
            address=f"{fname} {lname} house, {station.jurisdiction_area}, {station.district}",
            previous_appointments="Transferred from HQ"
        )

        print(f"✅ Created: {fname} {lname} ({username}) - {station.name}")
        created_users += 1
        count += 1

print(f"\n🎉 Total officers created: {created_users}")