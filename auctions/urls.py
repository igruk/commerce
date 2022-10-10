from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.new, name="new"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category_name>", views.category_view, name="category_view"),
    path("auction/<str:auction_id>", views.auction_page, name="auction"),
    path('auction/<str:auction_id>/bid', views.auction_bid, name='auction_bid'),
    path('auction/<str:auction_id>/close', views.auction_close, name='auction_close'),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist/<int:auction_id>/edit/<str:reverse_method>", views.watchlist_edit, name='watchlist_edit'),
    path('auction/<str:auction_id>/comment', views.comment, name='comment'),
]
