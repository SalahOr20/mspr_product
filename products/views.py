from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .models import Product
from .serializers import ProductSerializer
from .service_product import publish_product_created, publish_product_updated, publish_stock_updated


class ProductListCreate(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        product = serializer.save()
        # Publication de l'événement de création
        product_data = ProductSerializer(product).data
        publish_product_created(product_data)
        print(f"✅ Produit créé et événement publié: {product.name}")


class ProductRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def perform_update(self, serializer):
        old_stock = serializer.instance.stock if serializer.instance else 0
        product = serializer.save()
        
        # Publication de l'événement de mise à jour
        product_data = ProductSerializer(product).data
        publish_product_updated(product_data)
        
        # Si le stock a changé, publier un événement spécifique
        if old_stock != product.stock:
            publish_stock_updated(product.id, product.stock)
            print(f"✅ Stock mis à jour pour {product.name}: {old_stock} → {product.stock}")
        
        print(f"✅ Produit mis à jour et événement publié: {product.name}")

    def perform_destroy(self, instance):
        product_name = instance.name
        instance.delete()
        print(f"✅ Produit supprimé: {product_name}")


@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_stock(request, product_id):
    """Récupère le stock d'un produit spécifique"""
    try:
        product = Product.objects.get(id=product_id)
        return Response({
            'product_id': product.id,
            'name': product.name,
            'stock': product.stock,
            'available': product.stock > 0
        }, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({
            'message': f'Produit {product_id} non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH'])
@permission_classes([AllowAny])
def update_product_stock(request, product_id):
    """Met à jour le stock d'un produit"""
    try:
        product = Product.objects.get(id=product_id)
        new_stock = request.data.get('stock')
        
        if new_stock is None:
            return Response({
                'message': 'Le champ stock est requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if new_stock < 0:
            return Response({
                'message': 'Le stock ne peut pas être négatif'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        old_stock = product.stock
        product.stock = new_stock
        product.save()
        
        # Publication de l'événement de mise à jour de stock
        publish_stock_updated(product.id, new_stock)
        
        return Response({
            'message': 'Stock mis à jour avec succès',
            'product_id': product.id,
            'name': product.name,
            'old_stock': old_stock,
            'new_stock': new_stock
        }, status=status.HTTP_200_OK)
        
    except Product.DoesNotExist:
        return Response({
            'message': f'Produit {product_id} non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_low_stock_products(request):
    """Récupère les produits avec un stock faible (moins de 10 unités)"""
    try:
        threshold = request.query_params.get('threshold', 10)
        low_stock_products = Product.objects.filter(stock__lt=threshold)
        serializer = ProductSerializer(low_stock_products, many=True)
        
        return Response({
            'threshold': threshold,
            'count': len(low_stock_products),
            'products': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'message': f'Erreur lors de la récupération des produits: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
