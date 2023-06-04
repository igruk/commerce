from decimal import Decimal

from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, FormView
from django.contrib import messages

# from .service import send
# from .tasks import send_email
from .utils import DataMixin, LoginMixin
from .models import User, Auction, Bid, Comment
from .forms import CommentForm, BidForm, AuctionForm


class AuctionsHome(DataMixin, ListView):
    """View for the home page displaying a list of active auctions."""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Auctions')
        context.update(c_def)
        return context

    def get_queryset(self):
        return Auction.objects.filter(active=True)


class MyLoginView(LoginView):
    """View function for user login."""
    template_name = 'auctions/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('index')

    def form_invalid(self, form):
        return render(
            self.request,
            self.template_name,
            {'form': form, 'message': 'Invalid username or password.'}
        )


class MyLogoutView(LoginMixin, LogoutView):
    """View function for user logout."""
    next_page = reverse_lazy('index')


def register(request):
    """View function for user register."""
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']

        # Ensure password matches confirmation
        password = request.POST['password']
        confirmation = request.POST['confirmation']
        if password != confirmation:
            return render(request, 'auctions/register.html', {
                'message': 'Passwords must match.',
                'title': 'Register'
            })
        if not username or not password or not email:
            return render(request, 'auctions/register.html', {
                'message': 'Form is not valid.',
                'title': 'Register'
            })
        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            login(request, user)
        except IntegrityError:
            return render(request, 'auctions/register.html', {
                'message': 'Username already taken.',
                'title': 'Register'
            })
        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, 'auctions/register.html', {
            'title': 'Register'
        })


class AuctionPage(DetailView):
    """View for displaying details of an auction."""
    model = Auction
    template_name = 'auctions/auction.html'
    pk_url_kwarg = 'auction_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bid_form'] = BidForm()
        context['comment_form'] = CommentForm()
        context['comments'] = self.object.get_comments.all

        if self.request.user.is_authenticated:
            if self.object in self.request.user.watchlist.all():
                self.object.is_watched = True
            else:
                self.object.is_watched = False
        return context

    def get_queryset(self):
        return Auction.objects.all().select_related('author', 'category', 'buyer')


class NewAuction(LoginMixin, CreateView):
    """View for creating a new auction."""
    form_class = AuctionForm
    template_name = 'auctions/new.html'

    def form_valid(self, form):
        new_auction = form.save(commit=False)
        new_auction.author = self.request.user
        return super().form_valid(form)


class AuctionCategory(DataMixin, ListView):
    """View for displaying a list of auctions in a specific category."""
    allow_empty = False

    def get_queryset(self):
        return Auction.objects.filter(category__category_name=self.kwargs['category_name'], active=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        name = self.kwargs['category_name']
        c_def = self.get_user_context(title=name, h2_title=name)
        context.update(c_def)
        return context


class AuctionWatchlist(LoginMixin, DataMixin, ListView):
    """View for displaying the user's watchlist."""

    def get_queryset(self):
        return self.request.user.watchlist.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Watchlist', h2_title='Watchlist')
        context.update(c_def)
        return context


class Purchases(LoginMixin, DataMixin, ListView):
    """View for displaying a list of auctions that user won."""

    def get_queryset(self):
        return Auction.objects.filter(buyer=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Purchases', h2_title='Purchases')
        context.update(c_def)
        return context


class WatchlistEdit(LoginMixin, View):
    """View for adding/removing an auction from the user's watchlist."""

    def get(self, request, auction_id):
        auction = Auction.objects.get(id=auction_id)

        if request.user in auction.watchers.all():
            auction.watchers.remove(request.user)
            auction.is_watched = False
        else:
            auction.watchers.add(request.user)
            auction.is_watched = True

        return HttpResponseRedirect(reverse('auction', args=[auction_id]))


class AuctionBid(LoginMixin, FormView):
    """View for placing a bid on an auction."""
    form_class = BidForm
    template_name = 'auctions/bid.html'

    def form_valid(self, form):
        auction_id = self.kwargs['auction_id']
        auction = get_object_or_404(Auction, id=auction_id)
        amount = Decimal(form.cleaned_data['amount'])

        if amount >= auction.starting_bid and (auction.current_bid is None or amount > auction.current_bid):
            auction.current_bid = amount
            new_bid = form.save(commit=False)
            new_bid.auction = auction
            new_bid.user = self.request.user
            if self.request.user not in auction.watchers.all():
                auction.watchers.add(self.request.user)
            new_bid.save()
            auction.save()

            return HttpResponseRedirect(reverse('auction', args=[auction_id]))
        else:
            messages.error(self.request, 'Your bid must be greater than the current price.')
            return HttpResponseRedirect(reverse('auction', args=[auction_id]))


class AuctionClose(LoginMixin, View):
    """View for closing an auction."""

    def get(self, request, auction_id):
        auction = get_object_or_404(Auction, id=auction_id)

        if request.user == auction.author:
            auction.active = False
            if auction.current_bid:
                auction.buyer = Bid.objects.filter(auction=auction).last().user
            auction.save()
            # send(auction.buyer.email)
            # send_email.delay(auction.buyer.email)
            return HttpResponseRedirect(reverse('auction', args=[auction_id]))
        else:
            return HttpResponseForbidden()


class CommentCreate(LoginMixin, CreateView):
    """View for adding a comment to an auction."""
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        auction_id = self.kwargs['auction_id']
        auction = Auction.objects.get(id=auction_id)
        form.instance.user = self.request.user
        form.instance.auction = auction
        return super().form_valid(form)

    def get_success_url(self):
        auction_id = self.kwargs['auction_id']
        return reverse('auction', args=[auction_id])


class AuctionSearch(DataMixin, ListView):
    """View for searching auctions based on a query."""
    paginate_by = None

    def get_queryset(self):
        query = self.request.GET.get('q')
        return Auction.objects.filter(title__icontains=query, active=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Search Results', h2_title='Search Results')
        return dict(list(context.items()) + list(c_def.items()))
