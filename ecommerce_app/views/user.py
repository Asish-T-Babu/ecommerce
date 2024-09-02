from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions, mixins
from rest_framework.exceptions import ValidationError

from django.contrib.auth import authenticate
from django.db.models import Q

from ecommerce_app.serializers.user import UserSerializer, CartSerializer
from ecommerce_app.models.user import User, Cart
from ecommerce_app.utils import STATUS_CHOICES
from ecommerce_app.helper import create_jwt_token_for_user, CartMixin
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
def user_list(request):
    """
    Get All Users
    """
    users = User.objects.filter(status=STATUS_CHOICES[1][0])
    user_serializer = UserSerializer(users, many = True)
    return Response({'status': 'success', 'data': user_serializer.data}, status= status.HTTP_200_OK)

@api_view(['GET'])
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

# Cart Views
class CartViewSet(CartMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Cart.objects.filter(status=STATUS_CHOICES[1][0])
    serializer_class = CartSerializer

    def perform_create(self, serializer):
        """
        Add Product To Cart -> Here We are over ridding CreateModelMixin The Values After Validating The Data, But We Need To Throw Custom Validation Error
        """
        if not serializer.is_valid():
            raise ValidationError({'error': 'Custom error during creation.', 'details': serializer.errors})
        
        product = serializer.validated_data.get('product')
        quantity = serializer.validated_data.get('quantity')
        
        self.add_to_cart(self.request, product.id, quantity)

        return Response({'message': 'Product added to cart successfully'}, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        if not serializer.is_valid():
            raise ValidationError({'error': 'Custom error during update.', 'details': serializer.errors})
        
        product = serializer.validated_data.get('product')
        quantity = serializer.validated_data.get('quantity')
        
        self.add_to_cart(self.request, product.id, quantity)

        return Response({'message': 'Product updated in cart successfully'}, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        if instance.product.is_protected:
            raise ValidationError({'error': f'Product {instance.product.name} cannot be removed from the cart.'})

        instance.status = STATUS_CHOICES[2][0]
        instance.save()

        return Response({'message': 'Productremoved from cart successfully'}, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        cart = self.get_cart(request)
        serializer = CartSerializer(cart, many=True)
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
