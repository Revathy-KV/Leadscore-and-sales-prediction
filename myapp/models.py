from django.db import models
from django.contrib.auth.models import User


# ================= VEHICLE =================
class Vehicle(models.Model):
    name = models.CharField(max_length=100)
    fuel_type = models.CharField(max_length=50)
    max_capacity = models.IntegerField(default=0)
    power_figures = models.CharField(max_length=100)
    price = models.IntegerField()
    photo = models.ImageField(upload_to="vehicles/", blank=True, null=True)

    def __str__(self):
        return self.name


# ================= VEHICLE COLOR =================
class VehicleColor(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="colors")
    color_name = models.CharField(max_length=100)
    color_code = models.CharField(max_length=20, blank=True, null=True)
    photo = models.ImageField(upload_to="vehicle_colors/", blank=True, null=True)

    def __str__(self):
        return self.color_name


# ================= VEHICLE VARIANT =================
class VehicleVariant(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=100)
    fuel_type = models.CharField(max_length=50)
    transmission = models.CharField(max_length=50)
    ex_showroom_price = models.IntegerField()

    def __str__(self):
        return self.name


# ================= LEAD =================
class Lead(models.Model):

    STATUS_CHOICES = (
        ('New', 'New'),
        ('Contacted', 'Contacted'),
        ('Test_Driven', 'Test Driven'),
        ('Test_Completed', 'Test Completed'),
        ('Won', 'Won'),
        ('Lost', 'Lost'),
    )

    PRIORITY_CHOICES = (
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    )

    SOURCE_CHOICES = (
        ('Website', 'Website'),
        ('Referral', 'Referral'),
        ('Walk-in', 'Walk-in'),
        ('Social Media', 'Social Media'),
        ('Phone', 'Phone'),
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100)

    address = models.TextField(blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)

    annual_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )

    current_vehicle_owner = models.BooleanField(default=False)

    current_vehicle_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    current_vehicle_year = models.IntegerField(
        blank=True,
        null=True
    )

    current_vehicle_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    variant = models.ForeignKey(
        VehicleVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    source = models.CharField(
        max_length=50,
        choices=SOURCE_CHOICES,
        default='Website'
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='New'
    )

    priority = models.CharField(
        max_length=50,
        choices=PRIORITY_CHOICES,
        default='Medium'
    )

    follow_up_date = models.DateField(blank=True, null=True)

    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    ai_recommendation = models.TextField(
    blank=True,
    null=True
)
    def calculate_score(self):
        score = 0

        source_scores = {
            'Referral': 20,
            'Walk-in': 15,
            'Website': 10,
            'Phone': 8,
            'Social Media': 5
        }

        priority_scores = {
            'High': 25,
            'Medium': 15,
            'Low': 5
        }

        score += source_scores.get(self.source, 0)
        score += priority_scores.get(self.priority, 0)

        if self.vehicle:
            score += 25

        if self.follow_up_date:
            score += 20

        return score

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# ================= FOLLOWUP =================
class FollowUp(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="followups")
    task_title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField()
    priority = models.CharField(max_length=20, default="Medium")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.task_title


# ================= QUOTE =================
class Quote(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="quotes")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    variant = models.ForeignKey(VehicleVariant, on_delete=models.CASCADE)

    registration_charge = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    insurance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    road_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    accessories = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    dealer_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    exchange_bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    festival_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    is_final = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_price = (
            self.variant.ex_showroom_price +
            self.registration_charge +
            self.insurance +
            self.road_tax +
            self.accessories -
            self.dealer_discount -
            self.exchange_bonus -
            self.festival_discount
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Quote #{self.id}"


class TestDrive(models.Model):
    lead = models.ForeignKey("Lead", on_delete=models.CASCADE)
    vehicle = models.ForeignKey("Vehicle", on_delete=models.SET_NULL, null=True, blank=True)

    scheduled_date = models.DateTimeField()
    is_completed = models.BooleanField(default=False)

    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lead} - {self.vehicle}"
    