from django.urls import path
from .views import (
    ProductListCreate, ProductRetrieveUpdateDestroy,
    get_product_stock, update_product_stock, get_low_stock_products
)

urlpatterns = [
    # Routes CRUD standard
    path('products/', ProductListCreate.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroy.as_view(), name='product-detail'),
    
    # Routes pour la gestion des stocks
    path('products/<int:product_id>/stock/', get_product_stock, name='product-stock'),
    path('products/<int:product_id>/stock/update/', update_product_stock, name='update-product-stock'),
    path('products/low-stock/', get_low_stock_products, name='low-stock-products'),
]
