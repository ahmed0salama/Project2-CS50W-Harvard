from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create/', views.create_listing, name="create"),
    path("listing/<int:listing_id>", views.listing_page, name="listing"),
    path("listing/<int:listing_id>/watchlist", views.toggle_watchlist, name="watchlist_toggle"),
    path("listing/<int:listing_id>/bid", views.place_bid, name="place_bid"),
    path("listing/<int:listing_id>/close", views.close_auction, name="close_auction"),
    path("listing/<int:listing_id>/comment", views.add_comment, name="add_comment"),
]
