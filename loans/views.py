from django.shortcuts import render
from datetime import date
from dateutil.relativedelta import relativedelta
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import Max   
# Create your views here.
from rest_framework import generics,status
from .models import Customer,Loan
from .serializers import RegisterSerializer,EligibilitySerializer,LoanListSerializer,LoanDetailSerializer

class RegisterAPIView(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = RegisterSerializer

class CheckEligibilityAPIView(generics.CreateAPIView):
    serializer_class = EligibilitySerializer

class CreateLoanAPIView(APIView):
    def post(self, request, *args, **kwargs):
       
        elig = EligibilitySerializer(data=request.data)
        elig.is_valid(raise_exception=True)
        result = elig.save()

        # 2) If not approved, return 400
        if not result["approved"]:
            return Response({
                "loan_id": None,
                "customer_id": result["customer_id"],
                "loan_approved": False,
                "message": "Loan not approved based on credit score or EMI constraints.",
                "monthly_installment": result["monthly_installment"],
            }, status=status.HTTP_400_BAD_REQUEST)

        # 3) Approved → compute next global loan_id
        max_id = Loan.objects.aggregate(Max("loan_id"))["loan_id__max"] or 0
        next_id = max_id + 1

        # 4) Create the Loan record, assigning our new loan_id
        cust = Customer.objects.get(pk=result["customer_id"])
        loan = Loan.objects.create(
            customer          = cust,
            loan_id           = next_id,
            loan_amount       = result["loan_amount"],
            tenure            = result["tenure"],
            interest_rate     = result["corrected_rate"],
            monthly_payment   = result["monthly_installment"],
            emis_paid_on_time = 0,
            date_of_approval  = date.today(),
            end_date          = date.today() + relativedelta(months=result["tenure"]),
        )

        # 5) Return the newly minted loan_id
        return Response({
            "loan_id": loan.loan_id,
            "customer_id": cust.customer_id,
            "loan_approved": True,
            "message": "Loan approved successfully.",
            "monthly_installment": loan.monthly_payment,
        }, status=status.HTTP_201_CREATED)

class LoanDetailAPIView(generics.RetrieveAPIView):
    """
    GET /view-loan/<loan_id>/
    Returns one loan’s full details, including nested customer.
    """
    queryset = Loan.objects.select_related("customer")
    serializer_class = LoanDetailSerializer
    lookup_field = "loan_id"
    lookup_url_kwarg = "loan_id"


class LoanListAPIView(generics.ListAPIView):
    """
    GET /view-loans/<customer_id>/
    Returns all active loans (end_date >= today) for that customer.
    """
    serializer_class = LoanListSerializer

    def get_queryset(self):
        cust_id = self.kwargs["customer_id"]
        today = date.today()
        return Loan.objects.filter(
            customer__customer_id=cust_id,
            end_date__gte=today
        )
