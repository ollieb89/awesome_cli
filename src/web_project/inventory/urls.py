from django.urls import path
from .views import HomeView, ItemListView, ItemDetailView

app_name = 'inventory'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('items/', ItemListView.as_view(), name='item_list'),
    path('items/<int:pk>/', ItemDetailView.as_view(), name='item_detail'),
]
