from django.urls import path
from .views import ProductsAPIView

urlpatterns = [
    path('get-products/', ProductsAPIView.as_view(), name='get-products'),
]
