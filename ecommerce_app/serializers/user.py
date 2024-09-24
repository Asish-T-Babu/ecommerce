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

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'user', 'name', 'phone', 'pincode', 'locality', 'city', 'state', 'land_mark', 'alternative_phone', 'address_type', 'status', 'created_at', 'updated_at']

class CartSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.filter(status = STATUS_CHOICES[1][0]), required=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'quantity', 'status', 'created_at', 'updated_at']

class ProductPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPurchase
        fields = ['id', 'user', 'product', 'product_price', 'quantity', 'payment_status', 'order_status', 'status', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        """
        Allow only `payment_status` and `order_status` to be updated.
        """
        # Update only `payment_status` and `order_status`
        instance.payment_status = validated_data.get('payment_status', instance.payment_status)
        instance.order_status = validated_data.get('order_status', instance.order_status)
        instance.save()
        return instance
