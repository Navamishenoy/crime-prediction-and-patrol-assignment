from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count,Q
from django.shortcuts import get_object_or_404
import json
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseForbidden
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from .models import *
from .forms import *
from django.utils.dateparse import parse_datetime
import folium


def user_login(request):
    """
    Handles authentication for all user types
    Redirects to appropriate dashboard based on role
    Shows error messages for invalid login attempts
    """
    # If user is already authenticated, redirect them
    if request.user.is_authenticated:
        return role_redirect(request)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
 
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return role_redirect(request)  # Pass request instead of user
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    
    # GET request - show login form
    return render(request, 'accounts/login.html')

def user_logout(request):
    """Logs out user and redirects to login page"""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('login')


def role_redirect(request):
    """Helper function to redirect users based on their role"""
    if not request.user.is_authenticated:
        messages.error(request, 'Please login first')
        return redirect('login')
    # Check for admin (both superuser and role='admin')
    if getattr(request.user, 'is_superuser', False) or getattr(request.user, 'role', None) == 'admin':
        return redirect('admin_dashboard')
    elif getattr(request.user, 'role', None) == 'police':
        return redirect('police_dashboard')
    
    messages.error(request, 'Unauthorized access')
    return redirect('login')

import folium
from pathlib import Path
def home(request):
    context = {
        'user': request.user,
        'today': timezone.now().date(),
    }
    if request.user.is_authenticated:
       if getattr(request.user, 'is_superuser', False) or getattr(request.user, 'role', None) == 'admin':
          context = {}

          total_crimes = CrimeReport.objects.count()
          solved_crimes = CrimeReport.objects.filter(status='closed').count()
          high_priority = CrimeReport.objects.filter(is_high_priority=True).count()
          station_count = PoliceStation.objects.count()
          officer_count = PoliceProfile.objects.count()
          recent_stations = PoliceStation.objects.order_by('-id')[:5]
          crime_types = CrimeCategory.objects.annotate(count=Count('crimereport')).order_by('-count')[:10]

            # District short code to full name
          district_code_to_name = {
                'Ern': 'Ernakulam',
                'Thr': 'Thrissur',
                'Koz': 'Kozhikode',
                'Kol': 'Kollam',
                'Kot': 'Kottayam',
                'Pal': 'Palakkad',
                'Mal': 'Malappuram',
                'Kas': 'Kasaragod',
                'Way': 'Wayanad',
                'Idu': 'Idukki',
                'Alp': 'Alappuzha',
                'Pat': 'Pathanamthitta',
                'Tvm': 'Thiruvananthapuram',
                'Knl': 'Kannur',
            }

            # ✅ District-wise Crime Count
          district_qs = CrimeReport.objects.values('location__district').annotate(count=Count('id')).order_by('-count')
          district_labels = [district_code_to_name.get(d['location__district'], 'Unknown') for d in district_qs]
          district_data = [d['count'] for d in district_qs]

            # ✅ Crime Category-wise Crime Count
          crime_type_qs = CrimeReport.objects.values('crime_category__name').annotate(count=Count('id')).order_by('-count')
          crime_type_labels = [c['crime_category__name'] for c in crime_type_qs]
          crime_type_data = [c['count'] for c in crime_type_qs]

            # ✅ Kerala Map with Circle Markers
          m = folium.Map(location=[10.8505, 76.2711], zoom_start=7)
          district_coords = {
                "Ernakulam": [9.9816, 76.2999],
                "Thiruvananthapuram": [8.5241, 76.9366],
                "Kozhikode": [11.2588, 75.7804],
                "Kannur": [11.8745, 75.3704],
                "Kollam": [8.8932, 76.6141],
                "Alappuzha": [9.4980, 76.3388],
                "Idukki": [9.8496, 76.9750],
                "Palakkad": [10.7867, 76.6548],
                "Malappuram": [11.0510, 76.0711],
                "Thrissur": [10.5276, 76.2144],
                "Kottayam": [9.5916, 76.5222],
                "Pathanamthitta": [9.2648, 76.7870],
                "Wayanad": [11.6850, 76.1320],
                "Kasaragod": [12.4996, 74.9869]
            }

          for district, coord in district_coords.items():
                folium.CircleMarker(
                    location=coord,
                    radius=12,
                    popup=district,
                    color='blue',
                    fill=True,
                    fill_opacity=0.6
                ).add_to(m)

            # Save map
          map_path = Path(settings.BASE_DIR) / 'crimeapp/static/maps/admin_map.html'
          m.save(map_path)

            # ✅ Final context to template
          context.update({
                'crime_count': total_crimes,
                'solved_count': solved_crimes,
                'high_priority_count': high_priority,
                'station_count': station_count,
                'officer_count': officer_count,
                'recent_stations': recent_stations,

                'crime_type_labels': json.dumps(crime_type_labels),
                'crime_type_data': json.dumps(crime_type_data),

                'district_labels': json.dumps(district_labels),
                'district_data': json.dumps(district_data),

                'district_map': '/static/maps/admin_map.html'
            })

          return render(request, 'policeadmin/home.html', context) 
       elif request.user.role == 'police':
            try:
                profile = PoliceProfile.objects.get(user=request.user)
            except PoliceProfile.DoesNotExist:
                return HttpResponseForbidden("Police profile not found")

            station = profile.user.police_station
            district = station.district
            officer_district = district

            district_coords = {
                    "Ernakulam": [9.9816, 76.2999],
                    "Thiruvananthapuram": [8.5241, 76.9366],
                    # ... all districts
            }

            center = district_coords.get(district, [10.8505, 76.2711])
            m = folium.Map(location=center, zoom_start=11)
            folium.Marker(location=center, tooltip=f"{district} Station").add_to(m)

            map_path = Path(settings.BASE_DIR) / 'crimeapp/static/maps/admin_map.html'
            m.save(map_path)

            context['designation'] = profile.get_designation_display()
            context['station'] = profile.user.police_station
            context['officer_district'] = officer_district
            context['district'] = district

            if profile.designation in ['CI', 'SI']:
                station_crimes = CrimeReport.objects.filter(reporting_station=station)
                total_crimes = station_crimes.count()
                solved_crimes = station_crimes.filter(status='solved').count()
                high_priority = station_crimes.filter(is_high_priority=True).count()
                active_officers = PoliceProfile.objects.filter(user__police_station=station, user__is_active=True).count()
                recent_crimes = station_crimes.select_related('crime_category', 'location').order_by('-date_reported')[:10]
                thirty_days_ago = timezone.now() - timedelta(days=30)
                crime_trend = station_crimes.filter(date_reported__gte=thirty_days_ago).extra({'date': "date(date_reported)"}).values('date').annotate(count=Count('id')).order_by('date')
                status_distribution = station_crimes.values('status').annotate(count=Count('id')).order_by('-count')

                context.update({
                    'station_crime_count': total_crimes,
                    'solved_count': solved_crimes,
                    'high_priority_count': high_priority,
                    'active_officers': active_officers,
                    'recent_crimes': recent_crimes,
                    'trend_dates': json.dumps([item['date'].strftime('%b %d') for item in crime_trend]),
                    'trend_counts': json.dumps([item['count'] for item in crime_trend]),
                    'status_labels': json.dumps([item['status'].replace('_', ' ').title() for item in status_distribution]),
                    'status_data': json.dumps([item['count'] for item in status_distribution]),
                    'district_map': '/static/maps/admin_map.html'
                })
                return render(request, 'patrols/station_admin/admin_home.html', context)

            elif profile.designation == 'ASI':
                assigned_cases = CrimeReport.objects.filter(assigned_officer=request.user).select_related('crime_category', 'location').order_by('-date_reported')
                total_cases = assigned_cases.count()
                solved_cases = assigned_cases.filter(status='solved').count()
                pending_cases = assigned_cases.exclude(Q(status='solved') | Q(status='closed')).count()
                overdue_cases = assigned_cases.filter(date_reported__lt=timezone.now()-timedelta(days=7)).exclude(Q(status='solved') | Q(status='closed')).count()
                recent_cases = assigned_cases[:5]
                #'district_data': json.dumps(district_data),
                #  'crime_type_data': json.dumps(crime_type_data),
                context.update({
                    'assigned_cases_count': total_cases,
                    'solved_cases_count': solved_cases,
                    'pending_cases_count': pending_cases,
                    'overdue_cases_count': overdue_cases,
                    'assigned_cases': recent_cases,
                    'district_map': '/static/maps/admin_map.html'
                })
                return render(request, 'patrols/regular/home.html', context)
    else:
        return redirect('login')
    return HttpResponseForbidden("Invalid user role")

