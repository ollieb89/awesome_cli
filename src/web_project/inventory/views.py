from django.views.generic import TemplateView, ListView, DetailView
from django.db.models import Count
from .models import Item

class HomeView(TemplateView):
    template_name = "inventory/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_items'] = Item.objects.count()
        context['active_items'] = Item.objects.filter(status='active').count()
        context['recent_items'] = Item.objects.order_by('-created_at')[:5]
        return context

class ItemListView(ListView):
    model = Item
    context_object_name = 'items'
    template_name = "inventory/item_list.html"

class ItemDetailView(DetailView):
    model = Item
    context_object_name = 'item'
    template_name = "inventory/item_detail.html"
