from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from ecommerce_app.models import Cart
from ecommerce_app.utils import STATUS_CHOICES

@receiver(user_logged_in)
def transfer_cart_to_user(sender, request, user, **kwargs):
    print('is this working')
    session_id = request.session.get('cart_id')
    if session_id:
        # Get all cart items associated with the session ID
        session_cart_items = Cart.objects.filter(session_id=session_id, status=STATUS_CHOICES[1][0])

        for item in session_cart_items:
            # Check if the item already exists in the user's cart
            user_cart_item, created = Cart.objects.get_or_create(
                user=user,
                product=item.product,
                status=STATUS_CHOICES[1][0],
                defaults={'quantity': item.quantity}
            )
            if not created:
                # If the item exists, update the quantity
                user_cart_item.quantity += item.quantity
                user_cart_item.save()

        # After transferring, clear the session cart
        session_cart_items.delete()
        # Optionally clear the session cart ID
        del request.session['cart_id']