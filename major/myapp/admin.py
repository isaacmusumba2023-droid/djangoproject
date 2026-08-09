from django.contrib import admin
from .models import EmployeeLeavePlan


@admin.register(EmployeeLeavePlan)
class EmployeeLeavePlanAdmin(admin.ModelAdmin):
    list_display = ('employee_name', 'designation', 'project', 'department', 'days_remaining', 'service_years')
    search_fields = ('employee_name', 'employee_id', 'oracle_id', 'civil_id_no', 'passport_no')
    list_filter = ('project', 'department', 'nationality')

#=========================================================================
from django.contrib import admin
from .models import WorkOrderReconciliation

@admin.register(WorkOrderReconciliation)
class WorkOrderReconciliationAdmin(admin.ModelAdmin):
    # Columns to display in the admin list view
    list_display = (
        'crm_wo_number',
        'service_book_serial_no',
        'customer_or_site',
        'service_type',
        'technician_name',
        'reconciliation_status',
        'service_date'
    )

    # Filters on the right sidebar
    list_filter = ('reconciliation_status', 'service_type', 'service_date')

    # Search bar fields (enables quick lookup by WO number, paper serial, or tech)
    search_fields = (
        'crm_wo_number',
        'service_book_serial_no',
        'customer_or_site',
        'technician_name',
        'equipment_asset_id'
    )

    # Organize field layout inside the edit form
    fieldsets = (
        ('Dynamics CRM Information', {
            'fields': ('crm_wo_number', 'customer_or_site', 'equipment_asset_id', 'crm_planned_parts')
        }),
        ('Physical Service Book Slip Details', {
            'fields': ('service_book_serial_no', 'technician_name', 'service_type', 'actual_parts_used', 'service_date')
        }),
        ('Matching & Audit Status', {
            'fields': ('reconciliation_status', 'discrepancy_notes')
        }),
    )

from django.contrib import admin

# Register your models here.
