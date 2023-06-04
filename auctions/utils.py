from django.urls import reverse_lazy

from .models import Auction, Category
from django.contrib.auth.mixins import LoginRequiredMixin


class DataMixin:
    model = Auction
    template_name = 'auctions/index.html'
    context_object_name = 'auctions'
    paginate_by = 6

    def get_user_context(self, **kwargs):
        context = kwargs
        categories = Category.objects.all()
        context['categories'] = categories
        return context


class LoginMixin(LoginRequiredMixin):
    login_url = reverse_lazy('login')
