from django.urls import path
from .views import google_shopping_search

urlpatterns = [
    path("search/", google_shopping_search, name="google_shopping_search"),
]
