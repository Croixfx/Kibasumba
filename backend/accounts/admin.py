from django.contrib import admin

from .models import CustomUser, OTPCode

admin.site.register(CustomUser)
admin.site.register(OTPCode)
