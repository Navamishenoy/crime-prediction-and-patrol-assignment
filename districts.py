import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crime_prediction.settings")
django.setup()

from crimeapp.models import District  # adjust import if model is elsewhere

districts = [
    {
        "name": "Thiruvananthapuram", "code": "TVM",
        "min_lat": 8.2900, "max_lat": 8.9600,
        "min_lng": 76.5200, "max_lng": 77.1700
    },
    {
        "name": "Kollam", "code": "KLM",
        "min_lat": 8.7000, "max_lat": 9.1500,
        "min_lng": 76.4000, "max_lng": 76.9700
    },
    {
        "name": "Pathanamthitta", "code": "PTA",
        "min_lat": 9.1000, "max_lat": 9.6000,
        "min_lng": 76.4700, "max_lng": 77.2300
    },
    {
        "name": "Alappuzha", "code": "ALP",
        "min_lat": 9.2000, "max_lat": 9.8000,
        "min_lng": 76.2000, "max_lng": 76.6200
    },
    {
        "name": "Kottayam", "code": "KTM",
        "min_lat": 9.3000, "max_lat": 9.9000,
        "min_lng": 76.3000, "max_lng": 76.9000
    },
    {
        "name": "Idukki", "code": "IDK",
        "min_lat": 9.4000, "max_lat": 10.2000,
        "min_lng": 76.6000, "max_lng": 77.2000
    },
    {
        "name": "Ernakulam", "code": "EKM",
        "min_lat": 9.6000, "max_lat": 10.3000,
        "min_lng": 76.1000, "max_lng": 76.7000
    },
    {
        "name": "Thrissur", "code": "TSR",
        "min_lat": 10.2000, "max_lat": 10.7000,
        "min_lng": 76.0000, "max_lng": 76.5000
    },
    {
        "name": "Palakkad", "code": "PKD",
        "min_lat": 10.4000, "max_lat": 10.9000,
        "min_lng": 76.3000, "max_lng": 76.9000
    },
    {
        "name": "Malappuram", "code": "MLP",
        "min_lat": 10.7000, "max_lat": 11.2000,
        "min_lng": 75.8000, "max_lng": 76.4000
    },
    {
        "name": "Kozhikode", "code": "KKD",
        "min_lat": 11.0000, "max_lat": 11.6000,
        "min_lng": 75.5000, "max_lng": 76.2000
    },
    {
        "name": "Wayanad", "code": "WND",
        "min_lat": 11.4000, "max_lat": 11.9000,
        "min_lng": 75.8000, "max_lng": 76.5000
    },
    {
        "name": "Kannur", "code": "KNR",
        "min_lat": 11.6000, "max_lat": 12.1000,
        "min_lng": 75.1000, "max_lng": 75.8000
    },
    {
        "name": "Kasaragod", "code": "KSD",
        "min_lat": 11.9000, "max_lat": 12.7000,
        "min_lng": 74.8000, "max_lng": 75.5000
    },
]

for d in districts:
    obj = District.objects.create(
        name=d["name"],
        code=d["code"],
        min_lat=d["min_lat"],
        max_lat=d["max_lat"],
        min_lng=d["min_lng"],
        max_lng=d["max_lng"],
        boundary_coordinates=None
    )
    print(f"✅ Added: {obj.name} ({obj.code})")

print("\n🎉 All Kerala districts inserted successfully!")
