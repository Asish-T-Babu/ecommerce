from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.signals import user_logged_in
from django.contrib.auth import authenticate
from django.db.models import Q
from django.db import transaction

from ecommerce_app.serializers.user import UserSerializer, AddressSerializer, CartSerializer, ProductPurchaseSerializer
from ecommerce_app.models.admin import Product
from ecommerce_app.models.user import User, Address, Cart, ProductPurchase
from ecommerce_app.utils import STATUS_CHOICES, ORDER_STATUS
from ecommerce_app.helper import create_jwt_token_for_user, CartMixin
from ecommerce_app.pagination import StandardResultsSetPagination
from permission import IsUserActive, IsSuperUser
# Create your views here.

# User views
@api_view(['POST'])
def create_user(req):
    """
    Create User
    """

    user_serializer = UserSerializer(data=req.data)
    if user_serializer.is_valid():
        user = user_serializer.save()
        return Response({"status": "success",
                            "data": "User Created Successfully."},
                        status=status.HTTP_201_CREATED)
    else:
        return Response({"status": "validation_error", "data": user_serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    """
    Login User With Email & Password
    * Validate Email & Password available on the DB
    * Validate if User status is Active
    * Validate if User Tenant is Active
    """
    email = request.data.get('email')
    password = request.data.get('password')
    errors = {}

    if not email or email is None:
        errors['email'] = ["This field is required."]

    if not password or password is None:
        errors['password'] = ["This field is required."]
        return Response(
            {"status": "validation_error", "data": errors},
            status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(email=email, password=password)
        
    if user:
        if user.status == STATUS_CHOICES[1][0]:
                user_logged_in.send(sender=user.__class__, request=request, user=user)
                token = create_jwt_token_for_user(user)
                return Response({"status": "success", "data": {"msg": "User LoggedIn Successfully.", "token": token['access_token'], 'email' : user.email}}, status=status.HTTP_200_OK)
        elif user.status == STATUS_CHOICES[4][0]:
           return Response({"status": "validation_error", "data": {"email": ["You don't have access to the application. Verify your email to continue."] }}, status=status.HTTP_401_UNAUTHORIZED)
        else :
            return Response({"status": "validation_error", "data": {"email": ["You don't have access to the application. Please contact admin."] }}, status=status.HTTP_400_BAD_REQUEST)  
    else:
        user = User.objects.filter(email = email).first()
        if user:
            if user.status == STATUS_CHOICES[1][0]:
                return Response({'status': 'validation_error', 'data': {"email": ["Invalid Credentials."]}}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'status': 'validation_error', 'data': {"email": ["You don't have access to the application. Please contact admin"]}}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"status": "validation_error", "data": {"email": ["Please Register and Login."] }}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsUserActive, IsSuperUser])
def user_list(request):
    """
    Get All Users
    """
    users = User.objects.filter(status=STATUS_CHOICES[1][0]).order_by('-created_at')
    paginator = StandardResultsSetPagination()
    paginated_user = paginator.paginate_queryset(users, request) 
    user_serializer = UserSerializer(paginated_user, many = True)
    return paginator.get_paginated_response({'status': 'success', 'data': user_serializer.data})

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsUserActive])
def get_user(request, user_id):
    """
    Get Single User
    """
    user = User.objects.filter(id = user_id).first()
    if not user:
        return Response({'status': 'error', 'data': "User not found"}, status= status.HTTP_400_BAD_REQUEST)
    user_serializer = UserSerializer(user)
    return Response({'status': 'success', 'data': user_serializer.data}, status= status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsUserActive])
def update_user(request, user_id):
    """
    Update User
    """
    user = User.objects.filter(id = user_id).first()
    if not user:
        return Response({'status': 'error', 'data': 'User not found'}, status= status.HTTP_400_BAD_REQUEST)
    user_serializer = UserSerializer(user, data= request.data, partial= True)
    if user_serializer.is_valid():
        user_serializer.save()
        return Response({'status': 'success', 'data': 'User updated successfully'}, status= status.HTTP_200_OK)
    else:
        return Response({'status': 'validation_error', 'data': user_serializer.errors}, status= status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsUserActive])
def delete_user(request, user_id):
    """
    Delete User
    """
    user = User.objects.filter(id = user_id).first()
    if not user:
        return Response({'status': 'error', 'data': 'User not found'}, status= status.HTTP_400_BAD_REQUEST)
    user.status = STATUS_CHOICES[2][0]
    user.save()
    return Response({'status': 'User deleted successfully'}, status= status.HTTP_200_OK)


