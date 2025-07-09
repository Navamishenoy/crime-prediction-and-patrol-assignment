import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crime_prediction.settings")
django.setup()

from crimeapp.models import CrimeCategory

categories = [
    ("Theft", "Unlawful taking of property", 2),
    ("Fraud", "Deception intended for financial or personal gain", 3),
    ("Assault", "Physical attack or threat", 3),
    ("Homicide", "Unlawful killing of another person", 5),
    ("Cybercrime", "Crimes involving computers or networks", 4),
    ("Kidnapping", "Taking someone against their will", 4),
    ("Vandalism", "Deliberate destruction of property", 2),
    ("Robbery", "Theft involving force or threat", 4),
]

for name, description, severity in categories:
    obj, created = CrimeCategory.objects.get_or_create(
        name=name,
        defaults={"description": description, "severity_weight": severity}
    )
    action = "✅ Created" if created else "ℹ️ Already exists"
    print(f"{action}: {name}")

print("\n🎉 Crime categories inserted successfully!")
