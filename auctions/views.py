from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView

from .forms import *
from .models import User, Category, Auction


class AuctionsHome(ListView):
    model = Auction
    template_name = 'auctions/index.html'
    context_object_name = 'auctions'
    extra_context = {
        'title': 'Active Listings'
    }

    def get_queryset(self):
        return Auction.objects.filter(active=True)


# def index(request):
#     return render(request, "auctions/index.html", {
#         'auctions': Auction.objects.filter(active=True),
#         'title': 'Active Listings'
#     })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password.",
                'title': 'Log in'
            })
    else:
        return render(request, "auctions/login.html", {
            'title': 'Log in'
        })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match.",
                'title': 'Register'
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken.",
                'title': 'Register'
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html", {
            'title': 'Register'
        })


class NewAuction(CreateView):
    form_class = AuctionForm
    template_name = 'auctions/new.html'

    def form_valid(self, form):
        new_auction = form.save(commit=False)
        new_auction.author = self.request.user
        return super().form_valid(form)


# @login_required
# def new(request):
#     if request.method == 'POST':
#         form = AuctionForm(request.POST, request.FILES)
#         if form.is_valid():
#             new_auction = form.save(commit=False)
#             new_auction.author = request.user
#             form.save()
#
#             auction = Auction.objects.latest('id')
#             return render(request, 'auctions/auction.html', {
#                 'auction': auction,
#             })
#         else:
#             return render(request, "auctions/new.html", {
#                 'message': 'Not valid data',
#                 'form': AuctionForm(),
#             })
#     else:
#         return render(request, "auctions/new.html", {
#             'form': AuctionForm(),
#         })


# def auction_page(request, auction_id):
#     auction = Auction.objects.get(id=auction_id)
#
#     if request.user in auction.watchers.all():
#         auction.is_watched = True
#     else:
#         auction.is_watched = False
#
#     return render(request, 'auctions/auction.html', {
#         'auction': auction,
#         'bid_form': BidForm(),
#         'comments': auction.get_comments.all(),
#         'comment_form': CommentForm(),
#     })


class AuctionPage(DetailView):
    model = Auction
    template_name = 'auctions/auction.html'
    pk_url_kwarg = 'auction_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object in self.request.user.watchlist.all():
            self.object.is_watched = True
        else:
            self.object.is_watched = False
        return context


@login_required
def auction_bid(request, auction_id):
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
        return render(request, 'auctions/auction.html', {
            'auction': auction,
            'bid_form': BidForm,
            'error_min_value': True,
        })


class AuctionCategory(ListView):
    model = Auction
    template_name = 'auctions/index.html'
    context_object_name = 'auctions'
    allow_empty = False

    def get_queryset(self):
        return Auction.objects.filter(category__category_name=self.kwargs['category_name'], active=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = str(context['auctions'][0].category)
        return context


# def category_view(request, category_name):
#     category = Category.objects.get(category_name=category_name)
#     auctions = Auction.objects.filter(category=category, active=True)
#
#     return render(request, "auctions/index.html", {
#         'auctions': auctions,
#         'title': category_name,
#     })


# @login_required
# def watchlist(request):
#     auctions = request.user.watchlist.all()
#
#     return render(request, "auctions/index.html", {
#         'auctions': auctions,
#         'title': 'Watchlist',
#     })


class AuctionWatchlist(ListView):
    model = Auction
    template_name = 'auctions/index.html'
    context_object_name = 'auctions'
    allow_empty = False

    def get_queryset(self):
        return self.request.user.watchlist.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Watchlist'
        return context


@login_required
def watchlist_edit(request, auction_id, reverse_method):
    auction = Auction.objects.get(id=auction_id)

    if request.user in auction.watchers.all():
        auction.watchers.remove(request.user)
    else:
        auction.watchers.add(request.user)

    if reverse_method == 'auction':
        return auction_page(request, auction_id)
    else:
        return HttpResponseRedirect(reverse(reverse_method))


@login_required
def auction_close(request, auction_id):
    auction = Auction.objects.get(id=auction_id)

    if request.user == auction.author:
        auction.active = False
        if auction.current_bid:
            auction.buyer = Bid.objects.filter(auction=auction).last().user
        auction.save()
        return HttpResponseRedirect(reverse('auction', args=[auction_id]))
    else:
        auction.watchers.add(request.user)
        return HttpResponseRedirect(reverse('watchlist'))


@login_required
def comment(request, auction_id):
    auction = Auction.objects.get(id=auction_id)
    form = CommentForm(request.POST)
    new_comment = form.save(commit=False)
    new_comment.user = request.user
    new_comment.auction = auction
    new_comment.save()
    return HttpResponseRedirect(reverse('auction', args=[auction_id]))


def search(request):
    query = request.GET.get('q')
    auctions = Auction.objects.filter(title__icontains=query)
    print(auctions)

    return render(request, "auctions/index.html", {
        'auctions': auctions,
        'title': 'Search Results'
    })
