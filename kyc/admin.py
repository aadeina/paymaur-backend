from django.contrib import admin
from .models import SimpleKYC, PopulationRecord

@admin.register(SimpleKYC)
class SimpleKYCAdmin(admin.ModelAdmin):
    list_display = ("user", "nni", "status", "verified_at")
    search_fields = ("nni", "user__username", "user__phone")
    list_filter = ("status", "source")

@admin.register(PopulationRecord)
class PopulationRecordAdmin(admin.ModelAdmin):
    list_display = ("nni", "full_name")
    search_fields = ("nni", "full_name")
