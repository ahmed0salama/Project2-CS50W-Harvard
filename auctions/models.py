from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Auction(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField()
    category = models.CharField()
    starting_bid = models.FloatField()
    image = models.URLField(blank=True, null=True)
    active = models.BooleanField(default=True)
    watchlist = models.ManyToManyField(User, blank=True, related_name="watchlist")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    create_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} (by {self.owner.username})"

class Bids(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()

class Comments(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField()

