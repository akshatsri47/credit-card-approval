from django.db import models

class Customer(models.Model):
    customer_id    = models.AutoField(primary_key=True)       
    first_name     = models.CharField(max_length=100)
    last_name      = models.CharField(max_length=100)
    age            = models.IntegerField()
    phone_number   = models.CharField(max_length=15)
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2)
    approved_limit = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Loan(models.Model):
    customer           = models.ForeignKey(
                             Customer,
                             on_delete=models.CASCADE,
                             db_column="Customer_ID",
                             related_name="loans"
                         )
    loan_id = models.IntegerField()
    loan_amount        = models.DecimalField(max_digits=12, decimal_places=2)
    tenure             = models.IntegerField(help_text="Months")
    interest_rate      = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_payment    = models.DecimalField(max_digits=12, decimal_places=2)
    emis_paid_on_time  = models.IntegerField()
    date_of_approval   = models.DateField()
    end_date           = models.DateField()

    def __str__(self):
        return f"Loan {self.loan_id} for {self.customer}"
