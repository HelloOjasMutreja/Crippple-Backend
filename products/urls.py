from django.urls import path
from .views import search_apparel, google_shopping_search

urlpatterns = [
    path("search/", search_apparel, name="search_apparel"),
    path("google-shopping/", google_shopping_search, name="google_shopping_search"),  # Legacy endpoint
]
