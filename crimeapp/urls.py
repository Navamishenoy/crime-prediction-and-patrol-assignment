from django.urls import path,include
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.user_login, name='login'),  
    path('logout/', views.user_logout, name='logout'),
    path('', views.home, name='admin_dashboard'),
    path('', views.home, name='police_dashboard'),
    path('cases/', views.case_list, name='case_list'),
    path('case/<str:id>/', views.case_detail, name='case_detail'),
    path('cases/add/', views.create_crime_report, name='case_add'),
    path('cases/<str:pk>/assign/', views.assign_officer, name='assign_officer'),
    path('cases/<str:case_id>/unassign/', views.unassign_officer, name='unassign_officer'),
    path('cases/<str:case_id>/status/',views.case_status_update,name='status_update'),
    path('cases/<str:case_id>/update-status/', views.update_case_status, name='update_case_status'),

    path('patrols/',views.patrol_assign,name='patrol_assign'),
    path('map/patrol-suggestions/', views.district_map_view, name='district_map'),
    path('assign-patrol/', views.assign_patrol_ajax, name='assign_patrol_ajax'),
    path('refresh-suggestions/', views.refresh_patrol_suggestions, name='refresh_patrol_suggestions'),
    path('crime-map/<int:crime_id>/', views.crime_map_modal, name='crime_map_modal'),

    path('update-case-status/<str:case_id>/', views.update_case_status, name='update_case_status'),

    #admin
    path('stations/', views.StationListView.as_view(), name='station_list'),
    path('stations/add/', views.add_station, name='add_station'),
    path('stations/edit/<str:station_id>/', views.edit_station, name='edit_station'),
    path('stations/delete/<str:station_id>/', views.delete_station, name='delete_station'),
    path('stations/get/<str:station_id>/', views.get_station_data, name='get_station_data'),
    path('officers/', views.officers_by_district, name='officers_by_district'),
    path('officers/station/<str:station_id>/', views.officers_by_station, name='officers_by_station'),
    path('analytics/', views.analytics_view, name='analytics_dashboard'),
    # Data Processing
    
    path('analytics/hotspot-map/', views.hotspot_map_view, name='hotspot_map'),
    path('analytics/temporal/', views.temporal_analysis, name='temporal_analysis'),



    
      
]
