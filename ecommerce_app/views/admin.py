from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from ecommerce_app.models.admin import Brand, Category, Product, ProductImage
from ecommerce_app.serializers.admin import BrandSerializer, CategorySerializer, ProductSerializer
from ecommerce_app.utils import STATUS_CHOICES
from ecommerce_app.pagination import StandardResultsSetPagination
from permission import IsUserActive, IsSuperUser

# Brand API's
class BrandListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsUserActive, IsSuperUser]

    # We Can Specify The Queryset In Class Level and When We Try To Access The Queryset Using Built-In get_queryset(), The Queryset Will Be The One Which We Set On Class Level But Here We Override The get_queryset() For Implementing Search Functionality
    # queryset = Brand.objects.filter(status=STATUS_CHOICES[1][0])
    serializer_class = BrandSerializer

    def get_queryset(self):
        """
        Override the default queryset to include manual search functionality.
        """
        queryset = Brand.objects.filter(status=STATUS_CHOICES[1][0])
        search_query = self.request.query_params.get('search', None)
        
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)  # Filter based on case-insensitive match
        
        return queryset

    def list(self, request, *args, **kwargs):
        """
        Get All Brands with search functionality
        """
        queryset = self.get_queryset()
        paginator = StandardResultsSetPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request) 
        serializer = self.get_serializer(paginated_queryset, many=True)
        return paginator.get_paginated_response({'status': 'success', 'data': serializer.data})
    
    def create(self, request, *args, **kwargs):
        """
        Create New Brand
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response({'status': 'validation_error', 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response({"status": "success", "data": 'Brand created successfully'}, status=status.HTTP_201_CREATED)


class BrandRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsUserActive, IsSuperUser]
    queryset = Brand.objects.filter(status=STATUS_CHOICES[1][0])
    serializer_class = BrandSerializer

    def get(self, request, *args, **kwargs):
        """
        Get Single Brand
        """
        try:
            instance = self.get_object()
        except:
            return Response({'status': 'error', 'data': 'Brand not found'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance)
        return Response({"status": "success","data": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        """
        Update Every Fields Of Brand
        """
        partial = kwargs.pop('partial', False)
        try:
            instance = self.get_object()
        except:
            return Response({'status': 'error', 'data': 'Brand not found'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            return Response({'status': 'validation_error', 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)
        return Response({'status': 'success',"data": "Brand updated successfully"}, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        """
        Partial Update Of Brand
        """
        return self.put(request, *args, **kwargs)


    def destroy(self, request, *args, **kwargs):
        """
        Delete Brand
        """
        try:
            instance = self.get_object()
        except:
            return Response({'status': 'error', 'data': 'Brand not found'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = STATUS_CHOICES[2][0]
        instance.save()
        return Response({'status': 'success', 'data': 'Brand deleted succefully'}, status=status.HTTP_200_OK)
    

# Category API's
class CategoryListCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsUserActive, IsSuperUser]

    # We Can Specify The Queryset In Class Level and When We Try To Access The Queryset Using Built-In get_queryset(), The Queryset Will Be The One Which We Set On Class Level But Here We Override The get_queryset() For Implementing Search Functionality
    # queryset = Category.objects.filter(status=STATUS_CHOICES[1][0])
    serializer_class = CategorySerializer

    def get_queryset(self):
        """
        Override the default queryset to include manual search functionality.
        """
        queryset = Category.objects.filter(status=STATUS_CHOICES[1][0])
        search_query = self.request.query_params.get('search', None)
        
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)  # Filter based on case-insensitive match
        
        return queryset

    def get(self, request, *args, **kwargs):
        """
        Get All Categories with search functionality
        """
        queryset = self.get_queryset()
        paginator = StandardResultsSetPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request) 
        serializer = self.get_serializer(paginated_queryset, many=True)
        return paginator.get_paginated_response({'status': 'success', 'data': serializer.data})

    def post(self, request, *args, **kwargs):
        """
        Create New Category
        """
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({'status': 'validation_error', 'data': serializer.errors})
        serializer.save()
        return Response({'status': 'validation_error', 'data': "Category created successfully"}, status=status.HTTP_201_CREATED)

class CategoryRetrieveUpdateDestroyView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsUserActive, IsSuperUser]
    queryset = Category.objects.filter(status=STATUS_CHOICES[1][0])
    serializer_class = CategorySerializer

    def get(self, request, *args, **kwargs):
        """
        Get Category
        """
        try:
            instance = self.get_object()
        except:
            return Response({'status': 'error', 'data': 'Category not found'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance)
        return Response({'status': 'error', 'data': serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        """
        Update Every Fields Of Category
        """
        try:
            instance = self.get_object()
        except:
            return Response({'status': 'error', 'data': 'Category not found'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            return Response({'status': 'validation_error', 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        """
        Partial Update Of Category
        """
        try:
            instance = self.get_object()
        except:
            return Response({'status': 'error', 'data': 'Category not found'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'status': 'validation_error', 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except:
            return Response({'status': 'error', 'data': 'Category not found'}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = STATUS_CHOICES[2][0]
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Product CRUD API's
class ProductListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsUserActive, IsSuperUser]

    def get(self, request):
        """
        List all products along with their images.
        """
        products = Product.objects.filter(status=STATUS_CHOICES[1][0])  # Only active products
        paginator = StandardResultsSetPagination()
        paginated_products = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(paginated_products, many=True)
        return paginator.get_paginated_response({
            'status': 'success', 
            'data': serializer.data
        })

    def post(self, request):
        """
        Create a new product along with its images.
        """
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': 'validation_error', 
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated, IsUserActive, IsSuperUser]

    def get_object(self, pk):
        """
        Retrieve product by its primary key (ID).
        """
        try:
            return Product.objects.get(pk=pk, status=STATUS_CHOICES[1][0])
        except Product.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Retrieve a product by its ID.
        """
        product = self.get_object(pk)
        if not product:
            return Response({
                'status': 'error', 
                'data': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(product)
        return Response({
            'status': 'success',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Update a product and its images using the full update (PUT).
        """
        product = self.get_object(pk)
        if not product:
            return Response({
                'status': 'error',
                'data': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'status': 'validation_error',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """
        Partially update a product and its images (PATCH).
        """
        product = self.get_object(pk)
        if not product:
            return Response({
                'status': 'error',
                'data': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'status': 'validation_error',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Soft delete a product by changing its status.
        """
        product = self.get_object(pk)
        if not product:
            return Response({
                'status': 'error',
                'data': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Soft delete: update the status of the product instead of deleting it
        product.status = STATUS_CHOICES[2][0]  # For example, mark as inactive
        product.save()
        return Response({
            'status': 'success',
            'data': 'Product deleted successfully'
        }, status=status.HTTP_200_OK)
    
    def delete_image(self, request, pk, image_id):
        """
        Delete a specific image associated with the product.
        """
        product = self.get_object_by_id(pk)
        if not product:
            return Response({'status': 'error', 'data': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Retrieve the product image by its ID and ensure it belongs to the product
            product_image = ProductImage.objects.get(id=image_id, product=product)
        except ProductImage.DoesNotExist:
            return Response({
                'status': 'error',
                'data': 'Product image not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Delete the image
        product_image.status = STATUS_CHOICES[2][0]
        product_image.save()

        return Response({
            'status': 'success',
            'data': 'Product image deleted successfully'
        }, status=status.HTTP_200_OK)