@login_required
def case_list(request):
    # Start with all cases visible to the user
    if request.user.role == 'admin':
        cases = CrimeReport.objects.all()
    elif request.user.role == 'police':
        # Police users see cases from their station or assigned to them
        cases = CrimeReport.objects.filter(
            Q(reporting_station=request.user.police_station) |
            Q(assigned_officer=request.user)
        )
    else:
        cases = CrimeReport.objects.none()  # No access for other roles

    # Filtering
    category_filter = request.GET.get('category')
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    search_query = request.GET.get('search')

    if category_filter:
        cases = cases.filter(crime_category__id=category_filter)
    if status_filter:
        cases = cases.filter(status=status_filter)
    if priority_filter:
        cases = cases.filter(is_high_priority=(priority_filter == 'high'))
    if search_query:
        cases = cases.filter(
            Q(id__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__area__icontains=search_query)
        )

    # Sorting
    sort_by = request.GET.get('sort', '-date_reported')
    cases = cases.order_by(sort_by)

    # Pagination
    paginator = Paginator(cases, 25)  # Show 25 cases per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'cases': page_obj,
        'categories': CrimeCategory.objects.all(),
        'status_choices': CrimeReport.STATUS_CHOICES,
        'current_filters': {
            'category': category_filter,
            'status': status_filter,
            'priority': priority_filter,
            'search': search_query,
            'sort': sort_by,
        }
    }
    return render(request, 'cases/case_list.html', context)

