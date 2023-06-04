from django.urls import path

from . import views

urlpatterns = [
    path('', views.AuctionsHome.as_view(), name='index'),
    path('new', views.NewAuction.as_view(), name='new'),
    path('register', views.register, name='register'),
    path('login', views.MyLoginView.as_view(), name='login'),
    path('logout', views.MyLogoutView.as_view(), name='logout'),
    path('search', views.AuctionSearch.as_view(), name='search'),
    path('purchases', views.Purchases.as_view(), name='purchases'),
    path('watchlist', views.AuctionWatchlist.as_view(), name='watchlist'),
    path('auction/<int:auction_id>', views.AuctionPage.as_view(), name='auction'),
    path('auction/<int:auction_id>/bid', views.AuctionBid.as_view(), name='auction_bid'),
    path('auction/<int:auction_id>/comment', views.CommentCreate.as_view(), name='comment'),
    path('auction/<int:auction_id>/close', views.AuctionClose.as_view(), name='auction_close'),
    path('categories/<str:category_name>', views.AuctionCategory.as_view(), name='category_view'),
    path('watchlist/<int:auction_id>/watch', views.WatchlistEdit.as_view(), name='watchlist_edit'),
]
