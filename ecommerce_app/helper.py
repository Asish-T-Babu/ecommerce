from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta

def create_jwt_token_for_user(user, expiry_hours = None):
    """
    Create JWT Refresh & Access Token For User
    """
    refresh = RefreshToken.for_user(user)
    if expiry_hours:
        refresh.set_exp(lifetime=timedelta(hours=expiry_hours))

    return {
        'refresh_token': str(refresh),
        'access_token': str(refresh.access_token),
    }