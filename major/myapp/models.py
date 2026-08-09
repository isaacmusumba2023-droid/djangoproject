from django.db import models
from django.utils import timezone
from datetime import date


# ===============================================================================================================
# FLEET ASSETS & PM SCHEDULING (SUPABASE MATCHED)
# ===============================================================================================================

class Asset(models.Model):
    g_code = models.CharField(max_length=50, unique=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)
    running_hrs = models.FloatField(default=0.0)
    kva = models.IntegerField(default=0)
    year_of_manufacture = models.IntegerField(blank=True, null=True)
    service_yr_in_koc = models.IntegerField(blank=True, null=True)
    from_location = models.CharField(max_length=100, blank=True, null=True)
    to_location = models.CharField(max_length=100, blank=True, null=True)
    field = models.CharField(max_length=100, blank=True, null=True)
    user = models.CharField(max_length=100, blank=True, null=True)
    movement_date = models.DateField(blank=True, null=True)
    purpose = models.CharField(max_length=255, blank=True, null=True)
    service_technician = models.CharField(max_length=100, blank=True, null=True)
    supervisor = models.CharField(max_length=100, blank=True, null=True)
    reason_comment = models.TextField(blank=True, null=True)

    # Baseline date for calculating the 90-day PM cycle
    cycle_start_date = models.DateField(default=date.today, blank=True, null=True)

    def __str__(self):
        return f"{self.g_code} - {self.model}"

    @property
    def days_elapsed(self):
        start = self.cycle_start_date or date.today()
        return (date.today() - start).days % 90

    @property
    def next_service_info(self):
        elapsed = self.days_elapsed
        next_a = 14 - (elapsed % 14)
        next_b = 90 - elapsed

        if next_b <= 0 or elapsed == 0:
            return {'type': 'Service B', 'days_left': 90, 'status': 'DUE'}

        if next_b <= next_a:
            status = 'OVERDUE' if next_b < 0 else ('DUE SOON' if next_b <= 3 else 'OK')
            return {'type': 'Service B', 'days_left': next_b, 'status': status}
        else:
            status = 'OVERDUE' if next_a < 0 else ('DUE SOON' if next_a <= 2 else 'OK')
            return {'type': 'Service A', 'days_left': next_a, 'status': status}

    class Meta:
        db_table = 'generator_assets'
        managed = False


class GeneratorPMServiceLog(models.Model):
    generator = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='pm_logs')
    service_type = models.CharField(max_length=50)
    service_date = models.DateField(default=date.today)
    running_hrs_at_service = models.FloatField()
    technician = models.CharField(max_length=100, blank=True)
    work_order_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)


# ===============================================================================================================
# WAREHOUSE & INVENTORY MANAGEMENT
# ===============================================================================================================

class WarehousePart(models.Model):
    part_name = models.CharField(max_length=150)
    part_number = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    supplier = models.CharField(max_length=150)
    location = models.CharField(max_length=100, help_text="Shelf, bin, or aisle location")
    model = models.CharField(max_length=100)
    compatibility_asset = models.CharField(max_length=150, help_text="Compatible generator or equipment")
    quantity = models.PositiveIntegerField(default=0)
    date_received = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Warehouse Part'
        verbose_name_plural = 'Warehouse Parts'

    def __str__(self):
        return f"{self.part_name} ({self.part_number}) - Qty: {self.quantity}"


class PartIssueLog(models.Model):
    part = models.ForeignKey(WarehousePart, on_delete=models.CASCADE, related_name='issue_logs')
    issued_quantity = models.IntegerField()
    destination = models.CharField(max_length=100)  # Location or G-Code
    issued_by = models.CharField(max_length=100, blank=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)


# ===============================================================================================================
# WORK ORDERS & TICKETING
# ===============================================================================================================

class WorkOrder(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
    ]

    generator = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='work_orders')
    title = models.CharField(max_length=200)
    service_type = models.CharField(max_length=50, blank=True)  # e.g. Service A / Service B
    supervisor = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateField(default=date.today)
    resolved_at = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"WO-{self.id} | {self.generator.g_code} - {self.status}"

#===============================================================
#ADMIN $ HR
#===============================================================
from datetime import date
from django.db import models


