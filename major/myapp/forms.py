from django import forms
from .models import EmployeeLeavePlan

class EmployeeLeavePlanForm(forms.ModelForm):
    class Meta:
        model = EmployeeLeavePlan
        fields = [
            'employee_name', 'employee_id', 'oracle_id', 'designation',
            'nationality', 'company_mobile_no', 'project', 'department',
            'joining_date', 'civil_id_no', 'civil_id_expire_date',
            'passport_no', 'passport_expire_date', 'planned_leave_date', 'photo'
        ]
        widgets = {
            'civil_id_expire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'passport_expire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'planned_leave_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'joining_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

#================================================================================================================
from django import forms
from .models import ResidentCard

class ResidentCardForm(forms.ModelForm):
    class Meta:
        model = ResidentCard
        fields = [
            'employee_name', 'employee_id', 'civil_id_no', 'nationality',
            'designation_on_card', 'project_sponsor', 'card_serial_no',
            'issue_date', 'expire_date', 'status', 'card_document', 'renewal_notes'
        ]
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'expire_date': forms.DateInput(attrs={'type': 'date'}),
            'renewal_notes': forms.Textarea(attrs={'rows': 2}),
        }

#=================================================================================================================
# Inside major/myapp/forms.py
from django import forms
from .models import GeneratorDiagnostics, GeneratorAsset  # <-- Import GeneratorAsset here

class GeneratorDiagnosticsForm(forms.ModelForm):
    class Meta:
        model = GeneratorDiagnostics
        fields = [
            'generator', 'is_running', 'last_command',
            'oil_pressure', 'coolant_temp', 'battery_voltage', 'fuel_level',
            'fault_code', 'description', 'severity',
            'symptoms', 'root_cause', 'corrective_action', 'technician', 'resolved'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'symptoms': forms.Textarea(attrs={'rows': 2}),
            'root_cause': forms.Textarea(attrs={'rows': 2}),
            'corrective_action': forms.Textarea(attrs={'rows': 2}),
        }