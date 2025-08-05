import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from loans.models import Customer, Loan

class Command(BaseCommand):
    help = "Import customers and loans from Excel"

    def handle(self, *args, **options):
        base = Path(settings.BASE_DIR) / "data"

        # — Import customers
        cust_df = pd.read_excel(base / "customer_data.xlsx")
        Customer.objects.all().delete()
        customers = [
            Customer(
                customer_id    = row["Customer ID"],
                first_name     = row["First Name"],
                last_name      = row["Last Name"],
                age            = row["Age"],
                phone_number   = str(row["Phone Number"]),
                monthly_salary = row["Monthly Salary"],
                approved_limit = row["Approved Limit"],
                
            )
            for _, row in cust_df.iterrows()
        ]
        Customer.objects.bulk_create(customers)
        self.stdout.write(self.style.SUCCESS(f"Imported {len(customers)} customers"))


        loan_df = pd.read_excel(base / "loan_data.xlsx")
        Loan.objects.all().delete()
        loans = []
        for _, row in loan_df.iterrows():
            try:
                cust = Customer.objects.get(customer_id=row["Customer ID"])
            except Customer.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"Skipping loan {row['Loan ID']}: customer {row['Customer ID']} not found"
                ))
                continue

            loans.append(Loan(
                customer           = cust,
                loan_id            = row["Loan ID"],
                loan_amount        = row["Loan Amount"],
                tenure             = row["Tenure"],
                interest_rate      = row["Interest Rate"],
                monthly_payment    = row["Monthly payment"],
                emis_paid_on_time  = row["EMIs paid on Time"],
                date_of_approval   = row["Date of Approval"],
                end_date           = row["End Date"],
            ))
        Loan.objects.bulk_create(loans)
        self.stdout.write(self.style.SUCCESS(f"Imported {len(loans)} loans"))
