from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'get_police_station')
    list_filter = ('role', 'police_station')

    def get_police_station(self, obj):
        return obj.police_station.jurisdiction_area if obj.police_station else '-'
    get_police_station.short_description = 'Police Station'

admin.site.register(User, UserAdmin)
admin.site.register(PoliceStation)
admin.site.register(PoliceProfile)
