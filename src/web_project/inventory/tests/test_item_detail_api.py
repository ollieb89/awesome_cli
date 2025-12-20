from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from inventory.models import Item
import json

class ItemDetailApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.item = Item.objects.create(
            name="Test Item",
            description="A description",
            status="active"
        )

        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)

    def test_get_item_detail(self):
        """
        Verify that GET /api/items/<id>/ returns the correct data structure,
        including the status_display field.
        """
        # Note: Testing the non-versioned path as per migration requirement
        response = self.client.get(f'/api/items/{self.item.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content)

        self.assertIn('data', content)
        data = content['data']

        self.assertEqual(data['id'], self.item.id)
        self.assertEqual(data['name'], "Test Item")
        self.assertEqual(data['description'], "A description")
        self.assertEqual(data['status'], "active")
        self.assertEqual(data['status_display'], "Active")
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)

    def test_get_item_detail_v1(self):
        """
        Verify that GET /api/v1/items/<id>/ also works (standard path).
        """
        response = self.client.get(f'/api/v1/items/{self.item.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
