from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg, Min
from django.core.paginator import Paginator
from datetime import date
from dateutil.relativedelta import relativedelta
import json
from django.db.models.functions import TruncMonth
from .models import Lead, Vehicle, VehicleVariant, FollowUp, Quote
from .forms import LeadForm, VehicleForm, VehicleColorFormSet, VehicleVariantFormSet, FollowUpForm, QuoteForm
from django.db.models import Q, Count, Avg, Min
from django.db.models.functions import TruncMonth, ExtractWeekDay
from django.utils import timezone
from datetime import datetime, timedelta
import calendar
import json
import numpy as np
from sklearn.linear_model import LinearRegression
from .forms import (
    LeadForm,
    VehicleForm,
    FollowUpForm,
    QuoteForm,
    VehicleVariantFormSet,
    VehicleColorFormSet
)
# ================= HOME =================

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


# ================= DASHBOARD =================
@login_required
def dashboard(request):

    leads = Lead.objects.all().order_by('-created_at')

    search = request.GET.get('search', '')
    status = request.GET.get('status', '')

    if search:
        leads = leads.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    if status:
        leads = leads.filter(status=status)

    total_leads = Lead.objects.count()

    won_leads = Lead.objects.filter(
        status='Won'
    ).count()

    conversion_rate = round(
        (won_leads / total_leads) * 100,
        1
    ) if total_leads else 0

    avg_score = Lead.objects.aggregate(
        Avg('score')
    )['score__avg'] or 0

    month_data = (
        Lead.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    labels = []
    chart_data = []

    for item in month_data:
        if item['month']:
            labels.append(
                item['month'].strftime('%b %Y')
            )
            chart_data.append(
                item['count']
            )

    paginator = Paginator(leads, 10)

    page_obj = paginator.get_page(
        request.GET.get('page')
    )

    context = {
        'total_leads': total_leads,
        'won_leads': won_leads,
        'conversion_rate': conversion_rate,
        'avg_score': round(avg_score, 1),

        'leads': page_obj,
        'page_obj': page_obj,

        'search': search,
        'selected_status': status,

        'chart_labels': json.dumps(labels),
        'chart_data': json.dumps(chart_data),
    }

    return render(
        request,
        'dashboard.html',
        context
    )
@login_required
def my_leads(request):

    leads = Lead.objects.all().order_by('-created_at')

    search = request.GET.get('search', '')
    status = request.GET.get('status', '')

    if search:
        leads = leads.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    if status:
        leads = leads.filter(status=status)

    paginator = Paginator(leads, 20)

    page_obj = paginator.get_page(
        request.GET.get('page')
    )

    context = {
        'leads': page_obj,
        'page_obj': page_obj,
        'search': search,
        'selected_status': status,
    }

    return render(
        request,
        'mylead.html',
        context
    )
# ================= ADD LEAD =================
@login_required
def select_lead(request, id):
    variant = get_object_or_404(VehicleVariant, id=id)
    vehicle = variant.vehicle

    # Show leads interested in this vehicle first, then others
    leads = Lead.objects.filter(vehicle=vehicle).order_by('-created_at')

    query = request.GET.get('q', '')
    if query:
        leads = Lead.objects.all().filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)  |
            Q(phone__icontains=query)      |
            Q(city__icontains=query)       |
            Q(id__icontains=query)
        )

    return render(request, 'select_lead.html', {
        'variant': variant,
        'vehicle': vehicle,
        'leads': leads,
        'query': query,
    })
@login_required
def add_lead(request):
    vehicle_id = request.GET.get("vehicle")

    if request.method == "POST":
        form = LeadForm(request.POST)

        if form.is_valid():
            lead = form.save(commit=False)

            # optional safety: calculate score
            if hasattr(lead, "calculate_score"):
                lead.score = lead.calculate_score()

            lead.save()
            return redirect("my_leads")

    else:
        # prefill vehicle if coming from vehicle page
        initial_data = {}
        if vehicle_id:
            initial_data["vehicle"] = vehicle_id

        form = LeadForm(initial=initial_data)

    return render(request, "add_lead.html", {"form": form})
# ================= VIEW LEAD =================

@login_required
def view_lead(request, id):
    lead = get_object_or_404(Lead, id=id)
    followups = lead.followups.all().order_by('-created_at')
    quotes = lead.quotes.all().order_by('-created_at')
    return render(request, 'view_lead.html', {
        'lead': lead,
        'followups': followups,
        'quotes': quotes
    })

