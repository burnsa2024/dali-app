from django.contrib import admin

from .models import Match, PersonRecord, SearchRequest, Shelter, VolunteerProfile


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


class MatchInline(admin.TabularInline):
    model = Match
    extra = 0
    fields = ["person", "score", "reasons", "status"]
    readonly_fields = ["person", "score", "reasons"]


@admin.register(SearchRequest)
class SearchRequestAdmin(admin.ModelAdmin):
    list_display = ["reference_code", "sought_name", "searcher_name", "status", "created_at"]
    list_filter = ["status", "searcher_shelter"]
    search_fields = ["reference_code", "sought_name", "searcher_name"]
    readonly_fields = ["reference_code", "entered_by", "created_at", "updated_at"]
    inlines = [MatchInline]


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ["search", "person", "score", "status", "created_at"]
    list_filter = ["status", "person__shelter"]
    readonly_fields = ["search", "person", "score", "reasons", "created_at", "updated_at"]