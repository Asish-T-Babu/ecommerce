from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission
from rest_framework import status
from django.db.models import Q

from ecommerce_app.urls import STATUS_CHOICES

class IsUserActive(BasePermission):
    def has_permission(self, request, view):
        user = request._user
        if user.status != STATUS_CHOICES[1][0]:
            if user.status == STATUS_CHOICES[0][0]:
                raise ValidationError({"status": "error", "detail": "User Not Active."}, status.HTTP_400_BAD_REQUEST)
            else:
                raise ValidationError({"status": "error", "detail": "User Doesn't Exist."}, status.HTTP_400_BAD_REQUEST)
            
        return True

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        user = request._user
        if user.is_superadmin != True:
            raise ValidationError({'status': 'error', 'detail': 'API For Admin Only'})
        
        return True