@login_required
def edit_lead(request, id):
    lead = get_object_or_404(Lead, id=id)
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.score = lead.calculate_score()
            lead.save()
            return redirect('view_lead', id=lead.id)
    else:
        form = LeadForm(instance=lead)
    return render(request, 'edit_lead.html', {'form': form, 'lead': lead})

@login_required
def delete_lead(request, id):
    lead = get_object_or_404(Lead, id=id)
    if request.method == 'POST':
        lead.delete()
        return redirect('my_leads')
    return render(request, 'delete_lead.html', {'lead': lead})

@login_required
def add_followup(request, id):
    lead = get_object_or_404(Lead, id=id)
    if request.method == 'POST':
        form = FollowUpForm(request.POST)
        if form.is_valid():
            followup = form.save(commit=False)
            followup.lead = lead
            followup.save()
            return redirect('view_lead', id=lead.id)
    else:
        form = FollowUpForm()
    return render(request, 'add_followup.html', {'form': form, 'lead': lead})
@login_required
def variant_leads(request, id):
    variant = get_object_or_404(VehicleVariant, id=id)
    vehicle = variant.vehicle
    leads = Lead.objects.filter(vehicle=vehicle).order_by("-created_at")
    
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    if search:
        leads = leads.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(phone__icontains=search)
        )
    if status:
        leads = leads.filter(status=status)

    paginator = Paginator(leads, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'variant_leads.html', {  # ← THIS WAS variant_action.html
        'variant': variant,
        'vehicle': vehicle,
        'leads': page_obj,
        'page_obj': page_obj,
        'search': search,
        'selected_status': status,
        'interested_count': leads.count(),
    })

# ================= VEHICLES =================
@login_required
def vehicle_detail(request, id):
    vehicle = get_object_or_404(Vehicle, id=id)

    leads = Lead.objects.filter(vehicle=vehicle).order_by("-created_at")
    followups = FollowUp.objects.filter(lead__vehicle=vehicle).order_by("-created_at")

    return render(request, "view_vehicle.html", {
        "vehicle": vehicle,
        "leads": leads,
        "followups": followups,
        "interested_count": leads.count(),
    })

@login_required
def vehicles(request):
    vehicles_qs = Vehicle.objects.all()

    search = request.GET.get('search', '')
    selected_fuel = request.GET.get('fuel', '')
    selected_sort = request.GET.get('sort', '')

    if search:
        vehicles_qs = vehicles_qs.filter(name__icontains=search)

    if selected_fuel:
        vehicles_qs = vehicles_qs.filter(fuel_type__icontains=selected_fuel)

    if selected_sort == 'price_asc':
        vehicles_qs = vehicles_qs.order_by('price')
    elif selected_sort == 'price_desc':
        vehicles_qs = vehicles_qs.order_by('-price')
    elif selected_sort == 'name':
        vehicles_qs = vehicles_qs.order_by('name')

    vehicles_qs = vehicles_qs.annotate(interested_count=Count('lead'))

    return render(request, 'vehicles.html', {
        'vehicles': vehicles_qs,
        'search': search,
        'selected_fuel': selected_fuel,
        'selected_sort': selected_sort,
    })


# ================= ADD VEHICLE =================

@login_required
def add_vehicle(request):
    if request.method == 'POST':
        vehicle_form = VehicleForm(request.POST, request.FILES)
        color_formset = VehicleColorFormSet(request.POST, request.FILES, prefix='colors')
        variant_formset = VehicleVariantFormSet(request.POST, prefix='variants')

        if vehicle_form.is_valid() and color_formset.is_valid() and variant_formset.is_valid():
            vehicle = vehicle_form.save()

            color_formset.instance = vehicle
            variant_formset.instance = vehicle

            color_formset.save()
            variant_formset.save()

            return redirect('vehicles')

    else:
        vehicle_form = VehicleForm()
        color_formset = VehicleColorFormSet(prefix='colors')
        variant_formset = VehicleVariantFormSet(prefix='variants')

    return render(request, 'add_vehicle.html', {
        'vehicle_form': vehicle_form,
        'color_formset': color_formset,
        'variant_formset': variant_formset,
    })


# ================= VIEW VEHICLE (ONLY ONE - KEEP THIS) =================

@login_required
def view_vehicle(request, id):
    vehicle = get_object_or_404(Vehicle, id=id)

    leads = Lead.objects.filter(vehicle=vehicle).order_by("-created_at")
    followups = FollowUp.objects.filter(lead__vehicle=vehicle).order_by("-created_at")

    return render(request, "view_vehicle.html", {
        "vehicle": vehicle,
        "leads": leads,
        "followups": followups,
        "interested_count": leads.count(),
    })


# ================= EDIT VEHICLE =================

