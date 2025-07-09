# forms.py
from django import forms
from .models import PoliceStation
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import get_user_model

class PoliceStationForm(forms.ModelForm):
    class Meta:
        model = PoliceStation
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'jurisdiction_area': forms.TextInput(attrs={'class': 'form-control'}),
            'ward': forms.NumberInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
        }

class PoliceUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'police_station']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make username and police_station read-only
       

class PoliceProfileForm(forms.ModelForm):
    class Meta:
        model = PoliceProfile
        fields = '__all__'
        exclude = ['user', 'police_station']
        widgets = {
            'date_of_joining': forms.DateInput(attrs={'type': 'date'})
        }
    

class CrimeReportBasicForm(forms.ModelForm):
    date_occurred = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
        initial=timezone.now
    )
    
    def clean_date_occurred(self):
        dt = self.cleaned_data['date_occurred']
        if timezone.is_naive(dt):
            return timezone.make_aware(dt)
        return dt
    
    class Meta:
        model = CrimeReport
        fields = ['crime_category', 'location', 'ward', 'description', 'date_occurred', 'severity_level']

class VictimForm(forms.ModelForm):
    class Meta:
        model = Victim
        fields = ['name', 'age', 'gender', 'contact_number', 'address', 'injuries']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'injuries': forms.Textarea(attrs={'rows': 3}),
        }

class EvidenceForm(forms.ModelForm):
    class Meta:
        model = Evidence
        fields = ['description', 'file', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class PatrolRouteForm(forms.ModelForm):
    class Meta:
        model = PatrolRoute
        fields = [ 'police_station', 'covered_locations', 
                 'total_distance', 'estimated_duration', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'estimated_duration': forms.TimeInput(attrs={'type': 'time'}),
        }

class PatrolAssignmentForm(forms.ModelForm):
    class Meta:
        model = PatrolAssignment
        fields = ['patrol_route', 'officer', 'status', 'notes']