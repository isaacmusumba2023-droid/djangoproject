
#THIS  THE view.py from major
#=======================================================================================================

from django.db.models import Sum, Avg, Count
from .models import Asset, EmployeeLeavePlan
from django.core.paginator import Paginator
import csv
from django.http import HttpResponse, JsonResponse
#==========================================================================================================
#speed transfer
#==========================================================================================================
def generators(request):
    # ... (POST handling remains the same) ...

    # Fetch only 25 assets per page instead of the entire table
    asset_list = Asset.objects.all().order_by('-id')
    paginator = Paginator(asset_list, 25)
    page_number = request.GET.get('page', 1)
    assets = paginator.get_page(page_number)

    context = {
        'assets': assets,
        # ... dropdown lists ...
    }
    return render_module(request, 'Generators Registry', 'Manage generator assets.', 'generators', context)

assets = Asset.objects.only(
    'id', 'g_code', 'serial_number', 'model', 'type',
    'running_hrs', 'kva', 'from_location', 'to_location',
    'field', 'user', 'service_technician', 'supervisor'
).order_by('-id')[:25]


#==========================================================================================================
def clean_int(val):
    if val is None or str(val).strip() == '':
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None

def clean_float(val):
    if val is None or str(val).strip() == '':
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

def clean_str(val):
    if val is None or str(val).strip() == '':
        return None
    return str(val).strip()


def render_module(request, title, description, active_module, extra_context=None):
    """
    Universal renderer:
    - AJAX call (sidebar click) -> Renders ONLY the inner fragment to prevent nesting.
    - Standard GET (page load / refresh) -> Renders full home.html.
    """
    module_templates = {
        'overview': 'myapp/partials/overview_content.html',
        'generators': 'myapp/partials/generators_content.html',
    }

    partial_template = module_templates.get(active_module, 'myapp/partials/generic_module.html')

    context = {
        'title': title,
        'content': description,
        'active_module': active_module,
        'partial_template': partial_template,
    }

    if extra_context:
        context.update(extra_context)

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if is_ajax:
        return render(request, partial_template, context)

    return render(request, 'myapp/home.html', context)


# -----------------------------------------------------------------------------
# 1. EXEC & OPS VIEWS
# -----------------------------------------------------------------------------
def overview(request):
    total_units = Asset.objects.count() if hasattr(Asset, 'objects') else 0
    workshop_units = Asset.objects.filter(to_location__icontains='workshop').count() if hasattr(Asset, 'objects') else 0

    total_capacity = Asset.objects.aggregate(Sum('kva'))['kva__sum'] or 0 if hasattr(Asset, 'objects') else 0
    avg_running_hrs = round(Asset.objects.aggregate(Avg('running_hrs'))['running_hrs__avg'] or 0, 1) if hasattr(Asset, 'objects') else 0

    field_counts = {}
    user_counts = {}
    recent_assets = []

    if hasattr(Asset, 'objects'):
        for item in Asset.objects.values('field').annotate(total=Count('id')):
            if item['field']:
                field_counts[item['field']] = item['total']

        for item in Asset.objects.values('user').annotate(total=Count('id')):
            if item['user']:
                user_counts[item['user']] = item['total']

        recent_assets = Asset.objects.all().order_by('-id')[:5]

    context = {
        'total_units': total_units,
        'workshop_units': workshop_units,
        'total_capacity': total_capacity,
        'avg_running_hrs': avg_running_hrs,
        'field_counts': field_counts,
        'user_counts': user_counts,
        'recent_assets': recent_assets,
    }

    return render_module(
        request,
        'Executive Overview',
        'High-level operational overview.',
        active_module='overview',
        extra_context=context
    )


def gis_map(request):
    return render_module(request, '🗺️ GIS Map Operations',
                         'Geographic Information System tracking for active fleet units.', 'gis_map')


def dispatch(request):
    return render_module(request, '🚨 Active Dispatch Log',
                         'Real-time asset dispatching and emergency movement tracking.', 'dispatch')


