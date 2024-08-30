from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from ecommerce_app.models.user import *


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    user_currency = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=False)

    def validate_user_currency(self, value):
        allowed_user_currency = ['rupee', 'dollar']
        if value not in allowed_user_currency:
            raise serializers.ValidationError("Only rupee, dollar allowed.")
        return value
    
    def validate_email(self, value):
        # check if the serializer is used for update
        if self.instance:
            if self.instance.email == value:
                return value
            
        user = User.objects.filter(email=value).first()
        if user:
            raise serializers.ValidationError("User with this email already exists.")
        return value

    class Meta:
        model = User
        fields = ['id', 'email', 'region_code', 'phone_number', 'first_name', 'last_name', 'user_currency', 'profile_image', 'is_superadmin', 'is_staff', 'is_admin', 'status', 'created_at', 'updated_at', 'password']

        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'user_currency': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'quantity', 'status', 'created_at', 'updated_at']