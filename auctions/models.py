from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    category_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.category_name}"

class Auction(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="listings")
    starting_bid = models.FloatField()
    image = models.URLField(blank=True, null=True)
    active = models.BooleanField(default=True)
    watchlist = models.ManyToManyField(User, blank=True, related_name="watchlist")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (by {self.owner.username})"

class Bids(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()

class Comments(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='comments')
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField()