@login_required
def edit_vehicle(request, id):
    vehicle = get_object_or_404(Vehicle, id=id)

    form = VehicleForm(request.POST or None, request.FILES or None, instance=vehicle)

    color_formset = VehicleColorFormSet(
        request.POST or None,
        request.FILES or None,
        instance=vehicle,
        prefix="colors"
    )

    variant_formset = VehicleVariantFormSet(
        request.POST or None,
        instance=vehicle,
        prefix="variants"
    )

    if request.method == "POST":
        if form.is_valid() and color_formset.is_valid() and variant_formset.is_valid():
            vehicle = form.save()
            color_formset.instance = vehicle
            variant_formset.instance = vehicle
            color_formset.save()
            variant_formset.save()
            return redirect("view_vehicle", id=vehicle.id)

    return render(request, "edit_vehicle.html", {
        "vehicle_form": form,
        "color_formset": color_formset,
        "variant_formset": variant_formset,
        "vehicle": vehicle
    })


# ================= DELETE VEHICLE =================

@login_required
def delete_vehicle(request, id):
    vehicle = get_object_or_404(Vehicle, id=id)

    if request.method == 'POST':
        vehicle.delete()
        return redirect('vehicles')

    return render(request, 'delete_vehicle.html', {
        'vehicle': vehicle
    })

# ================= VIEW QUOTE =================

@login_required
def view_quote(request, id):
    quote = get_object_or_404(Quote, id=id)
    return render(request, 'view_quote.html', {'quote': quote})


# ================= EDIT QUOTE =================

@login_required
def edit_quote(request, id):
    quote = get_object_or_404(Quote, id=id)
    if request.method == 'POST':
        form = QuoteForm(request.POST, instance=quote)
        if form.is_valid():
            form.save()
            return redirect('view_quote', id=quote.id)
    else:
        form = QuoteForm(instance=quote)
    return render(request, 'create_quote.html', {
        'form':    form,
        'quote':   quote,
        'vehicle': quote.vehicle,
        'variant': quote.variant,
        'lead':    quote.lead,
    })


# ================= DELETE QUOTE =================

@login_required
def delete_quote(request, id):
    quote = get_object_or_404(Quote, id=id)
    if request.method == 'POST':
        lead_id = quote.lead.id
        quote.delete()
        return redirect('view_lead', lead_id=lead_id)
    return render(request, 'delete_quote.html', {'quote': quote})


# ================= MARK QUOTE FINAL =================

@login_required
def mark_quote_final(request, id):
    quote = get_object_or_404(Quote, id=id)
    quote.is_final = True
    quote.save()
    return redirect('view_quote', id=quote.id)


# ================= CREATE QUOTE =================

@login_required
def create_quote_variant(request, variant_id, lead_id):
    variant = get_object_or_404(VehicleVariant, id=variant_id)
    vehicle = variant.vehicle
    lead    = get_object_or_404(Lead, id=lead_id)
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            quote         = form.save(commit=False)
            quote.lead    = lead
            quote.vehicle = vehicle
            quote.variant = variant
            quote.save()
            return redirect('view_quote', id=quote.id)
    else:
        form = QuoteForm()
    return render(request, 'create_quote.html', {
        'form':    form,
        'vehicle': vehicle,
        'variant': variant,
        'lead':    lead,
    })

