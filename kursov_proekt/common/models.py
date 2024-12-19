from django.db import models

from kursov_proekt.accounts.models import CustomBaseUser
from kursov_proekt.product.models import Product


# Create your models here.
class Wishlist(models.Model):
    user = models.ForeignKey(
        CustomBaseUser,  # Променете с вашия модел на потребителя
        on_delete=models.CASCADE,
        related_name="wishlists",  # Това позволява да имате достъп до wishlist-ите на потребителя чрез 'user.wishlists'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist for {self.user.username}"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(
        Wishlist,  # Референция към Wishlist модел
        on_delete=models.CASCADE,
        related_name="items",  # Възможност за достъп до всички items чрез 'wishlist.items'
    )
    product = models.ForeignKey(
        Product,  # Референция към Product модел
        on_delete=models.CASCADE,
        related_name="wishlist_items",  # Възможност за достъп до всички wishlist items чрез 'product.wishlist_items'
    )
    added_at = models.DateTimeField(auto_now_add=True)  # Кога продуктът е добавен в wishlist

    def __str__(self):
        return f"{self.product.name} in {self.wishlist.user.username}'s wishlist"


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    message = models.TextField()

    def __str__(self):
        return f"Contact from {self.name}"