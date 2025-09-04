from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer

# Create your views here.

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by('-last_updated')
    serializer_class = ProductSerializer