# Address Views
class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    # queryset = Address.objects.all(status=STATUS_CHOICES[1][0])
    permission_classes = [IsAuthenticated, IsUserActive]

    def get_queryset(self):
        # Ensure the queryset only includes addresses with a specific status
        return Address.objects.filter(status=STATUS_CHOICES[1][0])
    
    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()
        data['user'] = user.id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            # serializer.save()
            self.perform_create(serializer)
            return Response({'status': 'success', 'data': 'Address created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status': 'validation_error', 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Update the payment_status or order_status for a purchase.
        """
        instance = self.get_object()
        partial = kwargs.pop('partial', False)
        user = request.user
        data = request.data.copy()
        data['user'] = user.id
        serializer = self.get_serializer(instance, data=data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
        else:
            return Response({'status': 'validation_error', 'data': serializer.errors}, status= status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete a purchase by setting status to 2.
        """
        instance = self.get_object()
        instance.status = STATUS_CHOICES[2][0]
        instance.save()
        return Response({"detail": "Purchase deleted successfully"}, status=status.HTTP_200_OK)
    
    def list(self, request, *args, **kwargs):
        """
        Override list to return purchases in a custom format.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"status": "success", "purchases": serializer.data}, status= status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """
        Override retrieve to return a custom response for a single purchase.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"status": 'success', "data": serializer.data}, status= status.HTTP_200_OK)
    

