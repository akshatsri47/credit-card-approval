from django.urls import path
from .views import RegisterAPIView,CheckEligibilityAPIView,CreateLoanAPIView,LoanDetailAPIView,LoanListAPIView

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("check-eligibility/", CheckEligibilityAPIView.as_view(), name="check-eligibility"),
    path("create-loan/", CreateLoanAPIView.as_view(), name="create-loan"),
    path("view-loan/<int:loan_id>/",   LoanDetailAPIView.as_view(), name="view-loan"),
    path("view-loans/<int:customer_id>/", LoanListAPIView.as_view(), name="view-loans"),
]