class EmployeeLeavePlan(models.Model):
    # Your existing fields...
    employee_name = models.CharField(max_length=255)
    employee_id = models.CharField(max_length=100, unique=True)
    oracle_id = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=255)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    company_mobile_no = models.CharField(max_length=50, blank=True, null=True)
    project = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    joining_date = models.DateField(null=True, blank=True)
    civil_id_no = models.CharField(max_length=100, blank=True, null=True)
    civil_id_expire_date = models.DateField(null=True, blank=True)
    passport_no = models.CharField(max_length=100, blank=True, null=True)
    passport_expire_date = models.DateField(null=True, blank=True)
    planned_leave_date = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='employee_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def days_remaining(self):
        """Calculates days remaining from today until the planned leave date."""
        if self.planned_leave_date:
            delta = self.planned_leave_date - date.today()
            return delta.days if delta.days >= 0 else 0
        return 0

    @property
    def service_years(self):
        """Calculates total years of service from joining date to today."""
        if self.joining_date:
            today = date.today()
            # Calculate difference in years, accounting for whether their anniversary has occurred this year
            years = today.year - self.joining_date.year
            if (today.month, today.day) < (self.joining_date.month, self.joining_date.day):
                years -= 1

            # For fractional/decimal years (e.g., 3.5 years), calculate exact days fraction
            delta = today - self.joining_date
            return round(delta.days / 365.25, 1) if delta.days >= 0 else 0.0
        return 0.0

#======================================================================================================================
#RESIDENT ID
#======================================================================================================================
class ResidentCard(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active / Valid'),
        ('IN_PROGRESS', 'Renewal in Progress'),
        ('EXPIRING_SOON', 'Expiring Soon'),
        ('EXPIRED', 'Expired'),
    ]

    employee_name = models.CharField(max_length=150)
    employee_id = models.CharField(max_length=50)
    civil_id_no = models.CharField(max_length=50, unique=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    designation_on_card = models.CharField(max_length=150)
    project_sponsor = models.CharField(max_length=150, blank=True, null=True)
    card_serial_no = models.CharField(max_length=100, blank=True, null=True)

    issue_date = models.DateField(blank=True, null=True)
    expire_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')

    card_document = models.FileField(upload_to='resident_cards/', blank=True, null=True)
    renewal_notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['expire_date']

    def __str__(self):
        return f"{self.employee_name} - {self.civil_id_no}"

    @property
    def days_remaining(self):
        if self.expire_date:
            today = timezone.now().date()
            return (self.expire_date - today).days
        return None
#====================================================================================================
#workorder matching
#====================================================================================================
from django.db import models

class WorkOrderReconciliation(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('PREVENTATIVE', 'Preventative Maintenance'),
        ('CORRECTIVE', 'Corrective / Breakdown Repair'),
        ('INSPECTION', 'Inspection & Testing'),
        ('OVERHAUL', 'Major Overhaul'),
        ('PART_REPLACEMENT', 'Service Parts Replacement'),
    ]

    MATCH_STATUS_CHOICES = [
        ('MATCHED', 'Fully Matched'),
        ('PENDING_PAPER', 'Pending Paper Slip'),
        ('DISCREPANCY', 'Parts / Scope Discrepancy'),
    ]

    # Dynamics CRM Info
    crm_wo_number = models.CharField(max_length=100, unique=True, help_text="Work Order ID from Dynamics CRM")
    customer_or_site = models.CharField(max_length=150, help_text="Client Name or Site Location")
    equipment_asset_id = models.CharField(max_length=100, blank=True, null=True, help_text="Generator / Asset ID")
    crm_planned_parts = models.TextField(blank=True, null=True, help_text="Parts scope specified in Dynamics")

    # Service Book (Paper Slip) Info
    service_book_serial_no = models.CharField(max_length=100, blank=True, null=True, help_text="Serial number from physical paper book page")
    technician_name = models.CharField(max_length=150, blank=True, null=True)
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES, default='PREVENTATIVE')
    actual_parts_used = models.TextField(blank=True, null=True, help_text="Actual parts written on the paper slip")
    service_date = models.DateField(blank=True, null=True)

    # Reconciliation Status & Notes
    reconciliation_status = models.CharField(max_length=30, choices=MATCH_STATUS_CHOICES, default='PENDING_PAPER')
    discrepancy_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.crm_wo_number} | Book SN: {self.service_book_serial_no or 'N/A'}"