from django.core.management.base import BaseCommand
from inventory.models import Item

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **options):
        items = [
            {'name': 'Project Alpha', 'description': 'Initial phase of the project', 'status': 'active'},
            {'name': 'Project Beta', 'description': 'Secondary phase', 'status': 'draft'},
            {'name': 'Project Gamma', 'description': 'Legacy system', 'status': 'archived'},
            {'name': 'Project Delta', 'description': 'New initiative', 'status': 'active'},
            {'name': 'Project Epsilon', 'description': 'Exploratory research', 'status': 'draft'},
        ]

        for item_data in items:
            Item.objects.get_or_create(**item_data)

        self.stdout.write(self.style.SUCCESS('Successfully populated database'))
