

from rest_framework import serializers
from .models import Customer

class RegisterSerializer(serializers.ModelSerializer):
   
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
            "age",
            "phone_number",
            "monthly_salary",
            "approved_limit",
        ]

   
    def create(self, validated_data):
        salary = validated_data["monthly_salary"]
        
        approved_limit = (salary * 36 // 100_000) * 100_000
        validated_data["approved_limit"] = approved_limit
        return super().create(validated_data)