# ================= ANALYTICS =================
@login_required
def analytics(request):
    from django.db.models import Sum

    total_leads = Lead.objects.count()
    won_leads = Lead.objects.filter(status='Won').count()
    lost_leads = Lead.objects.filter(status='Lost').count()
    new_leads = Lead.objects.filter(status='New').count()
    contacted = Lead.objects.filter(status='Contacted').count()
    test_driven = Lead.objects.filter(status='Test_Driven').count()
    test_completed = Lead.objects.filter(status='Test_Completed').count()
    total_vehicles = Vehicle.objects.count()
    total_quotes = Quote.objects.count()

    conversion_rate = round((won_leads / total_leads) * 100, 1) if total_leads else 0

    source_data = (
        Lead.objects.values('source')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Revenue per month from quotes
    revenue_data = (
        Quote.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(revenue=Sum('total_price'))
        .order_by('month')
    )

    # Lead growth last 12 months
    twelve_months_ago = timezone.now() - timedelta(days=365)
    month_data = (
        Lead.objects
        .filter(created_at__gte=twelve_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(
            total=Count('id'),
            won=Count('id', filter=Q(status='Won')),
            lost=Count('id', filter=Q(status='Lost')),
        )
        .order_by('month')
    )

    chart_labels = []
    chart_total = []
    chart_won = []
    chart_lost = []
    for item in month_data:
        if item['month']:
            chart_labels.append(item['month'].strftime('%b %Y'))
            chart_total.append(item['total'])
            chart_won.append(item['won'])
            chart_lost.append(item['lost'])

    revenue_labels = []
    revenue_values = []
    for item in revenue_data:
        if item['month']:
            revenue_labels.append(item['month'].strftime('%b %Y'))
            revenue_values.append(float(item['revenue'] or 0))

    top_vehicles = (
        Lead.objects
        .filter(vehicle__isnull=False, status='Won')
        .values('vehicle__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )

    context = {
        'total_leads': total_leads,
        'won_leads': won_leads,
        'lost_leads': lost_leads,
        'new_leads': new_leads,
        'contacted': contacted,
        'test_driven': test_driven,
        'test_completed': test_completed,
        'conversion_rate': conversion_rate,
        'total_vehicles': total_vehicles,
        'total_quotes': total_quotes,
        'source_data': source_data,
        'top_vehicles': top_vehicles,
        'chart_labels': json.dumps(chart_labels),
        'chart_total': json.dumps(chart_total),
        'chart_won': json.dumps(chart_won),
        'chart_lost': json.dumps(chart_lost),
        'revenue_labels': json.dumps(revenue_labels),
        'revenue_values': json.dumps(revenue_values),
    }

    return render(request, 'analytics.html', context)
# ================= AI PREDICTION =================
@login_required
def ai_prediction(request):
    print("START AI PREDICTION")
    selected_month = request.GET.get("month")

    first_date = Lead.objects.aggregate(
        min_date=Min("created_at")
    )["min_date"]

    if first_date:
        min_month = first_date.strftime("%Y-%m")
        first_month_date = first_date.replace(day=1)
    else:
        min_month = None
        first_month_date = None

    if not selected_month:

        current_date = timezone.now()

        max_month = (
            current_date.replace(day=1)
            + timedelta(days=180)
        ).strftime("%Y-%m")

        return render(
            request,
            "ai_prediction.html",
            {
                "min_month": min_month,
                "max_month": max_month,
            }
        )

    target_year, target_month = map(
        int,
        selected_month.split("-")
    )

    target_date = timezone.make_aware(
        datetime(
            target_year,
            target_month,
            1
        )
    )

    if first_month_date and target_date < first_month_date:
        print("BEFORE FINAL RETURN")
        return render(
            request,
            "ai_prediction.html",
            {
                "no_data": True,
                "message": "Selected month is before available data range.",
                "min_month": min_month,
            }
        )

    today = timezone.now()

    six_months_ago = today - timedelta(days=180)

    recent_stats = (
        Lead.objects
        .filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(
            total=Count("id"),
            won=Count(
                "id",
                filter=Q(status="Won")
            )
        )
        .order_by("month")
    )

    if not recent_stats:

        return render(
            request,
            "ai_prediction.html",
            {
                "no_data": True,
                "message": "No lead data available yet.",
                "min_month": min_month,
            }
        )

    total_leads = sum(
        m["total"]
        for m in recent_stats
    )

    total_won = sum(
        m["won"]
        for m in recent_stats
    )

    base_conversion = (
        total_won / total_leads * 100
    ) if total_leads else 0

    conversion_rate = round(
        base_conversion,
        2
    )

    weekday_map = {
        1: "Sunday",
        2: "Monday",
        3: "Tuesday",
        4: "Wednesday",
        5: "Thursday",
        6: "Friday",
        7: "Saturday",
    }

    weekday_stats = (
        Lead.objects
        .annotate(
            weekday=ExtractWeekDay(
                "created_at"
            )
        )
        .values("weekday")
        .annotate(
            count=Count("id")
        )
        .order_by("-count")
    )

    best_weekday = (
        weekday_map.get(
            weekday_stats[0]["weekday"]
        )
        if weekday_stats
        else "N/A"
    )

    all_stats = (
        Lead.objects
        .annotate(
            month=TruncMonth(
                "created_at"
            )
        )
        .values("month")
        .annotate(
            total=Count("id")
        )
        .order_by("month")
    )

    chart_labels = []
    chart_data = []

    last_month = None
    last_leads = None
    predicted_leads = None

    for item in all_stats:

        chart_labels.append(
            item["month"].strftime(
                "%b %Y"
            )
        )

        chart_data.append(
            item["total"]
        )

        last_month = item["month"]
        last_leads = item["total"]

        if (
            item["month"].year
            == target_year
            and
            item["month"].month
            == target_month
        ):
            predicted_leads = item["total"]

    if last_month is None:

        return render(
            request,
            "ai_prediction.html",
            {
                "no_data": True,
                "message": "Not enough data available.",
            }
        )

    monthly_counts = []

    for item in all_stats:
        monthly_counts.append(item["total"])

    if len(monthly_counts) >= 2:

        X = np.array(range(len(monthly_counts))).reshape(-1, 1)
        y = np.array(monthly_counts)

        model = LinearRegression()
        model.fit(X, y)

        total_months = (
            (target_year - first_month_date.year) * 12
            + (target_month - first_month_date.month)
        )

        predicted_leads = int(
            model.predict([[total_months]])[0]
        )

        predicted_leads = max(predicted_leads, 0)

        future_labels = []
        future_values = []

        for i in range(len(monthly_counts), total_months + 1):

            prediction = int(
                model.predict([[i]])[0]
            )

            prediction = max(prediction, 0)

            forecast_date = (
                first_month_date
                + relativedelta(months=i)
            )

            future_labels.append(
                forecast_date.strftime("%b %Y")
            )

            future_values.append(prediction)

        chart_labels.extend(future_labels)
        chart_data.extend(future_values)

    else:
        predicted_leads = last_leads

    predicted_converted = round(
        predicted_leads * conversion_rate / 100
    )

    top_vehicles = (
        Lead.objects
        .filter(vehicle__isnull=False)
        .values("vehicle__name")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    source_data = (
        Lead.objects
        .values("source")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    return render(
        request,
        "ai_prediction.html",
        {
            "predicted": True,
            "selected_month":
                f"{calendar.month_name[target_month]} {target_year}",

            "predicted_leads": predicted_leads,
            "conversion_rate": conversion_rate,
            "predicted_converted": predicted_converted,
            "best_weekday": best_weekday,
            "top_vehicles": top_vehicles,
            "source_data": source_data,
            "chart_labels": json.dumps(chart_labels),
            "chart_data": json.dumps(chart_data),
            "min_month": min_month,
        }
    )
# ================= LOGIN =================

def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user     = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            error = 'Invalid username or password'
    return render(request, 'login.html', {'error': error})


# ================= REGISTER =================

def register_view(request):
    error = None
    if request.method == 'POST':
        username         = request.POST.get('username')
        password         = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            error = 'Passwords do not match'
            return render(request, 'register.html', {'error': error})

        if User.objects.filter(username=username).exists():
            error = 'Username already exists'
            return render(request, 'register.html', {'error': error})

        User.objects.create_user(username=username, password=password)
        return redirect('login')

    return render(request, 'register.html')


# ================= LOGOUT =================

def logout_view(request):
    logout(request)
    return redirect('login')
@login_required
def ai_lead_summary(request, lead_id):

    lead = get_object_or_404(
        Lead,
        id=lead_id
    )

    summary = f"""
    Customer: {lead.first_name} {lead.last_name}

    Interested Vehicle:
    {lead.vehicle.name if lead.vehicle else 'Not Selected'}

    Source:
    {lead.source}

    Priority:
    {lead.priority}

    Status:
    {lead.status}

    Recommendation:
    Follow up within 3 days.
    """

    return render(
        request,
        "ai_summary.html",
        {
            "lead": lead,
            "summary": summary
        }
    )
def get_ai_recommendation(lead):

    recommendations = []

    if lead.priority == "High":
        recommendations.append(
            "Call within 24 hours"
        )

    if lead.status == "Contacted":
        recommendations.append(
            "Schedule Test Drive"
        )

    if lead.status == "Test_Driven":
        recommendations.append(
            "Send Quotation"
        )

    if lead.source == "Referral":
        recommendations.append(
            "Offer referral benefits"
        )

    if not recommendations:
        recommendations.append(
            "Perform regular follow-up"
        )

    return "\n".join(recommendations)
@login_required
def ai_recommendation(request, lead_id):

    lead = get_object_or_404(
        Lead,
        id=lead_id
    )

    recommendations = []

    if lead.priority == "High":
        recommendations.append(
            "Call customer within 24 hours."
        )

    if lead.status == "Contacted":
        recommendations.append(
            "Schedule a test drive."
        )

    if lead.status == "Test_Driven":
        recommendations.append(
            "Send quotation immediately."
        )

    if lead.source == "Referral":
        recommendations.append(
            "Offer referral bonus."
        )

    if not recommendations:
        recommendations.append(
            "Perform regular follow-up."
        )

    return render(
        request,
        "ai_recommendation.html",
        {
            "lead": lead,
            "recommendations": recommendations
        }
    )