import csv
import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "lead_project.settings"
)

django.setup()

from myapp.models import Lead

with open("leads_5000.csv", newline="", encoding="utf-8") as file:

    reader = csv.DictReader(file)

    count = 0

    for row in reader:

        lead = Lead(
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            phone=row["phone"],
            city=row["city"],
            address=row["address"],
            job_title=row["job_title"],
            annual_income=int(row["annual_income"]) if row["annual_income"] else None,
            current_vehicle_owner=row["current_vehicle_owner"] == "True",
            current_vehicle_name=row["current_vehicle_name"],
            current_vehicle_year=int(row["current_vehicle_year"]) if row["current_vehicle_year"] else None,
            current_vehicle_price=int(row["current_vehicle_price"]) if row["current_vehicle_price"] else None,
            source=row["source"],
            status=row["status"],
            priority=row["priority"]
        )

        # Calculate score
        lead.score = lead.calculate_score()

        lead.save()

        count += 1

print(f"{count} leads imported successfully")