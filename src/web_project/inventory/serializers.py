from rest_framework import serializers
from .models import Item

class ItemSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'status', 'status_display', 'created_at', 'updated_at']
