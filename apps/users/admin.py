from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["username", "mobile", "email", "is_staff", "is_active"]
    search_fields = ["username", "mobile"]
