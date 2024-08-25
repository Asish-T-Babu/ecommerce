from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from ecommerce_app.models.user import *


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required = True)
    email = serializers.EmailField(required = True)
    user_currency = serializers.CharField(required = True)
    password = serializers.CharField(required = True)

    def validate_user_currency(self, value):
        print('woowo',value)
        allowed_user_currency = ['rupee', 'dollar']
        if value not in allowed_user_currency:
            raise serializers.ValidationError("Only rupee, dollar allowed.")
        return value
    
    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if user:
            raise serializers.ValidationError("User with this email already exists.")
        return value

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'user_currency', 'profile_image', 'is_superadmin', 'is_staff', 'is_admin', 'status', 'created_at', 'updated_at', 'password']

        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'user_currency': {'write_only': True}
        }

    def create(self, validated_data):
        print(validated_data, 'validated_data')
        password = validated_data.pop('password', '')

        instance = self.Meta.model(**validated_data)
        instance.set_password(password)
        instance.save()
        return instance

