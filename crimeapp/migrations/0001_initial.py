# Generated by Django 5.0.7 on 2025-06-27 06:43

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CrimeCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('severity_weight', models.IntegerField(default=1, help_text='Weight from 1-5 for crime severity calculation', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
            ],
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=5)),
                ('min_lat', models.FloatField()),
                ('max_lat', models.FloatField()),
                ('min_lng', models.FloatField()),
                ('max_lng', models.FloatField()),
                ('boundary_coordinates', models.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('district', models.CharField(choices=[('TVM', 'Thiruvananthapuram'), ('KL', 'Kollam'), ('PTA', 'Pathanamthitta'), ('ALP', 'Alappuzha'), ('KT', 'Kottayam'), ('IDK', 'Idukki'), ('EKM', 'Ernakulam'), ('TSR', 'Thrissur'), ('PKD', 'Palakkad'), ('MLP', 'Malappuram'), ('KK', 'Kozhikode'), ('WND', 'Wayanad'), ('KN', 'Kannur'), ('KSD', 'Kasargod')], max_length=3)),
                ('ward', models.IntegerField(default=1)),
                ('area', models.CharField(max_length=100)),
                ('pincode', models.CharField(blank=True, max_length=6)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('risk_level', models.IntegerField(choices=[(1, 'Low'), (2, 'Medium-Low'), (3, 'Medium'), (4, 'Medium-High'), (5, 'High')], default=1, help_text='Current risk level of the location (1-5)')),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['district', 'area'],
            },
        ),
        migrations.CreateModel(
            name='PoliceStation',
            fields=[
                ('id', models.CharField(editable=False, max_length=10, primary_key=True, serialize=False)),
                ('name', models.CharField(default='Unknown', max_length=100)),
                ('district', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('jurisdiction_area', models.CharField(max_length=100)),
                ('ward', models.IntegerField(default=1)),
                ('pincode', models.CharField(max_length=10)),
                ('contact_number', models.CharField(max_length=15)),
                ('email', models.EmailField(blank=True, default='station@ps.com', max_length=254, null=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('police', 'Police Officer'), ('investigator', 'Investigator')], max_length=20)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('police_station', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='crimeapp.policestation')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='CrimeReport',
            fields=[
                ('id', models.CharField(editable=False, max_length=9, primary_key=True, serialize=False, unique=True)),
                ('ward', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.TextField()),
                ('date_reported', models.DateTimeField(auto_now_add=True)),
                ('date_occurred', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('status', models.CharField(choices=[('reported', 'Reported'), ('assigned', 'Assigned'), ('under_investigation', 'Under Investigation'), ('closed', 'Closed'), ('solved', 'Solved')], default='reported', max_length=20)),
                ('severity_level', models.IntegerField(choices=[(1, 'Minor'), (2, 'Moderate'), (3, 'Serious'), (4, 'Severe'), (5, 'Critical')], default=3)),
                ('is_high_priority', models.BooleanField(default=False)),
                ('assigned_officer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_cases', to=settings.AUTH_USER_MODEL)),
                ('crime_category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='crimeapp.crimecategory')),
                ('reported_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='crimeapp.location')),
                ('reporting_station', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='crimeapp.policestation')),
            ],
            options={
                'verbose_name': 'Crime Report',
                'verbose_name_plural': 'Crime Reports',
                'ordering': ['-date_reported'],
            },
        ),
        migrations.CreateModel(
            name='DatasetUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('uploaded_file', models.FileField(upload_to='datasets/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('uploaded_by', models.ForeignKey(limit_choices_to={'role': 'ADMIN'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AnalysisResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('generated_on', models.DateTimeField(auto_now_add=True)),
                ('model_used', models.CharField(max_length=100)),
                ('result_summary', models.TextField()),
                ('generated_by', models.ForeignKey(limit_choices_to={'role': 'ADMIN'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('dataset', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='crimeapp.datasetupload')),
            ],
        ),
        migrations.CreateModel(
            name='Evidence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200)),
                ('collected_on', models.DateTimeField(auto_now_add=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='evidence/%Y/%m/%d/')),
                ('notes', models.TextField(blank=True)),
                ('collected_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('crime', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evidence', to='crimeapp.crimereport')),
            ],
        ),
        migrations.CreateModel(
            name='PatrolRoute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_distance', models.FloatField()),
                ('estimated_duration', models.DurationField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('covered_locations', models.ManyToManyField(to='crimeapp.location')),
                ('police_station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crimeapp.policestation')),
            ],
        ),
        migrations.CreateModel(
            name='PatrolAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('assigned', 'Assigned'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='assigned', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('officer', models.ForeignKey(limit_choices_to={'role': 'officer'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('patrol_route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crimeapp.patrolroute')),
            ],
        ),
        migrations.CreateModel(
            name='PatrolSuggestions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('predicted_crime_type', models.CharField(max_length=100)),
                ('severity_level', models.CharField(max_length=10)),
                ('suggested_patrols', models.IntegerField()),
                ('assigned_patrols', models.IntegerField(blank=True, null=True)),
                ('suggested_on', models.DateTimeField(auto_now_add=True)),
                ('severity', models.DecimalField(decimal_places=2, default=1.0, max_digits=5)),
                ('confidence_level', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crimeapp.location')),
            ],
        ),
        migrations.CreateModel(
            name='PoliceProfile',
            fields=[
                ('id', models.CharField(editable=False, max_length=10, primary_key=True, serialize=False)),
                ('badge_number', models.CharField(max_length=20, unique=True)),
                ('designation', models.CharField(choices=[('asi', 'ASI'), ('si', 'SI'), ('ci', 'CI')], max_length=50)),
                ('date_of_joining', models.DateField()),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('previous_appointments', models.TextField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Victim',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('age', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(120)])),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('U', 'Unknown')], default='U', max_length=1)),
                ('contact_number', models.CharField(blank=True, max_length=15, null=True)),
                ('address', models.TextField(blank=True, default='')),
                ('injuries', models.TextField(blank=True, help_text='Description of injuries sustained')),
                ('is_minor', models.BooleanField(default=False)),
                ('crime', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='victims', to='crimeapp.crimereport')),
            ],
        ),
    ]
