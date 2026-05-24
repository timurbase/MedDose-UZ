from django.contrib import admin
from .models import Drug, Calculation


@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ['name', 'generic_name', 'category', 'k_default', 'ka_default', 'ke_default', 'mic', 'mtc']
    list_filter = ['category']
    search_fields = ['name', 'generic_name']


@admin.register(Calculation)
class CalculationAdmin(admin.ModelAdmin):
    list_display = ['drug_name', 'patient_weight', 'patient_age', 'dose', 'route', 'model_type', 'risk_status', 'created_at']
    list_filter = ['route', 'model_type', 'risk_status']
    search_fields = ['drug_name']
    readonly_fields = ['created_at']
