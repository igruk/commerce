from django.urls import path

from .views import *

urlpatterns = [
    path("", AuctionsHome.as_view(), name="index"),
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path("register", register, name="register"),
    path("new", new, name="new"),
    path("categories/<str:category_name>", AuctionCategory.as_view(), name="category_view"),
    path("auction/<str:auction_id>", auction_page, name="auction"),
    path('auction/<str:auction_id>/bid', auction_bid, name='auction_bid'),
    path('auction/<str:auction_id>/close', auction_close, name='auction_close'),
    path("watchlist", AuctionWatchlist.as_view(), name="watchlist"),
    path("watchlist/<int:auction_id>/edit/<str:reverse_method>", watchlist_edit, name='watchlist_edit'),
    path('auction/<str:auction_id>/comment', comment, name='comment'),
    path("search", search, name="search"),
]
