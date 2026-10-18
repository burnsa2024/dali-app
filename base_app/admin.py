from django.contrib import admin

from .models import PersonRecord, Shelter, VolunteerProfile


@admin.register(Shelter)
class ShelterAdmin(admin.ModelAdmin):
    list_display = ["name", "area", "is_active"]


@admin.register(VolunteerProfile)
class VolunteerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "shelter"]
    list_filter = ["shelter"]


@admin.register(PersonRecord)
class PersonRecordAdmin(admin.ModelAdmin):
    list_display = ["name", "approximate_age", "shelter", "status", "unaccompanied_minor", "created_at"]
    list_filter = ["shelter", "status", "unaccompanied_minor", "visibility", "source"]
    search_fields = ["name", "other_names"]
    readonly_fields = ["unaccompanied_minor", "entered_by", "created_at", "updated_at"]