@login_required
def case_detail(request, id):  # Using pk parameter
    case = get_object_or_404(CrimeReport, id=id)  
    officers = User.objects.filter(
        role='POLICE',
        police_station=case.reported_by.police_station
    ) if case.reported_by else []# Changed to use id=pk
    district={
        'Ern':'Ernakulam',
        'Thr':'Thrissur',
        'Koz':'Kozhikode',
        'Kol':'Kollam',
        'Kot':'Kottayam',
        'Pal':'Palakkad',
        'Mal':'Malappuram',
        'Kas':'Kasaragod',
        'Way':'Wayanad',
        'Idu':'Idukki',
        'Alp':'Alappuzha',
        'Pat':'Pathanamthitta',
        'Tvm':'Thiruvananthapuram',
        'Knl':'Kannur',
    }
    if case.location.district in district:
        district_name = district[case.location.district]
    else:
        district_name = 'Unknown'
    evidence=Evidence.objects.filter(crime=case).select_related('collected_by')
    if not evidence:
        evidence = None

    victim= Victim.objects.filter(crime=case).select_related('crime')
    # Calculate risk width based on severity level
    can_edit = (request.user.role == 'admin' or 
                request.user == case.assigned_officer or 
                request.user == case.reported_by)
    
    # Get available officers from the same station
    available_officers = User.objects.filter(
        role='police',
        police_station=case.reporting_station
    ).exclude(id=case.assigned_officer_id if case.assigned_officer else None)

    context = {
        'case': case,
        'district_name': district_name,
        'case_location.risk_width': case.severity_level * 20,
        'officers': officers,
        'page_title': f'Case {case.id}',
        'evidence': evidence,
        'victims': victim,
        'can_edit': can_edit,
        'available_officers': available_officers,
    }
    return render(request, 'cases/case_detail.html', context)


