from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime,random
from django.utils import timezone
ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('police', 'Police Officer'),
    ('investigator', 'Investigator'),
]

class PoliceStation(models.Model):
    id = models.CharField(primary_key=True, max_length=10, editable=False)
    name = models.CharField(max_length=100, default='Unknown')
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    jurisdiction_area= models.CharField(max_length=100)
    ward=models.IntegerField(default=1)
    pincode = models.CharField(max_length=10)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True,default='station@ps.com')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            last = PoliceStation.objects.order_by('-id').first()
            next_id = int(last.id.split('-')[1]) + 1 if last else 1
            self.id = f"PS-{next_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.jurisdiction_area}, {self.district}, {self.state}"


class User(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    police_station = models.ForeignKey(PoliceStation, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def is_admin(self):
        return self.role == 'ADMIN'

    def is_police_officer(self):
        return self.role == 'POLICE'

class PoliceProfile(models.Model):
    DESIGNATION_CHOICES = (
        ('asi', 'ASI'),
        ('si', 'SI'),
        ('ci', 'CI'),
    )
    id = models.CharField(primary_key=True, max_length=10, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    badge_number = models.CharField(max_length=20, unique=True)
    designation = models.CharField(max_length=50, choices=DESIGNATION_CHOICES)
    date_of_joining = models.DateField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    previous_appointments = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            last = PoliceProfile.objects.order_by('-id').first()
            next_id = int(last.id.split('-')[1]) + 1 if last else 1
            self.id = f"PO-{next_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.badge_number}"


class CrimeCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    severity_weight = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Weight from 1-5 for crime severity calculation"
    )
    
    def __str__(self):
        return self.name

class Location(models.Model):
    DISTRICT_CHOICES = [
        ('TVM', 'Thiruvananthapuram'),
        ('KL', 'Kollam'),
        ('PTA', 'Pathanamthitta'),
        ('ALP', 'Alappuzha'),
        ('KT', 'Kottayam'),
        ('IDK', 'Idukki'),
        ('EKM', 'Ernakulam'),
        ('TSR', 'Thrissur'),
        ('PKD', 'Palakkad'),
        ('MLP', 'Malappuram'),
        ('KK', 'Kozhikode'),
        ('WND', 'Wayanad'),
        ('KN', 'Kannur'),
        ('KSD', 'Kasargod'),
    ]
    
    district = models.CharField(max_length=3, choices=DISTRICT_CHOICES)
    ward=models.IntegerField(default=1)
    area = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    risk_level = models.IntegerField(
        choices=[(1, 'Low'), (2, 'Medium-Low'), (3, 'Medium'), (4, 'Medium-High'), (5, 'High')],
        default=1,
        help_text="Current risk level of the location (1-5)"
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
       
        ordering = ['district', 'area']

    def __str__(self):
        return f"{self.area}, {self.get_district_display()}"
    
class District(models.Model):
    name = models.CharField(max_length=100)  # e.g. "Thiruvananthapuram"
    code = models.CharField(max_length=5)    # e.g. "TVM" or "KL-01"
    
    # Bounding box fields (for map zooming)
    min_lat =models.DecimalField(max_digits=9, decimal_places=6)
    max_lat = models.DecimalField(max_digits=9, decimal_places=6)
    min_lng = models.DecimalField(max_digits=9, decimal_places=6)
    max_lng = models.DecimalField(max_digits=9, decimal_places=6)
    
    # Optional: Store simplified polygon coordinates as JSON
    boundary_coordinates = models.JSONField(null=True, blank=True)

class CrimeReport(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=9,
        editable=False,
        unique=True
    )
    STATUS_CHOICES = [
       ('reported', 'Reported'),
    ('assigned', 'Assigned'),
    ('under_investigation', 'Under Investigation'),
    ('closed', 'Closed'),
    ('solved', 'Solved'),
    ]
    crime_category = models.ForeignKey(CrimeCategory, on_delete=models.PROTECT)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    ward = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField()
    date_reported = models.DateTimeField(auto_now_add=True)
    date_occurred = models.DateTimeField(null=True, blank=True,default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')
    severity_level = models.IntegerField(
        choices=[(1, 'Minor'), (2, 'Moderate'), (3, 'Serious'), (4, 'Severe'), (5, 'Critical')],
        default=3
    )
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reporting_station = models.ForeignKey(
        PoliceStation, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True
    )
    assigned_officer = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_cases'
    )
    is_high_priority = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date_reported']
        verbose_name = "Crime Report"
        verbose_name_plural = "Crime Reports"
    
    def __str__(self):
        return f"{self.crime_category} at {self.location} on {self.date_occurred.date()} with ID {self.id}"
    
    def save(self, *args, **kwargs):
        # Auto-set high priority based on severity and category
        if self.severity_level >= 4 or self.crime_category.severity_weight >= 4:
            self.is_high_priority = True
        
        if not self.id:
        # Choose a random year from 2019 to 2024
           report_year = random.choice(range(2019, 2025))

        # Generate a random 3-digit number
           random_number = random.randint(100, 999)

        # Create the new ID
           self.id = f"CR{random_number}{report_year}"
  
        # Ensure date_occurred is timezone-aware
           if self.date_occurred and not timezone.is_aware(self.date_occurred):
               self.date_occurred = timezone.make_aware(self.date_occurred)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.id

class Victim(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('U', 'Unknown'),
    ]
    
    crime = models.ForeignKey(CrimeReport, on_delete=models.CASCADE, related_name='victims')
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        null=True,
        blank=True
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='U')
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(default='', blank=True)
    injuries = models.TextField(blank=True, help_text="Description of injuries sustained")
    is_minor = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if self.age is not None and self.age < 18:
            self.is_minor = True
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} (Victim of {self.crime})"

class Evidence(models.Model):
    crime = models.ForeignKey(CrimeReport, on_delete=models.CASCADE, related_name='evidence')
    description = models.CharField(max_length=200)
    collected_on = models.DateTimeField(auto_now_add=True)
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to='evidence/%Y/%m/%d/', blank=True, null=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Evidence #{self.id} for {self.crime}"

class PatrolSuggestions(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    predicted_crime_type = models.CharField(max_length=100)
    severity_level = models.CharField(max_length=10)
    suggested_patrols = models.IntegerField()
    assigned_patrols = models.IntegerField(null=True, blank=True) 
    suggested_on = models.DateTimeField(auto_now_add=True)
    severity = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    confidence_level = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)


    def __str__(self):  
        return f"Suggestion for {self.location} - {self.predicted_crime_type} ({self.severity_level})"
    


class PatrolRoute(models.Model):
    police_station = models.ForeignKey(PoliceStation, on_delete=models.CASCADE)
    covered_locations = models.ManyToManyField(Location)  # Covers multiple wards or hotspots
    total_distance = models.FloatField()
    estimated_duration = models.DurationField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Route for {self.police_station} ({self.start_time} to {self.end_time})"


class PatrolAssignment(models.Model):
    patrol_route = models.ForeignKey(PatrolRoute, on_delete=models.CASCADE)
    officer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'officer'})
    assigned_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('assigned', 'Assigned'), ('in_progress', 'In Progress'), ('completed', 'Completed')],
        default='assigned'
    )
    notes = models.TextField(blank=True)


    def __str__(self):
        return f"{self.officer} assigned on {self.patrol_route.covered_locations}"


class DatasetUpload(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    uploaded_file = models.FileField(upload_to='datasets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'ADMIN'})

    def __str__(self):
        return self.title


class AnalysisResult(models.Model):
    title = models.CharField(max_length=100)
    generated_on = models.DateTimeField(auto_now_add=True)
    dataset = models.ForeignKey(DatasetUpload, on_delete=models.SET_NULL, null=True)
    model_used = models.CharField(max_length=100)
    result_summary = models.TextField()
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'ADMIN'})

    def __str__(self):
        return f"{self.title} ({self.generated_on.date()})"
