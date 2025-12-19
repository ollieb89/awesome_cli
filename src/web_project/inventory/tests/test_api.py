from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from inventory.models import Item

class ItemApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.item = Item.objects.create(name="Test Item", status="active")

        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)

    def test_delete_item(self):
        # Verify DELETE returns 204 and empty body (no renderer envelope)
        response = self.client.delete(f'/api/v1/items/{self.item.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(response.content) # Should be empty

    def test_get_items_structure(self):
        response = self.client.get('/api/v1/items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # We must decode the response content because the renderer wraps the data
        # response.data is the raw data before the renderer runs.
        import json
        content = json.loads(response.content)

        self.assertIn('data', content)
        self.assertIn('meta', content)
        self.assertIn('errors', content)
        self.assertEqual(len(content['data']), 1)
        self.assertEqual(content['data'][0]['name'], "Test Item")

    def test_filtering(self):
        # Create another item with different status
        Item.objects.create(name="Archived Item", status="archived")

        # Filter for active
        response = self.client.get('/api/v1/items/?status=active')
        import json
        content = json.loads(response.content)

        self.assertEqual(len(content['data']), 1)
        self.assertEqual(content['data'][0]['status'], 'active')

        # Filter for archived
        response = self.client.get('/api/v1/items/?status=archived')
        content = json.loads(response.content)
        self.assertEqual(len(content['data']), 1)
        self.assertEqual(content['data'][0]['status'], 'archived')

    def test_schema_endpoint(self):
        response = self.client.get('/api/v1/schema/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
