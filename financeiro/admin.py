from django.contrib import admin
from .models import Plan, FinancialEnrollment, MonthlyFee


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'active']
    filter_horizontal = ['modalities']


@admin.register(FinancialEnrollment)
class FinancialEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'plan', 'start_date', 'active']
    list_filter = ['active', 'plan']
    search_fields = ['student__name']


@admin.register(MonthlyFee)
class MonthlyFeeAdmin(admin.ModelAdmin):
    list_display = ['student', 'reference_month', 'net_amount', 'status', 'due_date', 'payment_date']
    list_filter = ['status', 'payment_method']
    search_fields = ['student__name']
    date_hierarchy = 'due_date'
    list_editable = ['status']
