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
    product = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'children', 'product', 'status', 'status_text', 'created_at', 'updated_at']

    def get_children(self, obj):
        return CategorySerializer(obj.children.filter(status = STATUS_CHOICES[1][0]), many=True, context=self.context).data
    
    def get_status_text(self, obj):
        return STATUS_CHOICES[obj.status][1]
        
    def get_product(self, obj):
        return ProductSerializer(obj.product_category.filter(status = STATUS_CHOICES[1][0]), many=True, context=self.context).data
    
# class ProductSerializer(serializers.ModelSerializer):
#     category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.filter(status = STATUS_CHOICES[1][0]), required=True)

#     class Meta:
#         model = Product
#         fields = ['id', 'name', 'brand', 'category', 'price', 'stock', 'description', 'created_at', 'updated_at']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'status', 'created_at', 'updated_at']
        extra_kwargs = {'product': {'read_only': True}}  # product is auto-linked


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.filter(status=STATUS_CHOICES[1][0]), required=True)
    
    # Override the images field to filter by status=1
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'brand', 'category', 'price', 'offer_price', 'stock', 'description', 'status', 'created_at', 'updated_at', 'images']

    def get_images(self, instance):
        # Only return images where status is 1 (active)
        active_images = instance.productimage_set.filter(status=STATUS_CHOICES[1][0])
        return ProductImageSerializer(active_images, many=True).data

    def validate(self, data):
        """
        Ensure the product offer price is valid and at least one image is provided on create.
        """
        # Ensure offer price is less than or equal to price
        if 'offer_price' not in data or data['offer_price'] is None:
            data['offer_price'] = data.get('price')  # Default to price if offer_price is not provided
        
        if data['offer_price'] > data['price']:
            raise serializers.ValidationError({"offer_price": "Offer price cannot be greater than the actual price."})

        # Check if images are provided during creation
        if self.instance is None:  # This is a create operation, not update
            images_data = self.initial_data.get('images')
            if not images_data or len(images_data) == 0:
                raise serializers.ValidationError({"images": "At least one product image must be provided."})

        return data

    def create(self, validated_data):
        """
        Create product along with its images.
        """
        images_data = validated_data.pop('images', None)  # Extract images data

        # Call the default create method to create the product
        product = super().create(validated_data)

        # Add custom logic to handle product images
        if images_data:
            for image_data in images_data:
                ProductImage.objects.create(product=product, **image_data)

        return product

    def update(self, instance, validated_data):
        """
        Update product along with its images.
        """
        images_data = validated_data.pop('images', None)  # Extract images data

        # Call the default update method to update the product fields
        product = super().update(instance, validated_data)

        # Add custom logic to handle updating product images
        if images_data:
            for image_data in images_data:
                ProductImage.objects.create(product=product, **image_data)

        return product
