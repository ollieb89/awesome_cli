from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Item
from .serializers import ItemSerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'name']
    search_fields = ['name', 'description']
    # Permission is inherited from defaults (IsAuthenticated), so we don't need to override unless we want specific access.
    # For this exercise, we'll keep it standard.
