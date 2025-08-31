from rest_framework import serializers
from .models import Product
# from .service_product import publish_products
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

# publish_products()