# -----------------------------------------------------------------------------
# 2. FLEET MANAGEMENT VIEWS
# -----------------------------------------------------------------------------
def generators(request):
    # =========================================================================
    # 1. HANDLE POST REQUESTS (ADD, EDIT, DELETE)
    # =========================================================================
    if request.method == 'POST':

        # --- A. DELETE ASSET ---
        if request.POST.get('delete_asset') == '1' or 'delete_id' in request.POST:
            asset_id = request.POST.get('asset_id') or request.POST.get('delete_id')
            if asset_id:
                Asset.objects.filter(id=asset_id).delete()
            return redirect('generators')

        # --- B. ADD NEW ASSET ---
        elif request.POST.get('add_asset') == '1':
            Asset.objects.create(
                g_code=request.POST.get('g_code'),
                serial_number=request.POST.get('serial_number'),
                model=clean_str(request.POST.get('model')),
                type=clean_str(request.POST.get('type')),
                running_hrs=clean_float(request.POST.get('running_hrs')),
                kva=clean_float(request.POST.get('kva')),
                year_of_manufacture=clean_int(request.POST.get('year_of_manufacture')),
                service_yr_in_koc=clean_int(request.POST.get('service_yr_in_koc')),
                from_location=clean_str(request.POST.get('from_location')),
                to_location=clean_str(request.POST.get('to_location')),
                field=clean_str(request.POST.get('field')),
                user=clean_str(request.POST.get('user')),
                movement_date=clean_str(request.POST.get('movement_date')),
                purpose=clean_str(request.POST.get('purpose')),
                service_technician=clean_str(request.POST.get('service_technician')),
                supervisor=clean_str(request.POST.get('supervisor')),
                reason_comment=clean_str(request.POST.get('reason_comment')),
            )
            return redirect('generators')

        # --- C. UPDATE EXISTING ASSET ---
        elif request.POST.get('update_asset') == '1':
            asset_id = request.POST.get('asset_id')
            if asset_id:
                Asset.objects.filter(id=asset_id).update(
                    g_code=request.POST.get('g_code'),
                    serial_number=request.POST.get('serial_number'),
                    model=clean_str(request.POST.get('model')),
                    type=clean_str(request.POST.get('type')),
                    running_hrs=clean_float(request.POST.get('running_hrs')),
                    kva=clean_float(request.POST.get('kva')),
                    year_of_manufacture=clean_int(request.POST.get('year_of_manufacture')),
                    service_yr_in_koc=clean_int(request.POST.get('service_yr_in_koc')),
                    from_location=clean_str(request.POST.get('from_location')),
                    to_location=clean_str(request.POST.get('to_location')),
                    field=clean_str(request.POST.get('field')),
                    user=clean_str(request.POST.get('user')),
                    movement_date=clean_str(request.POST.get('movement_date')),
                    purpose=clean_str(request.POST.get('purpose')),
                    service_technician=clean_str(request.POST.get('service_technician')),
                    supervisor=clean_str(request.POST.get('supervisor')),
                    reason_comment=clean_str(request.POST.get('reason_comment')),
                )
            return redirect('generators')

    # =========================================================================
    # 2. HANDLE GET REQUESTS
    # =========================================================================
    assets = Asset.objects.all().order_by('-id')

    context = {
        'assets': assets,
        'models': ['C15', 'CAT', 'Perkins', 'Cummins', 'Volvo'],
        'types': ['CAT', 'VOLVO'],
        'fields': ['Burgan', 'NORTH', 'WEST', 'WORKSHOP', 'WAFURA', 'SEK'],
        'users': ['ESP-KOC', 'MOBILE', 'WORKSHOP', 'OFF-HIRE', 'NEW-GENERATOR', 'FIELD OP.REPAIR'],
        'technicians': ['John Doe', 'Alex Smith', 'Mohammed Ali', 'Isaac Musumba'],
        'supervisors': ['MURAD', 'MANIKANTH', 'TERRAK'],
    }

    return render_module(
        request,
        'Generators Data',
        'Manage generator assets and movement logs.',
        active_module='generators',
        extra_context=context
    )

