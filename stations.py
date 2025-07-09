import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crime_prediction.settings")
django.setup()

from crimeapp.models import PoliceStation
import random

stations_data = [
    # 🔴 ERNAKULAM (5 stations)
    {"name": "Fort Kochi PS", "district": "Ernakulam", "ward": 2, "jurisdiction_area": "Fort Kochi", "lat": 9.9621, "lon": 76.2422},
    {"name": "Mattancherry PS", "district": "Ernakulam", "ward": 4, "jurisdiction_area": "Mattancherry", "lat": 9.9563, "lon": 76.2594},
    {"name": "Palarivattom PS", "district": "Ernakulam", "ward": 6, "jurisdiction_area": "Palarivattom", "lat": 10.0086, "lon": 76.3023},
    {"name": "Thrikkakara PS", "district": "Ernakulam", "ward": 8, "jurisdiction_area": "Thrikkakara", "lat": 10.0200, "lon": 76.3263},
    {"name": "Aluva PS", "district": "Ernakulam", "ward": 5, "jurisdiction_area": "Aluva", "lat": 10.1076, "lon": 76.3516},

    # 🔴 ALAPPUZHA (4 stations)
    {"name": "Alappuzha North PS", "district": "Alappuzha", "ward": 2, "jurisdiction_area": "Boat Jetty", "lat": 9.5000, "lon": 76.3400},
    {"name": "Alappuzha South PS", "district": "Alappuzha", "ward": 4, "jurisdiction_area": "Avalookunnu", "lat": 9.4700, "lon": 76.3200},
    {"name": "Haripad PS", "district": "Alappuzha", "ward": 6, "jurisdiction_area": "Haripad", "lat": 9.2885, "lon": 76.4740},
    {"name": "Cherthala PS", "district": "Alappuzha", "ward": 7, "jurisdiction_area": "Cherthala", "lat": 9.6856, "lon": 76.3315},

    # 🔵 KOTTAYAM
    {"name": "Kottayam Town PS", "district": "Kottayam", "ward": 3, "jurisdiction_area": "Kottayam Town", "lat": 9.5916, "lon": 76.5222},
    {"name": "Ettumanoor PS", "district": "Kottayam", "ward": 5, "jurisdiction_area": "Ettumanoor", "lat": 9.6869, "lon": 76.5667},

    # 🟠 THIRUVANANTHAPURAM
    {"name": "Vanchiyoor PS", "district": "Thiruvananthapuram", "ward": 6, "jurisdiction_area": "Vanchiyoor", "lat": 8.5036, "lon": 76.9450},
    {"name": "Kowdiar PS", "district": "Thiruvananthapuram", "ward": 8, "jurisdiction_area": "Kowdiar", "lat": 8.5182, "lon": 76.9588},

    # 🟡 PALAKKAD
    {"name": "Palakkad Town PS", "district": "Palakkad", "ward": 3, "jurisdiction_area": "Palakkad Town", "lat": 10.7867, "lon": 76.6548},
    {"name": "Ottapalam PS", "district": "Palakkad", "ward": 5, "jurisdiction_area": "Ottapalam", "lat": 10.7700, "lon": 76.3770},

    # 🟢 KOZHIKODE
    {"name": "Kozhikode City PS", "district": "Kozhikode", "ward": 1, "jurisdiction_area": "City Centre", "lat": 11.2588, "lon": 75.7804},
    {"name": "Feroke PS", "district": "Kozhikode", "ward": 4, "jurisdiction_area": "Feroke", "lat": 11.1833, "lon": 75.8414},

    # 🔵 KANNUR
    {"name": "Kannur Town PS", "district": "Kannur", "ward": 2, "jurisdiction_area": "Town", "lat": 11.8745, "lon": 75.3704},
    {"name": "Thalassery PS", "district": "Kannur", "ward": 3, "jurisdiction_area": "Thalassery", "lat": 11.7480, "lon": 75.4925},
]

for data in stations_data:
    station = PoliceStation(
        name=data['name'],
        district=data['district'],
        state='Kerala',
        jurisdiction_area=data['jurisdiction_area'],
        ward=data['ward'],
        pincode=str(random.randint(680000, 690000)),
        contact_number=f"0484-{random.randint(200000, 299999)}",
        email=f"{data['name'].lower().replace(' ', '_')}@keralapolice.com",
        latitude=data['lat'],
        longitude=data['lon']
    )
    station.save()
    print(f"✅ Inserted: {station.name} ({station.district})")

print("\n🎉 Police stations inserted successfully!")
