from django.urls import path
from . import views

urlpatterns = [

    # ================= AUTH =================
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # ================= DASHBOARD =================
    path('dashboard/', views.dashboard, name='dashboard'),

    # ================= LEADS =================
    path('my-leads/', views.my_leads, name='my_leads'),
    path('add-lead/', views.add_lead, name='add_lead'),
    path('lead/<int:id>/', views.view_lead, name='view_lead'),
    path('lead/<int:id>/edit/', views.edit_lead, name='edit_lead'),
    path('lead/<int:id>/delete/', views.delete_lead, name='delete_lead'),
    path('lead/<int:id>/followup/', views.add_followup, name='add_followup'),
    path(
    "lead/<int:lead_id>/summary/",
    views.ai_lead_summary,
    name="ai_lead_summary"
),path(
    "lead/<int:lead_id>/recommendation/",
    views.ai_recommendation,
    name="ai_recommendation"
),
    # ================= VARIANTS =================

    path('variant/<int:id>/leads/', views.variant_leads, name='variant_leads'),
    path('variant/<int:id>/select-lead/', views.select_lead, name='select_lead'),
    path('variant/<int:variant_id>/lead/<int:lead_id>/quote/', views.create_quote_variant, name='create_quote_variant'),

    # ================= VEHICLES =================
    path('vehicles/', views.vehicles, name='vehicles'),
    path('vehicles/add/', views.add_vehicle, name='add_vehicle'),
    path('vehicles/<int:id>/', views.vehicle_detail, name='vehicle_detail'),
    path('vehicles/<int:id>/edit/', views.edit_vehicle, name='edit_vehicle'),
    path('vehicles/<int:id>/delete/', views.delete_vehicle, name='delete_vehicle'),
    path('vehicles/<int:id>/view/', views.view_vehicle, name='view_vehicle'),

    # ================= QUOTES =================
    path('quotes/<int:id>/', views.view_quote, name='view_quote'),
    path('quotes/<int:id>/edit/', views.edit_quote, name='edit_quote'),
    path('quotes/<int:id>/delete/', views.delete_quote, name='delete_quote'),
    path('quotes/<int:id>/mark-final/', views.mark_quote_final, name='mark_quote_final'),

    # ================= AI + ANALYTICS =================
    path('ai-prediction/', views.ai_prediction, name='ai_prediction'),
    path('analytics/', views.analytics, name='analytics'),
]