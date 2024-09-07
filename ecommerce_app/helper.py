from django.contrib.auth.models import AnonymousUser

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response

from datetime import timedelta
import uuid

from ecommerce_app.utils import STATUS_CHOICES
from ecommerce_app.models.user import Cart

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


# For Cart CRUD operations
class CartMixin:
    def get_cart(self, request):
        if isinstance(request.user, AnonymousUser):
            cart_id = request.session.get('cart_id')
            if not cart_id:
                cart_id = str(uuid.uuid4())
                request.session['cart_id'] = cart_id
            return Cart.objects.filter(session_id = cart_id, status = STATUS_CHOICES[1][0])
        else:
            return request.user.cart_user.filter(status = STATUS_CHOICES[1][0])

    def add_to_cart(self, request, product_id, quantity):
        if isinstance(request.user, AnonymousUser):
            cart_id = request.session.get('cart_id')
            if cart_id:
                cart_item = Cart.objects.filter(session_id = cart_id, product__id = product_id, status = STATUS_CHOICES[1][0]).first()
                if cart_item:
                    cart_item.quantity += quantity
                    cart_item.save()
                else:
                    Cart.objects.create(session_id = cart_id, product_id = product_id, quantity = quantity)
            else:
                cart_id = uuid.uuid4()
                request.session['cart_id'] = str(cart_id)
                Cart.objects.create(session_id = cart_id, product_id = product_id, quantity = 1)
            
        else:
            cart_item = request.user.cart_user.filter(product_id=product_id).first()
            if not cart_item:
                cart_item = Cart()
                cart_item.user = request.user
                cart_item.product_id = product_id
                cart_item.quantity = quantity
            else:
                cart_item.quantity += quantity
            cart_item.save()
        return
    
    def search_product_in_cart(self, request, product_id):
        if isinstance(request.user, AnonymousUser):
            cart_id = request.session.get('cart_id')
            if cart_id:
                # Searching for the product in the anonymous user's session-based cart
                cart_item = Cart.objects.filter(session_id=cart_id, product_id=product_id, status=STATUS_CHOICES[1][0]).first()
            else:
                cart_item = None
        else:
            # Searching for the product in the authenticated user's cart
            cart_item = request.user.cart_user.filter(product_id=product_id, status=STATUS_CHOICES[1][0]).first()

        if cart_item:
            return cart_item
        else:
            return None
