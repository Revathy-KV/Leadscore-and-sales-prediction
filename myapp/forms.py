from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.models import User

from .models import (
    Lead,
    Vehicle,
    VehicleColor,
    VehicleVariant,
    FollowUp,
    Quote
)

FIELD_STYLE = {
    'class': 'form-control',
    'style': '''
    width:100%;
    padding:13px 14px;
    border-radius:14px;
    border:1px solid rgba(255,255,255,.08);
    background:rgba(255,255,255,.05);
    color:white;
    font-size:14px;
    outline:none;
    '''
}

SELECT_STYLE = {
    'class': 'form-control',
    'style': '''
    width:100%;
    padding:13px 14px;
    border-radius:14px;
    border:1px solid rgba(255,255,255,.08);
    background:#1f2937;
    color:white;
    font-size:14px;
    outline:none;
    '''
}


# ================= LEAD FORM =================
class LeadForm(forms.ModelForm):

    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        empty_label="-- Select --",
        widget=forms.Select(attrs=SELECT_STYLE)
    )

    class Meta:
        model = Lead

        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'city',
            'address',
            'job_title',
            'annual_income',
            'current_vehicle_owner',
            'current_vehicle_name',
            'current_vehicle_year',
            'current_vehicle_price',
            'vehicle',
            'source',
            'status',
            'priority',
            'follow_up_date',
            'assigned_to',
        ]

        widgets = {
            'first_name': forms.TextInput(attrs=FIELD_STYLE),
            'last_name': forms.TextInput(attrs=FIELD_STYLE),
            'email': forms.EmailInput(attrs=FIELD_STYLE),
            'phone': forms.TextInput(attrs=FIELD_STYLE),
            'city': forms.TextInput(attrs=FIELD_STYLE),
            'address': forms.Textarea(attrs={**FIELD_STYLE, 'rows': 3}),
            'job_title': forms.TextInput(attrs=FIELD_STYLE),
            'annual_income': forms.NumberInput(attrs=FIELD_STYLE),
            'current_vehicle_name': forms.TextInput(attrs=FIELD_STYLE),
            'current_vehicle_year': forms.NumberInput(attrs=FIELD_STYLE),
            'current_vehicle_price': forms.NumberInput(attrs=FIELD_STYLE),
            'vehicle': forms.Select(attrs=SELECT_STYLE),
            'source': forms.Select(attrs=SELECT_STYLE),
            'status': forms.Select(attrs=SELECT_STYLE),
            'priority': forms.Select(attrs=SELECT_STYLE),
            'follow_up_date': forms.DateInput(
                attrs={**FIELD_STYLE, 'type': 'date'}
            ),
        }

# ================= VEHICLE FORM =================

class VehicleForm(forms.ModelForm):

    class Meta:
        model = Vehicle
        fields = [
            'name',
            'fuel_type',
            'max_capacity',
            'power_figures',
            'price',
            'photo',
        ]
        widgets = {                          # ← now INSIDE Meta
            'name':          forms.TextInput(attrs=FIELD_STYLE),
            'fuel_type':     forms.TextInput(attrs=FIELD_STYLE),
            'max_capacity':  forms.NumberInput(attrs=FIELD_STYLE),
            'power_figures': forms.TextInput(attrs=FIELD_STYLE),
            'price':         forms.NumberInput(attrs=FIELD_STYLE),
        }


# ================= FOLLOWUP FORM =================

class FollowUpForm(forms.ModelForm):

    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.Select(attrs=SELECT_STYLE)
    )

    class Meta:
        model = FollowUp
        fields = [
            'task_title',
            'description',
            'due_date',
            'priority',
            'assigned_to',
        ]
        widgets = {
            'task_title':  forms.TextInput(attrs={**FIELD_STYLE, 'placeholder': 'Task Title'}),
            'description': forms.Textarea(attrs={**FIELD_STYLE, 'rows': 4}),
            'due_date':    forms.DateInput(attrs={**FIELD_STYLE, 'type': 'date'}),
            'priority':    forms.Select(attrs=SELECT_STYLE),
        }


# ================= QUOTE FORM =================

class QuoteForm(forms.ModelForm):

    class Meta:
        model = Quote
        fields = [
            'registration_charge',
            'insurance',
            'road_tax',
            'accessories',
            'dealer_discount',
            'exchange_bonus',
            'festival_discount',
        ]
        widgets = {
            'registration_charge': forms.NumberInput(attrs=FIELD_STYLE),
            'insurance':           forms.NumberInput(attrs=FIELD_STYLE),
            'road_tax':            forms.NumberInput(attrs=FIELD_STYLE),
            'accessories':         forms.NumberInput(attrs=FIELD_STYLE),
            'dealer_discount':     forms.NumberInput(attrs=FIELD_STYLE),
            'exchange_bonus':      forms.NumberInput(attrs=FIELD_STYLE),
            'festival_discount':   forms.NumberInput(attrs=FIELD_STYLE),
        }


# ================= FORMSETS =================

TRANSMISSION_CHOICES = [
    ('Manual', 'Manual'),
    ('Automatic', 'Automatic'),
    ('AMT', 'AMT'),
    ('CVT', 'CVT'),
    ('DCT', 'DCT'),
]

FUEL_CHOICES = [
    ('Petrol', 'Petrol'),
    ('Diesel', 'Diesel'),
    ('CNG', 'CNG'),
    ('Hybrid', 'Hybrid'),
    ('Electric', 'Electric'),
]
VehicleVariantFormSet = inlineformset_factory(
    Vehicle,
    VehicleVariant,
    fields=['name', 'fuel_type', 'transmission', 'ex_showroom_price'],
    widgets={
        'name': forms.TextInput(attrs=FIELD_STYLE),
        'fuel_type': forms.Select(choices=FUEL_CHOICES, attrs=SELECT_STYLE),
        'transmission': forms.Select(choices=TRANSMISSION_CHOICES, attrs=SELECT_STYLE),
        'ex_showroom_price': forms.NumberInput(attrs=FIELD_STYLE),
    },
    extra=1,
    can_delete=True
)

VehicleColorFormSet = inlineformset_factory(
    Vehicle,
    VehicleColor,
    fields=['color_name', 'color_code', 'photo'],
    widgets={
        'color_name': forms.TextInput(attrs=FIELD_STYLE),
        'color_code': forms.TextInput(attrs={**FIELD_STYLE, 'placeholder': '#ffffff'}),
    },
    extra=1,
    can_delete=True
)