#=====================================================================================================================

def diagnostics(request):
    return render_module(request, '📈 Diagnostics & Health', 'Generator run-hours, telemetry logs, and mechanical health assessments.', 'diagnostics')

def well_sites(request):
    return render_module(request, '🛢️ Well Sites Allocation', 'Active deployment points and site-specific power operational logs.', 'well_sites')

def disposal(request):
    return render_module(request, '🗑️ Decommissioning & Disposal', 'Retired assets, scrap logs, and off-hire processing archives.', 'disposal')

def trips(request):
    return render_module(request, '🚨 Trip Logs & Transport', 'Transport movement records, driver logs, and logistics tracking.', 'trips')


# -----------------------------------------------------------------------------
# 3. MAINTENANCE VIEWS
# -----------------------------------------------------------------------------
from .models import WorkOrderReconciliation


def work_orders_view(request):
    reconciliations = WorkOrderReconciliation.objects.all().order_by('-created_at')

    # KPI Counters
    total_records = reconciliations.count()
    matched_count = reconciliations.filter(reconciliation_status='MATCHED').count()
    pending_count = reconciliations.filter(reconciliation_status='PENDING_PAPER').count()
    discrepancy_count = reconciliations.filter(reconciliation_status='DISCREPANCY').count()

    context = {
        'reconciliations': reconciliations,
        'total_records': total_records,
        'matched_count': matched_count,
        'pending_count': pending_count,
        'discrepancy_count': discrepancy_count,
        'active_module': 'work_orders',  # Ensures home.html knows which tab is active
    }

    # If requested via AJAX (sidebar click using loadTab)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'myapp/partials/work_orders_content.html', context)

    # If loaded directly via browser URL refresh
    return render(request, 'myapp/home.html', context)


def add_work_order(request):
    if request.method == "POST":
        try:
            WorkOrderReconciliation.objects.create(
                crm_wo_number=request.POST.get('crm_wo_number'),
                customer_or_site=request.POST.get('customer_or_site'),
                equipment_asset_id=request.POST.get('equipment_asset_id'),
                crm_planned_parts=request.POST.get('crm_planned_parts'),
                service_book_serial_no=request.POST.get('service_book_serial_no'),
                technician_name=request.POST.get('technician_name'),
                service_type=request.POST.get('service_type'),
                actual_parts_used=request.POST.get('actual_parts_used'),
                service_date=request.POST.get('service_date') or None,
                reconciliation_status=request.POST.get('reconciliation_status'),
                discrepancy_notes=request.POST.get('discrepancy_notes'),
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'errors': str(e)})


def edit_work_order(request, pk):
    item = get_object_or_404(WorkOrderReconciliation, pk=pk)
    if request.method == "POST":
        try:
            item.crm_wo_number = request.POST.get('crm_wo_number')
            item.customer_or_site = request.POST.get('customer_or_site')
            item.equipment_asset_id = request.POST.get('equipment_asset_id')
            item.crm_planned_parts = request.POST.get('crm_planned_parts')
            item.service_book_serial_no = request.POST.get('service_book_serial_no')
            item.technician_name = request.POST.get('technician_name')
            item.service_type = request.POST.get('service_type')
            item.actual_parts_used = request.POST.get('actual_parts_used')
            item.service_date = request.POST.get('service_date') or None
            item.reconciliation_status = request.POST.get('reconciliation_status')
            item.discrepancy_notes = request.POST.get('discrepancy_notes')
            item.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'errors': str(e)})


def delete_work_order(request, pk):
    if request.method == "POST":
        item = get_object_or_404(WorkOrderReconciliation, pk=pk)
        item.delete()
        return JsonResponse({'status': 'success'})