@login_required
def create_crime_report(request):
    current_step = request.session.get('crime_report_step', 1)
    
    if request.method == 'POST':
        if 'next_step' in request.POST:
            if current_step == 1:
                basic_form = CrimeReportBasicForm(request.POST, prefix='basic')
                if basic_form.is_valid():
                    basic_data = basic_form.cleaned_data
                    # Store datetime as ISO string
                    date_occurred = basic_data['date_occurred']
                    request.session['basic_form_data'] = {
                        'crime_category_id': basic_data['crime_category'].id,
                        'location_id': basic_data['location'].id,
                        'ward': basic_data['ward'],
                        'description': basic_data['description'],
                        'date_occurred': date_occurred.isoformat(),
                        'severity_level': basic_data['severity_level'],
                    }
                    request.session['crime_report_step'] = 2
                    return redirect('case_add')
            
            elif current_step == 2:
                victim_form = VictimForm(request.POST, prefix='victim')
                if victim_form.is_valid():
                    request.session['victim_form_data'] = victim_form.cleaned_data
                    request.session['crime_report_step'] = 3
                    return redirect('case_add')
            
        elif 'prev_step' in request.POST:
            request.session['crime_report_step'] = current_step - 1
            return redirect('case_add')
        
        elif 'submit' in request.POST and current_step == 3:
            evidence_form = EvidenceForm(request.POST, request.FILES, prefix='evidence')
            if evidence_form.is_valid():
                basic_data = request.session['basic_form_data']
                
                # Parse datetime from ISO string - it will maintain its timezone
                date_occurred = parse_datetime(basic_data['date_occurred'])
                
                crime_report = CrimeReport.objects.create(
                    crime_category_id=basic_data['crime_category_id'],
                    location_id=basic_data['location_id'],
                    ward=basic_data['ward'],
                    description=basic_data['description'],
                    date_occurred=date_occurred,
                    severity_level=basic_data['severity_level'],
                    reported_by=request.user,
                    reporting_station=request.user.police_station,
                )
                
                Victim.objects.create(
                    crime=crime_report,
                    **request.session['victim_form_data']
                )
                
                evidence = evidence_form.save(commit=False)
                evidence.crime = crime_report
                evidence.collected_by = request.user
                evidence.save()
                
                # Clear session
                del request.session['crime_report_step']
                del request.session['basic_form_data']
                del request.session['victim_form_data']
                
                return redirect('case_detail', id=crime_report.id)
    
    # GET request - initialize forms
    if current_step == 1:
        initial = {}
        if 'basic_form_data' in request.session:
            basic_data = request.session['basic_form_data']
            try:
                date_occurred = parse_datetime(basic_data['date_occurred'])
                initial = {
                    'crime_category': CrimeCategory.objects.get(id=basic_data['crime_category_id']),
                    'location': Location.objects.get(id=basic_data['location_id']),
                    'ward': basic_data['ward'],
                    'description': basic_data['description'],
                    'date_occurred': date_occurred,
                    'severity_level': basic_data['severity_level'],
                }
            except (KeyError, CrimeCategory.DoesNotExist, Location.DoesNotExist):
                # If data is corrupted, start fresh
                del request.session['crime_report_step']
                del request.session['basic_form_data']
                return redirect('create_crime_report')
                
        basic_form = CrimeReportBasicForm(initial=initial, prefix='basic')
    
    elif current_step == 2:
        initial = request.session.get('victim_form_data', {})
        victim_form = VictimForm(initial=initial, prefix='victim')
    
    elif current_step == 3:
        evidence_form = EvidenceForm(prefix='evidence')
    
    context = {
        'basic_form': basic_form if current_step == 1 else None,
        'victim_form': victim_form if current_step == 2 else None,
        'evidence_form': evidence_form if current_step == 3 else None,
        'current_step': current_step,
        'total_steps': 3,
    }
    return render(request, 'cases/case_form.html', context)


@login_required
def assign_officer(request, pk):
    case = get_object_or_404(CrimeReport, id=pk)
    
    if request.method == 'POST':
        officer_id = request.POST.get('officer_id')
        
        # Debug print
        print(f"Attempting to assign officer {officer_id} to case {pk}")
        
        try:
            officer = User.objects.get(pk=officer_id, role='police')
            
            # Verify officer is from same station
            if officer.police_station != case.reporting_station:
                messages.error(request, "Officer must be from the same police station")
                print("Station mismatch error")
            else:
                case.assigned_officer = officer
                case.save()
                messages.success(request, f"Assigned Officer: {officer.username}")
                print("Assignment successful")
        except User.DoesNotExist:
            messages.error(request, "Invalid officer selected")
            print("Officer not found")
        
        return redirect('case_detail', id=pk)
    
    messages.error(request, "Invalid request method")
    return redirect('case_detail', id=pk)

