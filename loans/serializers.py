
from decimal import Decimal
from datetime import date
from rest_framework import serializers
from .models import Customer,Loan


class RegisterSerializer(serializers.ModelSerializer):

    first_name   = serializers.CharField(max_length=100, write_only=True)
    last_name    = serializers.CharField(max_length=100, write_only=True)

  
    age            = serializers.IntegerField()
    phone_number   = serializers.CharField(max_length=15)
    monthly_income = serializers.DecimalField(
        source="monthly_salary",  
        max_digits=12,
        decimal_places=2,
    )

    customer_id    = serializers.IntegerField(read_only=True)
    name           = serializers.SerializerMethodField(read_only=True)
    approved_limit = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Customer
       
        fields = [
            "first_name",
            "last_name",
            "customer_id",
            "name",
            "age",
            "monthly_income",
            "approved_limit",
            "phone_number",
        ]

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def create(self, validated_data):
      
        salary = validated_data["monthly_salary"]

        approved_limit = round((salary * Decimal("36")) / Decimal("100000")) * Decimal("100000")
        validated_data["approved_limit"] = approved_limit

        return super().create(validated_data)


class EligibilitySerializer(serializers.Serializer):
    
    customer_id   = serializers.IntegerField()
    loan_amount   = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        write_only=True
    )
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure        = serializers.IntegerField()

  
    approval                   = serializers.BooleanField(source="approved", read_only=True)
    corrected_interest_rate    = serializers.DecimalField(
        source="corrected_rate",
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    monthly_installment        = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    def validate(self, attrs):
        cust  = Customer.objects.prefetch_related("loans").get(pk=attrs["customer_id"])
        loans = cust.loans.all()

        
        total_emis = sum(l.tenure for l in loans)
        on_time    = sum(l.emis_paid_on_time for l in loans)
        on_time_pct = (Decimal(on_time) / Decimal(total_emis) * 100) if total_emis else Decimal("100")

    
        num_loans = loans.count()
        loans_factor_pct = Decimal("1") / (num_loans + 1) * 100

       
        current_year = date.today().year
        year_loans   = loans.filter(date_of_approval__year=current_year).count()
        activity_pct = Decimal(year_loans) / (num_loans + 1) * 100

       
        total_volume = sum(l.loan_amount for l in loans)
        limit        = cust.approved_limit or Decimal("1")
        volume_pct   = min(total_volume / limit * 100, Decimal("100"))

        
        active_debt = sum(l.monthly_payment for l in loans if l.end_date >= date.today())
        emi_ok      = active_debt <= cust.monthly_salary * Decimal("0.5")
        emi_pct     = Decimal("100") if emi_ok else Decimal("0")

        
        if not emi_ok:
            score = Decimal("0")
        else:
            score = (on_time_pct + loans_factor_pct + activity_pct + volume_pct + emi_pct) / Decimal("5")

        attrs["_cust"]  = cust
        attrs["_score"] = score
        attrs["_emi_ok"] = emi_ok
        return attrs

    def create(self, validated_data):
        cust       = validated_data["_cust"]
        score      = validated_data["_score"]
        emi_ok     = validated_data["_emi_ok"]
        P          = validated_data["loan_amount"]
        req_rate   = validated_data["interest_rate"]
        n          = validated_data["tenure"]

       
        if not emi_ok:
            return {
                "customer_id":           cust.customer_id,
                "approved":              False,
                "interest_rate":         req_rate,
                "corrected_rate":        req_rate.quantize(Decimal("0.01")),
                "tenure":                n,
                "monthly_installment":   Decimal("0.00"),
            }

       
        if score > Decimal("50"):
            slab = None
        elif score > Decimal("30"):
            slab = Decimal("12")
        elif score > Decimal("10"):
            slab = Decimal("16")
        else:
            slab = Decimal("Infinity")

        approved  = (score > Decimal("10")) and (slab is None or req_rate >= slab)
        corrected = req_rate if slab is None or req_rate >= slab else slab

       
        if approved:
            r = corrected / Decimal("100") / Decimal("12")
            numerator   = P * r * (Decimal("1") + r) ** n
            denominator = (Decimal("1") + r) ** n - Decimal("1")
            emi = numerator / denominator
        else:
            emi = Decimal("0")

        return {
            "customer_id":           cust.customer_id,
             "loan_amount":           P,
            "approved":              approved,
            "interest_rate":         req_rate,
            "corrected_rate":        corrected.quantize(Decimal("0.01")),
            "tenure":                n,
            "monthly_installment":   emi.quantize(Decimal("0.01")),
        }
class LoanDetailSerializer(serializers.ModelSerializer):
    loan_id = serializers.IntegerField(read_only=True)

    monthly_installment = serializers.DecimalField(
        source="monthly_payment",
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

   
    customer = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = [
            "loan_id",
            "customer",
            "loan_amount",
            "interest_rate",
            "monthly_installment",
            "tenure",
            "date_of_approval",
            "end_date",
            "emis_paid_on_time",
        ]

    def get_customer(self, obj):
        c = obj.customer
        return {
            "customer_id": c.customer_id,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "age": c.age,
            "phone_number": c.phone_number,
            "monthly_salary": str(c.monthly_salary),
            "approved_limit": str(c.approved_limit),
        }


class LoanListSerializer(serializers.ModelSerializer):
    loan_id = serializers.IntegerField(read_only=True)

    monthly_installment = serializers.DecimalField(
        source="monthly_payment",
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    repayments_left = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = [
            "loan_id",
            "loan_amount",
            "interest_rate",
            "monthly_installment",
            "repayments_left",
        ]

    def get_repayments_left(self, obj):
       
        return obj.tenure - obj.emis_paid_on_time