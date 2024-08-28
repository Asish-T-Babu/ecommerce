from rest_framework import generics, status
from rest_framework.response import Response

from ecommerce_app.models.admin import Brand, Category
from ecommerce_app.serializers.admin import BrandSerializer, CategorySerializer
from ecommerce_app.utils import STATUS_CHOICES

# Brand API's
class BrandListCreateView(generics.ListCreateAPIView):
    queryset = Brand.objects.filter(status=STATUS_CHOICES[1][0])
    serializer_class = BrandSerializer

    def list(self, request, *args, **kwargs):
        """
        Get All Brands
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    
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
    queryset = Category.objects.filter(status=STATUS_CHOICES[1][0])
    serializer_class = CategorySerializer

    def get(self, request, *args, **kwargs):
        """
        Get All Categories
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'status': 'success', 'data': serializer.data}, status= status.HTTP_200_OK)

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