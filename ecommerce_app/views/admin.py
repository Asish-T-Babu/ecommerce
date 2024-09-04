from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from ecommerce_app.models.admin import Brand, Category, Product
from ecommerce_app.serializers.admin import BrandSerializer, CategorySerializer, ProductSerializer
from ecommerce_app.utils import STATUS_CHOICES
from ecommerce_app.pagination import StandardResultsSetPagination
from permission import IsUserActive, IsSuperUser

# Brand API's
class BrandListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsUserActive, IsSuperUser]
    queryset = Brand.objects.filter(status=STATUS_CHOICES[1][0])
    serializer_class = BrandSerializer

    def list(self, request, *args, **kwargs):
        """
        Get All Brands
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
    queryset = Category.objects.filter(status=STATUS_CHOICES[1][0])
    serializer_class = CategorySerializer

    def get(self, request, *args, **kwargs):
        """
        Get All Categories
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

class ProductListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsUserActive, IsSuperUser]

    def get(self, request):
        products = Product.objects.filter(status = STATUS_CHOICES[1][0])
        paginator = StandardResultsSetPagination()
        paginated_product = paginator.paginate_queryset(products, request) 
        product_serializer = ProductSerializer(paginated_product, many = True)
        return paginator.get_paginated_response({'status': 'success', 'data': product_serializer.data})

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'status': 'validation_error', 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated, IsUserActive, IsSuperUser]

    def get_object(self, pk):
        return Product.objects.filter(id = pk).first()

    def get(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response({'status': 'error', 'data': 'Product not found'}, status= status.HTTP_400_BAD_REQUEST)
        serializer = ProductSerializer(product)
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response({'status': 'error', 'data': 'Product not found'}, status= status.HTTP_400_BAD_REQUEST)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({'status': 'error', 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response({'status': 'error', 'data': 'Product not found'}, status= status.HTTP_400_BAD_REQUEST)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({'status': 'error', 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response({'status': 'error', 'data': 'Product not found'}, status= status.HTTP_400_BAD_REQUEST)
        product.status = STATUS_CHOICES[2][0]
        product.save()
        return Response({'status': 'success', 'data': 'Product deleted successfully'}, status=status.HTTP_200_OK)