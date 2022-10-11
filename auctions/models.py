from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    def __str__(self):
        return f'{self.username}'


class Category(models.Model):
    category_name = models.CharField(max_length=50, db_index=True)

    def __str__(self):
        return f'{self.category_name}'


class Auction(models.Model):
    title = models.CharField(max_length=140)
    description = models.TextField(max_length=900, null=True)
    author = models.ForeignKey(User, models.PROTECT, related_name='auctions')
    starting_bid = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0.01)])
    current_bid = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0.01)], blank=True,
                                      null=True)
    image = models.ImageField(upload_to='images/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categories')
    active = models.BooleanField(default=True)
    created = models.DateTimeField(default=timezone.now)
    watchers = models.ManyToManyField(User, related_name='watchlist', blank=True)
    buyer = models.ForeignKey(User, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f'Auction "{self.title}" by {self.author}'


class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f'Bid {self.amount} on {self.auction.title} by {self.user.username}'


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='get_comments')
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'Comment by {self.user} on {self.auction}'
