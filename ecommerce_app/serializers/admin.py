from rest_framework import serializers

from ecommerce_app.models.admin import *
from ecommerce_app.utils import STATUS_CHOICES

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description', 'status', 'created_at', 'updated_at']

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    status_text = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'children', 'status', 'status_text', 'created_at', 'updated_at']

    def get_children(self, obj):
        return CategorySerializer(obj.children.filter(status = STATUS_CHOICES[1][0]), many=True, context=self.context).data
    
    def get_status_text(self, obj):
        return STATUS_CHOICES[obj.status][1]
        
    
class ProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'brand', 'category', 'price', 'stock', 'description', 'created_at', 'updated_at']