#=================================================================================================================
#PM SERVICE SCHEDULING
#===================================================================================================================
def pm_schedule_view(request):
    generators = Asset.objects.all().order_by('g_code')
    recent_logs = GeneratorPMServiceLog.objects.select_related('generator').order_by('-service_date')[:50]
    warehouse_parts = WarehousePart.objects.filter(quantity__gt=0)

    # 1. Automated Work Order Creation for Overdue Assets
    for g in generators:
        if g.next_service_info['status'] == 'OVERDUE':
            # Create OPEN ticket if one doesn't already exist for this generator
            WorkOrder.objects.get_or_create(
                generator=g,
                status='OPEN',
                defaults={
                    'title': f"Overdue Maintenance: {g.next_service_info['type']}",
                    'service_type': g.next_service_info['type'],
                    'notes': f"System generated ticket. Asset is overdue by {abs(g.next_service_info['days_left'])} days."
                }
            )

    chart_data = [
        {
            'g_code': g.g_code,
            'days_left': g.next_service_info['days_left'],
            'service_type': g.next_service_info['type']
        }
        for g in generators
    ]

    context = {
        'generators': generators,
        'recent_logs': recent_logs,
        'warehouse_parts': warehouse_parts,
        'chart_data_json': json.dumps(chart_data),
        'active_module': 'pm_schedule'
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'myapp/partials/pm_schedule_content.html', context)

    return render(request, 'myapp/home.html', context)

