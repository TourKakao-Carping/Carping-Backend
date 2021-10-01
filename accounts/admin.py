from django.contrib import admin

from .models import User, Profile, Certification, EcoLevel, SmsHistory, Search
from django.contrib import admin
from rest_framework_simplejwt.token_blacklist.admin import OutstandingTokenAdmin
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken


class CustomOutstandingTokenAdmin(OutstandingTokenAdmin):
    def has_delete_permission(self, *args, **kwargs):
        return True


admin.site.unregister(OutstandingToken)
# admin.site.register(OutstandingToken, CustomOutstandingTokenAdmin)
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Certification)
admin.site.register(EcoLevel)
admin.site.register(SmsHistory)
admin.site.register(Search)
