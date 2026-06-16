from django.contrib import admin
from .models import (
    Lead,
    Vehicle,
    VehicleColor,
    VehicleVariant,
    FollowUp,
    Quote
)


# ================= VEHICLE INLINES =================

class VehicleColorInline(admin.TabularInline):
    model = VehicleColor
    extra = 1


class VehicleVariantInline(admin.TabularInline):
    model = VehicleVariant
    extra = 1


# ================= VEHICLE ADMIN =================

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'fuel_type',
        'price',
        'max_capacity'
    )

    search_fields = (
        'name',
        'fuel_type'
    )

    inlines = [
        VehicleColorInline,
        VehicleVariantInline
    ]


# ================= LEAD ADMIN =================

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):

    list_display = (
        'first_name',
        'last_name',
        'email',
        'phone',
        'status',
        'priority',
        'score',
        'created_at'
    )

    list_filter = (
        'status',
        'priority',
        'source'
    )

    search_fields = (
        'first_name',
        'last_name',
        'email',
        'phone'
    )

    ordering = (
        '-created_at',
    )


# ================= FOLLOW UP ADMIN =================

@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):

    list_display = (
        'task_title',
        'lead',
        'due_date',
        'priority',
        'assigned_to',
        'completed'
    )

    list_filter = (
        'priority',
        'completed'
    )

    search_fields = (
        'task_title',
        'lead__first_name',
        'lead__last_name'
    )


# ================= QUOTE ADMIN =================

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'lead',
        'vehicle',
        'variant',
        'total_price',
        'is_final',
        'created_at'
    )

    list_filter = (
        'is_final',
        'created_at'
    )

    search_fields = (
        'lead__first_name',
        'lead__last_name',
        'vehicle__name',
        'variant__name'
    )


# ================= VEHICLE COLOR ADMIN =================

@admin.register(VehicleColor)
class VehicleColorAdmin(admin.ModelAdmin):

    list_display = (
        'color_name',
        'vehicle',
        'color_code'
    )


# ================= VEHICLE VARIANT ADMIN =================

@admin.register(VehicleVariant)
class VehicleVariantAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'vehicle',
        'fuel_type',
        'transmission',
        'ex_showroom_price'
    )