def export_pm_schedule_csv(request):
    """Generates a downloadable CSV report of the current PM Schedule."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="PM_Schedule_{timezone.now().date()}.csv"'

    writer = csv.writer(response)
    # Write CSV Header
    writer.writerow(['G-Code', 'Model', 'Current Running Hrs', 'Cycle Start Date', 'Next Service', 'Days Remaining', 'Status'])

    # Write Generator Data Rows
    generators = Asset.objects.all().order_by('g_code')
    for g in generators:
        writer.writerow([
            g.g_code,
            g.model or '-',
            f"{g.running_hrs} hrs",
            g.cycle_start_date,
            g.next_service_info['type'],
            f"{g.next_service_info['days_left']} Days",
            g.next_service_info['status']
        ])

    return response

def log_pm_service(request, generator_id):
    generator = get_object_or_404(Asset, id=generator_id)

    if request.method == 'POST':
        try:
            new_hrs = int(request.POST.get('running_hrs_at_service', 0))
        except ValueError:
            new_hrs = generator.running_hrs

        # Enforce running hours validation (must not be less than current)
        if new_hrs < generator.running_hrs:
            messages.error(request,
                           f"Error: Running hours ({new_hrs}) cannot be less than current hours ({generator.running_hrs}).")
            return redirect('pm_schedule')

        service_type = request.POST.get('service_type')
        service_date_str = request.POST.get('service_date')

        # 1. Update generator baseline
        generator.running_hrs = new_hrs

        # If Service B is completed (or cycle reset requested), restart 90-day cycle
        if service_type == 'Service B' or request.POST.get('reset_cycle') == 'true':
            generator.cycle_start_date = timezone.now().date()

        generator.save()

        # 2. Save Service Log
        GeneratorPMServiceLog.objects.create(
            generator=generator,
            service_type=service_type,
            service_date=service_date_str or timezone.now().date(),
            running_hrs_at_service=new_hrs,
            technician=request.POST.get('technician', ''),
            work_order_number=request.POST.get('work_order_number', ''),
            notes=request.POST.get('notes', '')
        )

        messages.success(request, f"PM Service logged for {generator.g_code}. Running hours updated to {new_hrs}.")

    return redirect('pm_schedule')
#----------------------------------------------------------------------------------------------------------------------
def load_tests(request):
    return render_module(request, '⚡ Load Tests', 'Capacity testing certificates and generator performance reports.', 'load_tests')

def activity_planner(request):
    return render_module(request, '📚 Activity Planner', 'Project milestones, site installation tasks, and field schedules.', 'activity_planner')

def qa_qc(request):
    return render_module(request, '✅ QA / QC Standards', 'Quality assurance sign-offs and maintenance inspection reports.', 'qa_qc')


# -----------------------------------------------------------------------------
# 4. SUPPLY CHAIN VIEWS
# -----------------------------------------------------------------------------

def warehouse_parts_list(request):
    if request.method == 'POST':
        WarehousePart.objects.create(
            part_name=request.POST.get('part_name'),
            part_number=request.POST.get('part_number'),
            model=request.POST.get('model'),
            supplier=request.POST.get('supplier'),
            location=request.POST.get('location'),
            compatibility_asset=request.POST.get('compatibility_asset'),
            quantity=request.POST.get('quantity') or 0,
            date_received=request.POST.get('date_received'),
            description=request.POST.get('description', '')
        )
        messages.success(request, "Warehouse part added successfully!")
        return redirect('warehouse_parts')

    parts = WarehousePart.objects.all()
    # Fetch recent issue logs (newest first)
    issue_logs = PartIssueLog.objects.select_related('part').order_by('-issue_date')[:50]

    context = {
        'parts': parts,
        'issue_logs': issue_logs,
        'active_module': 'warehouse_parts'
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'myapp/partials/warehouse_content.html', context)

    return render(request, 'myapp/home.html', context)


def edit_warehouse_part(request, part_id):
    part = get_object_or_404(WarehousePart, id=part_id)
    if request.method == 'POST':
        part.part_name = request.POST.get('part_name')
        part.part_number = request.POST.get('part_number')
        part.model = request.POST.get('model')
        part.supplier = request.POST.get('supplier')
        part.location = request.POST.get('location')
        part.compatibility_asset = request.POST.get('compatibility_asset')
        part.quantity = request.POST.get('quantity') or 0
        part.date_received = request.POST.get('date_received')
        part.description = request.POST.get('description', '')
        part.save()
        messages.success(request, "Warehouse part updated successfully!")

    return redirect('warehouse_parts')


def delete_warehouse_part(request, part_id):
    part = get_object_or_404(WarehousePart, id=part_id)
    if request.method == 'POST':
        part.delete()
        messages.success(request, "Warehouse part deleted successfully!")

    return redirect('warehouse_parts')# Updated redirect name


def issue_warehouse_part(request, part_id):
    part = get_object_or_404(WarehousePart, id=part_id)

    if request.method == 'POST':
        try:
            issue_qty = int(request.POST.get('issue_quantity', 0))
        except ValueError:
            issue_qty = 0

        destination = request.POST.get('destination', '').strip()
        notes = request.POST.get('notes', '').strip()

        if issue_qty <= 0:
            messages.error(request, "Please enter a valid quantity to issue.")
        elif issue_qty > part.quantity:
            messages.error(request, f"Insufficient stock! Only {part.quantity} available.")
        else:
            # 1. Deduct Stock
            part.quantity -= issue_qty
            part.save()

            # 2. Record Transaction
            PartIssueLog.objects.create(
                part=part,
                issued_quantity=issue_qty,
                destination=destination,
                notes=notes
            )

            messages.success(request, f"Issued {issue_qty} units of {part.part_name} to {destination}.")

    return redirect('warehouse_parts')
def delete_issue_log(request, log_id):
    log = get_object_or_404(PartIssueLog, id=log_id)
    if request.method == 'POST':
        log.delete()
        messages.success(request, "Issue log record deleted successfully!")
    return redirect('warehouse_parts')
#=======================================================================================================================
def van_stock(request):
    return render_module(request, '🚐 Van Stock', 'Field technician mobile inventory tracking.', 'van_stock')

def purchase_orders(request):
    return render_module(request, '🛒 Purchase Orders', 'Spare parts procurement and supplier request logs.', 'purchase_orders')

def tool_calibrations(request):
    return render_module(request, '🛠️ Tool Calibrations', 'Testing equipment calibration records and validity dates.', 'tool_calibrations')


# -----------------------------------------------------------------------------
# 5. COMMERCIAL VIEWS
# -----------------------------------------------------------------------------
def contracts(request):
    return render_module(request, '📝 Field Contracts', 'Rental agreements, client contracts, and asset lease terms.', 'contracts')

def invoicing(request):
    return render_module(request, '💰 Invoicing & Billing', 'Operational billing statements and rental charge records.', 'invoicing')


# -----------------------------------------------------------------------------
# 6. ANALYTICS & HSE VIEWS
# -----------------------------------------------------------------------------
def reliability_rcm(request):
    return render_module(request, '📉 Reliability RCM', 'Reliability-Centered Maintenance metrics and MTBF failure analysis.', 'reliability_rcm')

def fuel_logistics(request):
    return render_module(request, '⛽ Fuel Logistics', 'Diesel consumption tracking, refuel logs, and site tank levels.', 'fuel_logistics')

def hse_safety(request):
    return render_module(request, '🦺 HSE & Safety', 'Safety compliance, incident reports, and environmental hazard logs.', 'hse_safety')


# ------------------------------------------------------------------------------
# 7. ADMIN & HR VIEWS
# -----------------------------------------------------------------------------
def roles_access(request):
    return render_module(request, '🔐 Roles & Access Control', 'User permissions and system role management.', 'roles_access')
#-----------------------------------------------------------------------------------------------
from django.shortcuts import render
from django.http import JsonResponse
from .models import EmployeeLeavePlan
from .forms import EmployeeLeavePlanForm

def leave_plans_view(request):
    leave_plans = EmployeeLeavePlan.objects.all().order_by('-id') # Or whatever your model name is
    context = {
        'leave_plans': leave_plans,
        'active_module': 'leave_plans',
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'myapp/partials/leave_plans_content.html', context)
    return render(request, 'myapp/home.html', context)
def add_employee_leave(request):
    """Handle new employee creation via form submit."""
    if request.method == 'POST':
        form = EmployeeLeavePlanForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Employee added successfully!'})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
from django.shortcuts import get_object_or_404

def edit_employee_leave(request, pk):
    """Update an existing employee leave record."""
    employee = get_object_or_404(EmployeeLeavePlan, pk=pk)
    if request.method == 'POST':
        form = EmployeeLeavePlanForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Employee updated successfully!'})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


def delete_employee_leave(request, pk):
    """Delete an employee leave record."""
    if request.method == 'POST':
        employee = get_object_or_404(EmployeeLeavePlan, pk=pk)
        employee.delete()
        return JsonResponse({'status': 'success', 'message': 'Employee deleted successfully!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

#----------------------------------------------------------------------------------------------------
#======================================================================================================
#RESIDENT CARD FORMS
#======================================================================================================
from django.http import JsonResponse
from .models import ResidentCard
from .forms import ResidentCardForm

def resident_cards_view(request):
    """List view with metric counts for Resident Cards."""
    cards = ResidentCard.objects.all()
    today = timezone.now().date()

    # Calculate top metric counters
    total_active = cards.filter(status='ACTIVE').count()
    expiring_30 = 0
    expired_count = 0

    for card in cards:
        if card.days_remaining is not None:
            if 0 <= card.days_remaining <= 30:
                expiring_30 += 1
            elif card.days_remaining < 0:
                expired_count += 1

    form = ResidentCardForm()

    context = {
        'cards': cards,
        'form': form,
        'active_module': 'resident_cards',
        'total_active': total_active,
        'expiring_30': expiring_30,
        'expired_count': expired_count,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'myapp/partials/resident_cards_content.html', context)

    return render(request, 'myapp/home.html', context)


def add_resident_card(request):
    if request.method == 'POST':
        form = ResidentCardForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Card record saved!'})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method.'}, status=405)


def edit_resident_card(request, pk):
    card = get_object_or_404(ResidentCard, pk=pk)
    if request.method == 'POST':
        form = ResidentCardForm(request.POST, request.FILES, instance=card)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Card updated!'})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method.'}, status=405)


def delete_resident_card(request, pk):
    if request.method == 'POST':
        card = get_object_or_404(ResidentCard, pk=pk)
        card.delete()
        return JsonResponse({'status': 'success', 'message': 'Card deleted!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid method.'}, status=405)


#-------------------------------------------------------------------------------------------------------
def medical_fitness(request):
    return render_module(request, '🏥 Medical Fitness Records', 'Operational field crew fitness certifications.', 'medical_fitness')

def safety_training(request):
    return render_module(request, '🎓 Safety Training Logs', 'HSE course completions and technical certification tracking.', 'safety_training')

def master_data(request):
    return render_module(request, '📚 Master Data Management', 'System lookup tables, location codes, and asset category master listings.', 'master_data')

def audit_logs(request):
    return render_module(request, '🛡️ Audit Logs', 'System security audit trails and change history records.', 'audit_logs')

#===============================================END==============================================================
#LOGIC LINK GENERATOR WORKORDERS AND PM SERVICE
#=================================================================================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
import json

# Import Asset instead of Generator
from .models import Asset, GeneratorPMServiceLog, WarehousePart, PartIssueLog, WorkOrder


def pm_schedule_view(request):
    # Fetch assets from your generator_assets table
    generators = Asset.objects.all().order_by('g_code')
    recent_logs = GeneratorPMServiceLog.objects.select_related('generator').order_by('-service_date')[:50]
    warehouse_parts = WarehousePart.objects.filter(quantity__gt=0)

    chart_data = [
        {
            'g_code': g.g_code,
            'days_left': g.next_service_info['days_left'],
            'service_type': g.next_service_info['type']
        }
        for g in generators
    ]

    context = {
        'generators': generators,
        'recent_logs': recent_logs,
        'warehouse_parts': warehouse_parts,
        'chart_data_json': json.dumps(chart_data),
        'active_module': 'pm_schedule'
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'myapp/partials/pm_schedule_content.html', context)

    return render(request, 'myapp/home.html', context)


def log_pm_service(request, generator_id):
    # Target Asset model
    generator = get_object_or_404(Asset, id=generator_id)

    if request.method == 'POST':
        try:
            new_hrs = float(request.POST.get('running_hrs_at_service', 0.0))
        except ValueError:
            new_hrs = generator.running_hrs

        if new_hrs < generator.running_hrs:
            messages.error(request, f"Running hours ({new_hrs}) cannot be less than current ({generator.running_hrs}).")
            return redirect('pm_schedule')

        service_type = request.POST.get('service_type')
        service_date = request.POST.get('service_date') or timezone.now().date()
        part_id = request.POST.get('part_id')

        try:
            part_qty = int(request.POST.get('part_qty', 1))
        except ValueError:
            part_qty = 1

        # Deduct Warehouse Inventory
        if part_id:
            part = get_object_or_404(WarehousePart, id=part_id)
            if part.quantity >= part_qty:
                part.quantity -= part_qty
                part.save()

                PartIssueLog.objects.create(
                    part=part,
                    issued_quantity=part_qty,
                    destination=f"PM Service ({generator.g_code})",
                    notes=f"Used during {service_type} on {service_date}"
                )
            else:
                messages.error(request, f"Insufficient stock for {part.part_name}. Only {part.quantity} remaining.")
                return redirect('pm_schedule')

        # Update Generator baseline hours & reset cycle for Service B
        generator.running_hrs = new_hrs
        if service_type == 'Service B':
            generator.cycle_start_date = timezone.now().date()
        generator.save()

        # Log PM History Record
        GeneratorPMServiceLog.objects.create(
            generator=generator,
            service_type=service_type,
            service_date=service_date,
            running_hrs_at_service=new_hrs,
            technician=request.POST.get('technician', ''),
            work_order_number=request.POST.get('work_order_number', ''),
        )

        # Resolve Open Work Orders
        WorkOrder.objects.filter(generator=generator, status='OPEN').update(status='RESOLVED')

        messages.success(request, f"PM Service logged for {generator.g_code}.")

    return redirect('pm_schedule')
#============================================================================================================
from django.shortcuts import render, redirect
from .models import GeneratorDiagnostics
from .forms import GeneratorDiagnosticsForm


def diagnostics_view(request):
    logs = GeneratorDiagnostics.objects.all().order_by('-timestamp')
    if request.method == 'POST':
        form = GeneratorDiagnosticsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('diagnostics')
    else:
        form = GeneratorDiagnosticsForm()

    context = {
        'logs': logs,
        'form': form,
    }
    return render(request, 'myapp/diagnostics.html', context)