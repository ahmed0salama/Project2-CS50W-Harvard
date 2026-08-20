from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import CreateListingForm
from .models import User, Auction, Bids, Comments, Category


def isCurrentUserBid(request, listing_id):
    listing = Auction.objects.get(pk=listing_id)
    try:
        current_bid_user = True if listing.bids.all().order_by('-amount').first().user == request.user else False
    except:
        current_bid_user=False
    return current_bid_user


def index(request):
    active_listings = Auction.objects.filter(active=True)
    
    listings_data = []
    for listing in active_listings:
        highest_bid = listing.bids.order_by('-amount').first()
        current_price = highest_bid.amount if highest_bid else listing.starting_bid
        listings_data.append({
            'auction': listing,
            'current_price': current_price
        })

    return render(request, "auctions/index.html", {
        "listings_data": listings_data
    })


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
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = CreateListingForm()

    return render(request, "auctions/create_listing.html", {
        "form": form
    })

def listing_page(request, listing_id):
    listing = Auction.objects.get(pk=listing_id)
    bids = listing.bids.all().order_by('-amount')
    highest_bid = bids.first()
    current_price = highest_bid.amount if highest_bid else listing.starting_bid
    
    is_in_watchlist = False
    if request.user.is_authenticated:
        is_in_watchlist = listing.watchlist.filter(id=request.user.id).exists()

    is_winner = False
    if not listing.active and highest_bid and request.user == highest_bid.user:
        is_winner = True

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "current_price": current_price,
        "highest_bid": highest_bid,
        "bids_count": bids.count(),
        "is_in_watchlist": is_in_watchlist,
        "is_winner": is_winner,
        "comments": listing.comments.all(),
        'current_bid_user': isCurrentUserBid(request, listing_id)
    })

@login_required
def toggle_watchlist(request, listing_id):
    listing = Auction.objects.get(pk=listing_id)
    if listing.watchlist.filter(id=request.user.id).exists():
        listing.watchlist.remove(request.user)
    else:
        listing.watchlist.add(request.user)
    return redirect("listing", listing_id=listing_id)

@login_required
def place_bid(request, listing_id):
    listing = Auction.objects.get(pk=listing_id)
    if request.method == "POST":
        try:
            bid_amount = float(request.POST.get("bid_amount"))
        except (ValueError, TypeError):
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "error_message": "Invalid bid amount.",
                "current_price": listing.bids.order_by('-amount').first().amount if listing.bids.exists() else listing.starting_bid,
                "comments": listing.comments.all(),
                'current_bid_user': isCurrentUserBid(request, listing_id)
            })

        highest_bid = listing.bids.order_by('-amount').first()
        current_price = highest_bid.amount if highest_bid else listing.starting_bid

        if (highest_bid and bid_amount <= current_price) or (not highest_bid and bid_amount < current_price):
            bids = listing.bids.all().order_by('-amount')
            is_in_watchlist = listing.watchlist.filter(id=request.user.id).exists()
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "error_message": "Your bid must be strictly higher than the current price / starting bid.",
                "current_price": current_price,
                "highest_bid": highest_bid,
                "bids_count": bids.count(),
                "is_in_watchlist": is_in_watchlist,
                "comments": listing.comments.all(),
                'current_bid_user': isCurrentUserBid(request, listing_id)
            })

        Bids.objects.create(amount=bid_amount, user=request.user, auction=listing)
        return redirect("listing", listing_id=listing_id)

@login_required
def close_auction(request, listing_id):
    listing = Auction.objects.get(pk=listing_id)
    if request.user == listing.owner:
        listing.active = False
        listing.save()
    return redirect("listing", listing_id=listing_id)

@login_required
def add_comment(request, listing_id):
    listing = Auction.objects.get(pk=listing_id)
    if request.method == "POST":
        message = request.POST.get("message")
        if message:
            Comments.objects.create(commenter=request.user, auction=listing, comment=message)
    return redirect("listing", listing_id=listing_id)

@login_required
def watchlist_page(request):
    watchlist_items = request.user.watchlist.all()
    
    listings_data = []
    for listing in watchlist_items:
        highest_bid = listing.bids.order_by('-amount').first()
        current_price = highest_bid.amount if highest_bid else listing.starting_bid
        listings_data.append({
            'listing': listing,
            'current_price': current_price
        })

    return render(request, "auctions/watchlist.html", {
        "listings_data": listings_data
    })

def categories_list(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category_listings(request, category_id):
    category = Category.objects.get(pk=category_id)
    active_listings = Auction.objects.filter(category=category, active=True)
    
    listings_data = []
    for listing in active_listings:
        highest_bid = listing.bids.order_by('-amount').first()
        current_price = highest_bid.amount if highest_bid else listing.starting_bid
        listings_data.append({
            'listing': listing,
            'current_price': current_price
        })

    return render(request, "auctions/category_listings.html", {
        "category": category,
        "listings_data": listings_data
    })
