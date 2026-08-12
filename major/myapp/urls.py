from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    # 1. ROOT PATH & OVERVIEW (Fixes the 404 on http://127.0.0.1:8000/)
    path('', views.overview, name='overview'),
    path('overview/', views.overview, name='overview'),

    # Exec & Ops
    path('gis-map/', views.gis_map, name='gis_map'),
    path('dispatch/', views.dispatch, name='dispatch'),

    # Fleet Management
    path('generators/', views.generators, name='generators'),
    path('diagnostics/', views.diagnostics_view, name='diagnostics'),
    path('well-sites/', views.well_sites, name='well_sites'),
    path('disposal/', views.disposal, name='disposal'),
    path('trips/', views.trips, name='trips'),

    # Maintenance
    #----------------------------------------------------------------------------------------------------------
    #workorders
    # ... your existing paths ...
    path('work-orders/', views.work_orders_view, name='work_orders'),
    path('work-orders/add/', views.add_work_order, name='add_work_order'),
    path('work-orders/edit/<int:pk>/', views.edit_work_order, name='edit_work_order'),
    path('work-orders/delete/<int:pk>/', views.delete_work_order, name='delete_work_order'),

    #================================================================================================================
    #PM-SERVICE
    #===============================================================================================================
    path('pm-schedule/', views.pm_schedule_view, name='pm_schedule'),
    path('pm-schedule/log/<int:generator_id>/', views.log_pm_service, name='log_pm_service'),
    path('pm-schedule/export/', views.export_pm_schedule_csv, name='export_pm_schedule'),


    #===============================================================================================================
    path('load-tests/', views.load_tests, name='load_tests'),
    path('activity-planner/', views.activity_planner, name='activity_planner'),
    path('qa-qc/', views.qa_qc, name='qa_qc'),

    # Supply Chain
    #=================================================================================================================
    #WAREHOUSE
    #=================================================================================================================
    path('warehouse-parts/', views.warehouse_parts_list, name='warehouse_parts'),
    path('warehouse-parts/edit/<int:part_id>/', views.edit_warehouse_part, name='edit_warehouse_part'),
    path('warehouse-parts/delete/<int:part_id>/', views.delete_warehouse_part, name='delete_warehouse_part'),
    path('warehouse-parts/issue/<int:part_id>/', views.issue_warehouse_part, name='issue_warehouse_part'),
    path('warehouse-parts/issue-log/delete/<int:log_id>/', views.delete_issue_log, name='delete_issue_log'),
    #=================================================================================================================
    path('van-stock/', views.van_stock, name='van_stock'),
    path('purchase-orders/', views.purchase_orders, name='purchase_orders'),
    path('tool-calibrations/', views.tool_calibrations, name='tool_calibrations'),

    # Commercial
    path('contracts/', views.contracts, name='contracts'),
    path('invoicing/', views.invoicing, name='invoicing'),

    # Analytics & HSE
    path('reliability-rcm/', views.reliability_rcm, name='reliability_rcm'),
    path('fuel-logistics/', views.fuel_logistics, name='fuel_logistics'),
    path('hse-safety/', views.hse_safety, name='hse_safety'),

    # Admin & HR
    path('roles-access/', views.roles_access, name='roles_access'),
    #==============================================================================================================
    #leave plans
    #=============================================================================================================
    path('leave-plans/', views.leave_plans_view, name='leave_plans'),
    path('leave-plans/add/', views.add_employee_leave, name='add_employee_leave'),
    path('leave-plans/edit/<int:pk>/', views.edit_employee_leave, name='edit_employee_leave'),
    path('leave-plans/delete/<int:pk>/', views.delete_employee_leave, name='delete_employee_leave'),
    #---------------------------------------------------------------------------------------------------------------
    #==============================================================================================
    path('resident-cards/', views.resident_cards_view, name='resident_cards'),
    path('resident-cards/add/', views.add_resident_card, name='add_resident_card'),
    path('resident-cards/edit/<int:pk>/', views.edit_resident_card, name='edit_resident_card'),
    path('resident-cards/delete/<int:pk>/', views.delete_resident_card, name='delete_resident_card'),

    #-----------------------------------------------------------------------------------------------------------
    path('medical-fitness/', views.medical_fitness, name='medical_fitness'),
    path('safety-training/', views.safety_training, name='safety_training'),
    path('master-data/', views.master_data, name='master_data'),
    path('audit-logs/', views.audit_logs, name='audit_logs'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)