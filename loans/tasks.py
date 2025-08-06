# loans/tasks.py
import pandas as pd
from pathlib import Path
from django.conf import settings
from celery import shared_task
from loans.models import Customer, Loan
from django.db import connection

@shared_task
def import_customers_and_loans():
    base = Path(settings.BASE_DIR) / "data"

    # Customers
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

    # Loans
    loan_df = pd.read_excel(base / "loan_data.xlsx")
    Loan.objects.all().delete()
    loans = []
    for _, row in loan_df.iterrows():
        try:
            cust = Customer.objects.get(customer_id=row["Customer ID"])
        except Customer.DoesNotExist:
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

    # Reset sequence for Customer PK
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT setval(
                pg_get_serial_sequence('loans_customer','customer_id'),
                (SELECT MAX(customer_id) FROM loans_customer)
            );
        """)
    return {
        "customers_imported": len(customers),
        "loans_imported": len(loans),
    }
