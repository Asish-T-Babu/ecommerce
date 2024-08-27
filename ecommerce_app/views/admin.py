from rest_framework import generics, status
from rest_framework.response import Response

from ecommerce_app.models.admin import Brand
from ecommerce_app.serializers.admin import BrandSerializer
from ecommerce_app.utils import STATUS_CHOICES

class BrandListCreateView(generics.ListCreateAPIView):
    queryset = Brand.objects.filter(status=STATUS_CHOICES[1][0])
    serializer_class = BrandSerializer

class BrandRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Brand.objects.filter(status=STATUS_CHOICES[1][0])
    serializer_class = BrandSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = STATUS_CHOICES[2][0]
        instance.save()
        return Response(status=status.HTTP_200_OK)
