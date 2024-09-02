from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework import mixins

class CartViewSet(CartMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Cart.objects.filter(status=STATUS_CHOICES[1][0])
    serializer_class = CartSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # Custom error handling
            raise ValidationError({'error': 'Custom error during creation.', 'details': serializer.errors})

        # If valid, proceed to perform_create
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'message': 'Product added to cart successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            # Custom error handling
            raise ValidationError({'error': 'Custom error during update.', 'details': serializer.errors})

        # If valid, proceed to perform_update
        self.perform_update(serializer)
        return Response({'message': 'Product updated in cart successfully', 'data': serializer.data}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Product removed from cart successfully'}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        product = serializer.validated_data.get('product')
        quantity = serializer.validated_data.get('quantity')

        # Custom business logic errors can still be raised here
        if quantity <= 0:
            raise ValidationError({'quantity': 'Quantity must be greater than zero.'})

        self.add_to_cart(self.request, product.id, quantity)

    def perform_update(self, serializer):
        product = serializer.validated_data.get('product')
        quantity = serializer.validated_data.get('quantity')

        # Custom business logic errors can still be raised here
        if quantity <= 0:
            raise ValidationError({'quantity': 'Quantity must be greater than zero.'})

        self.add_to_cart(self.request, product.id, quantity)
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        # Custom business logic errors can still be raised here
        if instance.product.is_protected:
            raise ValidationError({'error': f'Product {instance.product.name} cannot be removed from the cart.'})

        instance.status = STATUS_CHOICES[2][0]
        instance.save()
        super().perform_destroy(instance)

    def list(self, request, *args, **kwargs):
        cart = self.get_cart(request)
        serializer = CartSerializer(cart, many=True)
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