# Cart Views
class CartViewSet(CartMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsUserActive]
    queryset = Cart.objects.filter(status=STATUS_CHOICES[1][0])
    serializer_class = CartSerializer

    def get_object(self):
        """
        Override get_object to filter by status.
        """
        # Use self.kwargs to get the lookup field value (default is 'pk')
        lookup_field_value = self.kwargs.get(self.lookup_field)

        # Attempt to get the cart item filtered by status
        try:
            instance = Cart.objects.get(pk=lookup_field_value, status=STATUS_CHOICES[1][0])
        except:
            # Handle case where no matching cart item is found
            raise Response({'status': 'error', 'data': 'Cart Item not found or inactive'}, status=status.HTTP_400_BAD_REQUEST)
        
        return instance
    
    # Custom action for searching a product in the cart
    @action(detail=False, methods=['get'], url_path='search/(?P<product_id>[^/.]+)')
    def search_product(self, request, product_id=None):
        """
        Search for a specific product in the cart by product ID.
        """
        cart_item = self.search_product_in_cart(request, product_id)
        if cart_item:
            serializer = self.get_serializer(cart_item)
            return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'error', 'data': 'Product not found in cart'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        """
        Adding Item To Cart -> Here we are using create method and perform create to do this task, we can only use create function but for learning purpose we are using both, perform_create will handle the logic after raising the serializer validationn error, for throwing custom serializer validation error create function is used, after validating  the serilizer the rest operations can be performed here itself
        """
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # Custom error handling
            return Response({'status': 'validation_error', 'data': serializer.errors}, status= status.HTTP_400_BAD_REQUEST)

        # If valid, proceed to perform_create
        self.perform_create(serializer)
        return Response({'status': 'success', 'data': "Item added in cart"}, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """
        Override the retrieve method to add custom logic
        """
        try:
            # Get the cart item instance
            instance = self.get_object()
        except:
            # Handle the case where the object is not found
            return Response({'status': 'error', 'data': 'Cart Item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the instance
        serializer = self.get_serializer(instance)
        
        # Return the response
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)

        try:
            # Get the cart item instance
            instance = self.get_object()
        except:
            return Response({'status': 'error', 'data': 'Cart Item not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if 'quantity' is in the request data
        quantity = request.data.get('quantity', None)
        if quantity is None:
            return Response({'status': 'error', 'data': 'Quantity is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the quantity
        try:
            instance.quantity += int(quantity)
            if instance.quantity <= 0:
                return Response({'status': 'error', 'data': 'Quantity must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)
            instance.save()
        except ValueError:
            return Response({'status': 'error', 'data': 'Invalid quantity_change value'}, status=status.HTTP_400_BAD_REQUEST)

        # Serialize the updated instance
        serializer = self.get_serializer(instance)

        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Delete The Cart Instance
        """
        try:
            instance = self.get_object()
        except:
            return Response({'status': 'error', 'data': 'Cart Item not found'}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response({'status': 'success', 'data': 'Product removed from cart successfully'}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        product = serializer.validated_data.get('product')
        quantity = serializer.validated_data.get('quantity')

        self.add_to_cart(self.request, product.id, quantity)

    # The Below Function Is Not Needed Because, I Am Only Updating The Quantity Of The Instance
    # def perform_update(self, serializer):
    #     product = serializer.validated_data.get('product')
    #     quantity = serializer.validated_data.get('quantity')

    #     self.add_to_cart(self.request, product.id, quantity)
    #     super().perform_update(serializer)

    def perform_destroy(self, instance):
        instance.status = STATUS_CHOICES[2][0]
        instance.save()
        super().perform_destroy(instance)

    def list(self, request, *args, **kwargs):
        cart = self.get_cart(request)
        serializer = CartSerializer(cart, many=True)
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)

# PurchaseProduct Views
class ProductPurchaseViewSet(viewsets.ModelViewSet):
    serializer_class = ProductPurchaseSerializer
    queryset = ProductPurchase.objects.all()

    def get_queryset(self):
        """
        Filter purchases by the logged-in user.
        """
        user = self.request.user
        return ProductPurchase.objects.filter(user=user, status=STATUS_CHOICES[1][0])
    
    def create(self, request, *args, **kwargs):
        user = request.user
        cart_items = Cart.objects.filter(user=user)

        # If a specific product is being purchased
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)  # Default to 1 if no quantity is provided

        # Check if the request is for a single product or all products
        if product_id:
            return self._purchase_product_not_from_cart(user, product_id, quantity)

        # Purchase all products in the cart
        if cart_items.exists():
            self._purchase_all_products(user, cart_items)
            return Response({"status": "success", "data": "All products purchased successfully."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "error", "data": "No products in cart."}, status=status.HTTP_400_BAD_REQUEST)

    def _purchase_single_product(self, user, cart_item, quantity):
        """Helper method to handle single product purchase (if in cart)."""
        product_purchase_data = {
            'user': user.id,
            'product': cart_item.product.id,
            'product_price': cart_item.product.price,  # Assuming product has a price field
            'quantity': quantity,
            'payment_status': True,  # Adjust payment logic as needed
            'order_status': ORDER_STATUS[0][0],  # Default to 'ORDERED'
        }

        serializer = ProductPurchaseSerializer(data=product_purchase_data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response({'status': 'validation_error', 'data': serializer.errors})

        # Remove the product from the cart after purchase
        cart_item.delete()

    def _purchase_product_not_from_cart(self, user, product_id, quantity):
        """Helper method to handle purchase when the product is not in the cart."""
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Prepare the purchase data
        product_purchase_data = {
            'user': user.id,
            'product': product.id,
            'product_price': product.price,
            'quantity': quantity,
            'payment_status': False,
            'order_status': ORDER_STATUS[0][0],
        }

        # Use the serializer to create the purchase
        serializer = ProductPurchaseSerializer(data=product_purchase_data)
        if serializer.is_valid():
            serializer.save()
            product.stock - quantity
            product.save()
        else:
            return Response({'status': 'validation_error', 'data': serializer.errors})

        return Response({"detail": "Product purchased successfully."}, status=status.HTTP_201_CREATED)

    def _purchase_all_products(self, user, cart_items):
        """Helper method to handle purchasing all products in the cart."""
        with transaction.atomic():
            for cart_item in cart_items:
                self._purchase_single_product(user, cart_item, cart_item.quantity)

    def update(self, request, *args, **kwargs):
        """
        Update the payment_status or order_status for a purchase.
        """
        instance = self.get_object()
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
        else:
            return Response({'status': 'validation_error', 'data': serializer.errors}, status= status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete a purchase by setting status to 2.
        """
        instance = self.get_object()
        instance.status = 2
        instance.save()
        return Response({"detail": "Purchase deleted successfully"}, status=status.HTTP_200_OK)
    
    def list(self, request, *args, **kwargs):
        """
        Override list to return purchases in a custom format.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"status": "success", "purchases": serializer.data}, status= status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """
        Override retrieve to return a custom response for a single purchase.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"status": 'success', "data": serializer.data}, status= status.HTTP_200_OK)
    
# If the order status is updated to completed then authomatically i need to update the payment status to True