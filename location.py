import os
import django
from django.utils import timezone

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crime_prediction.settings")
import sys
sys.path.append("C:/Users/USER/ProjectMain")  # ✅ Update this if needed

django.setup()

from crimeapp.models import Location

# Add all the missing locations with rough coordinates (can be refined later)
missing_locations = [
    {"district": "EKM", "ward_number": 2, "latitude": 9.9816, "longitude": 76.2999},
    {"district": "KT", "ward_number": 6, "latitude": 9.5916, "longitude": 76.5222},
    {"district": "ALP", "ward_number": 2, "latitude": 9.4980, "longitude": 76.3388},
    {"district": "IdK", "ward_number": 9, "latitude": 9.8496, "longitude": 76.9750},
    {"district": "TSR", "ward_number": 3, "latitude": 10.5276, "longitude": 76.2144},
    {"district": "MLP", "ward_number": 8, "latitude": 11.0510, "longitude": 76.0711},
    {"district": "KN", "ward_number": 1, "latitude": 11.8745, "longitude": 75.3704},
    {"district": "PTA", "ward_number": 2, "latitude": 9.2648, "longitude": 76.7870},
    {"district": "KSD", "ward_number": 8, "latitude": 12.4996, "longitude": 74.9869},
    {"district": "TVM", "ward_number": 6, "latitude": 8.5241, "longitude": 76.9366},
    {"district": "KK", "ward_number": 1, "latitude": 11.2588, "longitude": 75.7804},
    {"district": "KL", "ward_number": 1, "latitude": 8.8932, "longitude": 76.6141},
    {"district": "PKD", "ward_number": 6, "latitude": 10.7867, "longitude": 76.6548},
    {"district": "WND", "ward_number": 8, "latitude": 11.6850, "longitude": 76.1320},
    {"district": "EKM", "ward_number": 4, "latitude": 10.0236, "longitude": 76.3084},
    {"district": "TSR", "ward_number": 5, "latitude": 10.5190, "longitude": 76.2075},
    {"district": "KTM", "ward_number": 3, "latitude": 9.5916, "longitude": 76.5225},
    {"district": "TVM", "ward_number": 10, "latitude": 8.4855, "longitude": 76.9492},
    {"district": "KNR", "ward_number": 2, "latitude": 11.8741, "longitude": 75.3701},
    {"district": "WAY", "ward_number": 5, "latitude": 11.7150, "longitude": 76.1380},
    {"district": "IDK", "ward_number": 6, "latitude": 9.8432, "longitude": 77.0021},
]

created, skipped = 0, 0

for loc in missing_locations:
    obj, was_created = Location.objects.get_or_create(
        district=loc["district"],
        ward=loc["ward_number"],
        defaults={
            "area": f"Ward {loc['ward_number']}",
            "latitude": loc["latitude"],
            "longitude": loc["longitude"]
        }
    )
    if was_created:
        print(f"✅ Created: {loc['district']} - Ward {loc['ward_number']}")
        created += 1
    else:
        print(f"⚠ Already exists: {loc['district']} - Ward {loc['ward_number']}")
        skipped += 1

print(f"\n✅ Done: {created} created, {skipped} already existed")
