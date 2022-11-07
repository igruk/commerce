from django.urls import path

from .views import *

urlpatterns = [
    path('', AuctionsHome.as_view(), name='index'),
    path('login', login_view, name='login'),
    path('logout', logout_view, name='logout'),
    path('register', register, name='register'),
    path('new', NewAuction.as_view(), name='new'),
    path('search', AuctionSearch.as_view(), name='search'),
    path('purchases', Purchases.as_view(), name='purchases'),
    path('watchlist', AuctionWatchlist.as_view(), name='watchlist'),
    path('auction/<int:auction_id>/comment', comment, name='comment'),
    path('auction/<int:auction_id>/bid', auction_bid, name='auction_bid'),
    path('auction/<int:auction_id>', AuctionPage.as_view(), name='auction'),
    path('auction/<int:auction_id>/close', auction_close, name='auction_close'),
    path('watchlist/<int:auction_id>/watch', watchlist_edit, name='watchlist_edit'),
    path('categories/<str:category_name>', AuctionCategory.as_view(), name='category_view'),
]