@login_required
def unassign_officer(request, case_id):
    case = get_object_or_404(CrimeReport, id=case_id)
    
    # Permission check
    if not (request.user.role == 'admin' or request.user == case.reported_by):
        messages.error(request, "You don't have permission to unassign officers")
        return redirect('case_detail', id=case_id)
    
    case.assigned_officer = None
    case.save()
    messages.success(request, "Officer unassigned successfully")
    return redirect('case_detail', id=case_id)

def case_status_update(request,case_id):
    case=get_object_or_404(CrimeReport,id=case_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(CrimeReport.STATUS_CHOICES):
            case.status = new_status
            case.save()
            messages.success(request, f"Case status updated to {new_status}")
        else:
            messages.error(request, "Invalid status selected")
        return redirect('case_detail', id=case_id)
    
from django.conf import settings
import requests
from .utils.geo import haversine_distance
from django.db.models import Q


@login_required
def patrol_assign(request):
    user = request.user
    recent_crimes = CrimeReport.objects.filter(date_occurred__gte=timezone.now() - timedelta(days=30))
    officers = User.objects.filter(police_station=user.police_station)

    # Role-specific assignment filtering
    if hasattr(user, 'police_station'):
        assignments = PatrolAssignment.objects.filter(
            patrol_route__police_station=user.police_station
        ).select_related('officer', 'patrol_route', 'patrol_route__police_station') \
         .prefetch_related('patrol_route__covered_locations')
    else:
        assignments = PatrolAssignment.objects.all().select_related(
            'officer', 'patrol_route', 'patrol_route__police_station'
        ).prefetch_related('patrol_route__covered_locations')

    high_priority_count = recent_crimes.filter(severity_level__gt=3).count()

    profile = PoliceProfile.objects.get(user=user)
    station = profile.user.police_station
    station_coords = (station.latitude, station.longitude)
    district = station.district

    district_map = {
        'Thiruvananthapuram': 'TVM', 'Kollam': 'KL', 'Pathanamthitta': 'PTA',
        'Alappuzha': 'ALP', 'Kottayam': 'KT', 'Idukki': 'IDK', 'Ernakulam': 'EKM',
        'Thrissur': 'TSR', 'Palakkad': 'PKD', 'Malappuram': 'MLP',
        'Kozhikode': 'KK', 'Wayanad': 'WND', 'Kannur': 'KN', 'Kasargod': 'KSD'
    }
    district_code = district_map.get(district, district)
    geojson_url = "https://raw.githubusercontent.com/geohacker/kerala/master/geojsons/district.geojson"
    geojson_data = requests.get(geojson_url).json()
    m = folium.Map(location=station_coords, zoom_start=11)

    suggestions = PatrolSuggestions.objects.filter(location__district=district_code)
    all_stations = PoliceStation.objects.filter(district=district)
    
    suggestion_station_map = {}
    for suggestion in suggestions:
        ward_coord = (suggestion.location.latitude, suggestion.location.longitude)
        nearest_station = None
        shortest_distance = float('inf')

        print(f"Current station: {station.name} — District: {station.district}")
        print("Found stations:")
    

        for ps in all_stations:
            print(f"  - {ps.name} ({ps.latitude}, {ps.longitude})")
            ps_coord = (ps.latitude, ps.longitude)
            dist = haversine_distance(ward_coord, ps_coord)
            print(dist)
            if dist < shortest_distance:
                shortest_distance = dist
                nearest_station = ps
            folium.Marker(
            location=(ps.latitude, ps.longitude),
            popup=f"Police Station: {ps .name}",
            icon=folium.Icon(color='red', icon='glyphicon glyphicon-tower')
            ).add_to(m)

        if nearest_station:
            suggestion_station_map[suggestion.id] = {
                'station': nearest_station,
                'distance': round(shortest_distance, 2)
            }

    # Map visualization
    

    for feature in geojson_data["features"]:
        if feature["properties"]["DISTRICT"].lower() == district.lower():
            folium.GeoJson(
                feature,
                name=district,
                style_function=lambda feat: {
                    "fillColor": "#f1e1a0",
                    "color": "black",
                    "weight": 4,
                    "fillOpacity": 0.25
                },
                tooltip=district
            ).add_to(m)

    folium.Marker(
        location=station_coords,
        popup=f"Police Station: {station.name}",
        icon=folium.Icon(color='blue', icon='shield')
    ).add_to(m)

    severity_colors = {"High": "red", "Medium": "orange", "Low": "yellow"}

    for suggestion in suggestions:
        loc = suggestion.location
        color = severity_colors.get(suggestion.severity_level, "gray")

        # Draw hotspot circle
        folium.CircleMarker(
            location=(loc.latitude, loc.longitude),
            radius=10,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            tooltip=f"Ward {loc.ward} – {suggestion.severity_level} severity"
        ).add_to(m)

        # Add nearest station + line
        nearest_info = suggestion_station_map.get(suggestion.id)
        if nearest_info:
            ps = nearest_info['station']
            ps_coord = (ps.latitude, ps.longitude)
            dist = nearest_info['distance']

            folium.Marker(
                location=ps_coord,
                popup=f"Nearest PS: {ps.name}",
                icon=folium.Icon(color='darkblue', icon='glyphicon glyphicon-home')
            ).add_to(m)

            folium.PolyLine(
                locations=[(loc.latitude, loc.longitude), ps_coord],
                color="blue",
                dash_array="5",
                tooltip=f"Assigned from {ps.name} ({dist} km)"
            ).add_to(m)

    map_path = Path(settings.BASE_DIR) / 'crimeapp/static/maps/patrol_assignment_map.html'
    m.save(map_path)

    # Form handling
    if request.method == 'POST':
        route_form = PatrolRouteForm(request.POST)
        assignment_form = PatrolAssignmentForm(request.POST)
        if route_form.is_valid() and assignment_form.is_valid():
            route = route_form.save()
            assignment = assignment_form.save(commit=False)
            assignment.patrol_route = route
            assignment.save()
            return redirect('patrol_assign')
    else:
        route_form = PatrolRouteForm()
        assignment_form = PatrolAssignmentForm()

    return render(request, 'patrols/station_admin/assign.html', {
        'patrol_assignments': assignments,
        'recent_crimes': recent_crimes,
        'officers': officers,
        'suggestions': suggestions,
        'station': station,
        'map_path': '/static/maps/patrol_assignment_map.html',
        'form': route_form,
        'assignment_form': assignment_form,
        'available_officers': officers,
        'high_priority_count': high_priority_count,
    })

def crime_map_modal(request, crime_id):
    try:
        crime = CrimeReport.objects.get(id=crime_id)
        lat, lng = crime.location.latitude, crime.location.longitude
        crime_type = crime.crime_category.name

        m = folium.Map(location=[lat, lng], zoom_start=15)
        folium.Marker(
            [lat, lng],
            tooltip=f"{crime_type} at Ward {crime.ward}",
            icon=folium.Icon(color='red', icon='exclamation-sign')
        ).add_to(m)

        return HttpResponse(m._repr_html_())
    except Exception as e:
        return HttpResponse(f"<p>Error loading map: {e}</p>")
    
from datetime import timedelta
@login_required
def assign_patrol_ajax(request):
    if request.method == 'POST':
        suggestion_id = request.POST.get('suggestion_id')
        officer_id = request.POST.get('officer_id')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        try:
            suggestion = PatrolSuggestions.objects.get(id=suggestion_id)
            officer = User.objects.get(id=officer_id)

            route = PatrolRoute.objects.create(
            police_station=officer.police_station,
            total_distance=0.0,
            estimated_duration = timedelta(minutes=30),
            start_time=start_time,
            end_time=end_time
        )
            route.covered_locations.add(suggestion.location)

            PatrolAssignment.objects.create(
                patrol_route=route,
                officer=officer,
                status='assigned'
            )

            # Update assigned count
            suggestion.assigned_patrols = (suggestion.assigned_patrols or 0) + 1
            suggestion.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request'})

from .utils.patrol_suggestion_generator import generate_patrol_suggestions

@login_required
def refresh_patrol_suggestions(request):
    if request.method == 'POST':
        result = generate_patrol_suggestions()
        return JsonResponse({'success': True, 'message': result})
    return JsonResponse({'success': False, 'message': 'Invalid method'})

def district_map_view(request):
    return render(request, 'patrols/map.html')


@login_required
def update_case_status(request, case_id):
    case = get_object_or_404(CrimeReport, id=case_id, assigned_to=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        case.status = new_status
        case.save()
        messages.success(request, f"Status for Case {case.id} updated to {case.get_status_display()}.")
    return redirect('officer_dashboard')

#Admin 
from django.views.generic import ListView

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from .models import PoliceStation
from .forms import PoliceStationForm

class StationListView(ListView):
    model = PoliceStation
    template_name = 'policeadmin/stations/stationlist.html'  # Correct path
    context_object_name = 'stations'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context here
        return context

# views.py
from django.http import JsonResponse

def get_station_data(request, station_id):
    station = get_object_or_404(PoliceStation, id=station_id)
    data = {
        'name': station.name,
        'district': station.district,
        'state': station.state,
        'jurisdiction_area': station.jurisdiction_area,
        'ward': station.ward,
        'pincode': station.pincode,
        'contact_number': station.contact_number,
        'email': station.email,
        'latitude': str(station.latitude) if station.latitude else '',
        'longitude': str(station.longitude) if station.longitude else '',
    }
    return JsonResponse(data)

def add_station(request):
    if request.method == 'POST':
        form = PoliceStationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('station_list')
    else:
        form = PoliceStationForm()
    
    return render(request, 'policeadmin/stations/stationform.html', {
        'form': form,
        'stations': PoliceStation.objects.all()
    })

def edit_station(request, station_id):
    station = get_object_or_404(PoliceStation, id=station_id)
    if request.method == 'POST':
        form = PoliceStationForm(request.POST, instance=station)
        if form.is_valid():
            form.save()
            return redirect('station_list')
    else:
        form = PoliceStationForm(instance=station)
    
    return render(request, 'policeadmin/stations/stationform.html', {
        'form': form,
        'stations': PoliceStation.objects.all()
    })

def delete_station(request, station_id):
    station = get_object_or_404(PoliceStation, id=station_id)
    if request.method == 'POST':
        station.delete()
        return redirect('station_list')
    return render(request, 'policeadmin/stations/station_confirm_delete.html', {'station': station})

def officers_by_district(request):
    # Group stations by district with officer counts
    stations_by_district = {}
    stations = PoliceStation.objects.annotate(officer_count=Count('user'))
    
    for station in stations:
        if station.district not in stations_by_district:
            stations_by_district[station.district] = []
        stations_by_district[station.district].append(station)
    
    return render(request, 'policeadmin/officers/officers_by_dist.html', {
        'stations_by_district': stations_by_district
    })

from django.contrib.auth import get_user_model

def officers_by_station(request, station_id):
    User = get_user_model()  # Corrected: call the function
    station = PoliceStation.objects.get(id=station_id)

    # Get all users assigned to this station
    users = User.objects.filter(police_station=station)

    # Get their corresponding police profiles
    officers = PoliceProfile.objects.filter(user_id__in=users).select_related('user')

    return render(request, 'policeadmin/officers/officers_by_station.html', {
        'station': station,
        'officers': officers
    })

# Monthly case trend (last 6 months)
from django.db.models.functions import TruncMonth
def analytics_view(request):
    # Case status counts
    status_counts = CrimeReport.objects.values('status').annotate(total=Count('id'))
    status_data = {item['status']: item['total'] for item in status_counts}

    # Crime type distribution
    type_counts = CrimeReport.objects.values('crime_category__name').annotate(total=Count('id'))
    type_labels = [item['crime_category__name'] for item in type_counts]
    type_data = [item['total'] for item in type_counts]

    

    recent_months = CrimeReport.objects.annotate(month=TruncMonth('date_occurred')) \
        .values('month').annotate(total=Count('id')).order_by('month')
    month_labels = [entry['month'].strftime('%b %Y') for entry in recent_months]
    month_data = [entry['total'] for entry in recent_months]

    monthly_data = CrimeReport.objects.extra(
        select={'month': "DATE_FORMAT(date_occurred, '%%Y-%%m')"}
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    # Extract lists for chart
    months = [entry['month'] for entry in monthly_data]
    counts = [entry['count'] for entry in monthly_data]
    months_query = CrimeReport.objects.extra(
        select={'month': "DATE_FORMAT(date_occurred, '%%Y-%%m')"}
    ).values('month').order_by('month').distinct()

    months = [entry['month'] for entry in months_query]

    # Step 2: Get all crime types
    crime_types = CrimeReport.objects.values_list('crime_category', flat=True).distinct()

    # Step 3: Count per crime_type per month
    crime_data = {}
    
    for crime_type in crime_types:
        counts = []
        for month in months:
            count = CrimeReport.objects.extra(
                select={'month': "DATE_FORMAT(date_occurred, '%%Y-%%m')"}
            ).filter(
                crime_category=crime_type,
                date_occurred__isnull=False
            ).filter(
                date_occurred__startswith=month
            ).count()
            counts.append(count)
        crime_data[crime_type] = counts


    return render(request, 'analytics/dashboard.html', {
        'status_data': status_data,
        'type_labels': type_labels,
        'type_data': type_data,
        'month_labels': month_labels,
        'month_data': month_data,
        'months': months,
        'counts': counts,
        'crime_data': crime_data
    })



from django.shortcuts import render
from .models import CrimeReport
import folium
from folium.plugins import MarkerCluster
from django.utils import timezone
from datetime import timedelta

@login_required
def hotspot_map_view(request):
    recent_days = int(request.GET.get('days', 30))  # default: 30 days
    recent_crimes = CrimeReport.objects.filter(
        date_occurred__gte=timezone.now() - timedelta(days=recent_days)
    )

    # Initialize Map
    base_map = folium.Map(location=[10.0, 76.3], zoom_start=8)

    # Marker Cluster (optional)
    marker_cluster = MarkerCluster().add_to(base_map)

    # Color & weight based on severity
    severity_color = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}
    severity_weight = {'Low': 3, 'Medium': 6, 'High': 9}

    for crime in recent_crimes:
        folium.CircleMarker(
            location=[crime.location.latitude, crime.location.longitude],
            radius=severity_weight.get(crime.severity_level, 12),
            popup=f"{crime.crime_category} at {crime.location.district}  in ward {crime.location.ward}",
            color=severity_color.get(crime.severity_level, 'red'),
            fill=True,
            fill_opacity=0.6
        ).add_to(marker_cluster)

    # Save map as HTML
    map_html = base_map._repr_html_()

    return render(request, 'analytics/hotspots.html', {'map': map_html})

def temporal_analysis(request):
    # Format date as 'YYYY-MM' for MySQL
    monthly_data = CrimeReport.objects.extra(
        select={'month': "DATE_FORMAT(date_occurred, '%%Y-%%m')"}
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    # Extract lists for chart
    months = [entry['month'] for entry in monthly_data]
    counts = [entry['count'] for entry in monthly_data]

    return render(request, 'analytics/temporal.html', {
        'months': months,
        'counts': counts
    })

@login_required
def update_case_status(request, case_id):
    if request.method == 'POST':
        new_status = request.POST.get('status')
        case = get_object_or_404(CrimeReport, id=case_id)

        if new_status in ['reported', 'under_investigation', 'solved']:
            case.status = new_status
            case.save()
            messages.success(request, f"Case {case_id} status updated to {new_status.replace('_', ' ').title()}.")
        else:
            messages.error(request, "Invalid status selected.")

    return redirect(request.META.get('HTTP_REFERER', 'home'))