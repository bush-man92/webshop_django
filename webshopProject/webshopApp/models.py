from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.

"modeli za bazu podataka"

class Item(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField(
        default = 0
    )
    about = models.TextField(blank=True)
    photo = models.ImageField(upload_to='')
    photo_link =  models.URLField(
        max_length=128,
        blank=True
    )

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(
        default = 0
    )

class Purchase(models.Model):

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    address = models.CharField(max_length=100)
    total_price = models.IntegerField(
        default = 0
    )
    credit_card = models.CharField(
        max_length=50,
        default=""
    )
    security_number = models.IntegerField(
        default=3
    )
    paying = models.CharField(
        max_length=4,
        default=""
    )
    delivery = models.CharField(
        max_length=4,
        default=""
    )

class Comment(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    username = models.CharField(
        max_length=50,
        default="AnonymousUser")
    comment = models.CharField(max_length=500)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.now, blank=True)