from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.response import Response

# For Cart CRUD operations
class CartMixin:
    def get_cart(self, request):
        if isinstance(request.user, AnonymousUser):
            return request.session.get('cart', {})
        else:
            return {item.product_id: item.quantity for item in request.user.cart_user.all()}

    def save_cart(self, request, cart):
        if isinstance(request.user, AnonymousUser):
            request.session['cart'] = cart
        else:
            for product_id, quantity in cart.items():
                cart_item, created = request.user.cart_user.get_or_create(product_id=product_id)
                if not created:
                    cart_item.quantity += quantity
                else:
                    cart_item.quantity = quantity
                cart_item.save()

    def add_to_cart(self, request, product, quantity):
        cart = self.get_cart(request)
        product_id = str(product.id)

        if product_id in cart:
            cart[product_id] += quantity
        else:
            cart[product_id] = quantity

        self.save_cart(request, cart)
        return Response({'message': 'Product added to cart successfully'}, status=status.HTTP_200_OK)
