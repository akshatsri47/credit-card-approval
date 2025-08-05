from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from .models import Customer
from .serializers import RegisterSerializer

class RegisterAPIView(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = RegisterSerializer
