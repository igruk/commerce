from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages

# from .service import send
# from .tasks import send_email
from .utils import DataMixin, LoginMixin
from .models import User, Auction, Bid
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


def login_view(request):
    """View function for user login."""
    if request.method == 'POST':

        # Attempt to sign user in
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'auctions/login.html', {
                'message': 'Invalid username and/or password.',
                'title': 'Log in'
            })
    else:
        return render(request, 'auctions/login.html', {
            'title': 'Log in'
        })


def logout_view(request):
    """View function for user logout."""
    logout(request)
    return HttpResponseRedirect(reverse('index'))


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


@login_required
def watchlist_edit(request, auction_id):
    """View for adding/removing an auction from the user's watchlist."""
    auction = Auction.objects.get(id=auction_id)

    if request.user in auction.watchers.all():
        auction.watchers.remove(request.user)
        auction.is_watched = False
    else:
        auction.watchers.add(request.user)
        auction.is_watched = True

    return HttpResponseRedirect(reverse('auction', args=[auction_id]))


@login_required
def auction_bid(request, auction_id):
    """View for placing a bid on an auction."""
    auction = Auction.objects.get(id=auction_id)
    amount = Decimal(request.POST['amount'])

    if amount >= auction.starting_bid and (auction.current_bid is None or amount > auction.current_bid):
        auction.current_bid = amount
        form = BidForm(request.POST)
        new_bid = form.save(commit=False)
        new_bid.auction = auction
        new_bid.user = request.user
        if request.user not in auction.watchers.all():
            auction.watchers.add(request.user)
        new_bid.save()
        auction.save()

        return HttpResponseRedirect(reverse('auction', args=[auction_id]))
    else:
        messages.error(request, 'Your bid must be greater than current price.')
        return HttpResponseRedirect(reverse('auction', args=[auction_id]))


@login_required
def auction_close(request, auction_id):
    """View for closing an auction."""
    auction = Auction.objects.get(id=auction_id)

    if request.user == auction.author:
        auction.active = False
        if auction.current_bid:
            auction.buyer = Bid.objects.filter(auction=auction).last().user
        auction.save()
        # send(auction.buyer.email)
        # send_email.delay(auction.buyer.email)
        return HttpResponseRedirect(reverse('auction', args=[auction_id]))
    else:
        auction.watchers.add(request.user)
        return HttpResponseRedirect(reverse('watchlist'))


@login_required
def comment(request, auction_id):
    """View for adding a comment to an auction."""
    auction = Auction.objects.get(id=auction_id)
    form = CommentForm(request.POST)
    new_comment = form.save(commit=False)
    new_comment.user = request.user
    new_comment.auction = auction
    new_comment.save()
    return HttpResponseRedirect(reverse('auction', args=[auction_id]))


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
