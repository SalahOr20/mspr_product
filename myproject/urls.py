from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
import django_prometheus

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="Documentation de l'API pour la gestion des produits",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    urlconf='products.urls',  # Make sure to set your project's URLconf
)



urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('products.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('metrics/', django_prometheus.exports.ExportToDjangoView, name='prometheus-django-metrics'),
]
