from django.core.cache import cache

from .models import *


class DataMixin:
    model = Auction
    template_name = 'auctions/index.html'
    context_object_name = 'auctions'
    paginate_by = 6

    def get_user_context(self, **kwargs):
        context = kwargs
        categories = cache.get('categories')
        if not categories:
            categories = Category.objects.all()
            cache.set('categories', categories, 60)
        context['categories'] = categories
        return context
