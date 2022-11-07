from .models import *


class DataMixin:
    model = Auction
    template_name = 'auctions/index.html'
    context_object_name = 'auctions'
    paginate_by = 3

    def get_user_context(self, **kwargs):
        context = kwargs
        categories = Category.objects.all()
        context['categories'] = categories
        return context
