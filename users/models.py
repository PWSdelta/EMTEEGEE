from django.contrib.auth.models import User
from django.db import models
from cards.models import Card


# Use Django's built-in User model for now
# Custom User model can be added later if needed


class UserFavorite(models.Model):
    """
    User's favorite cards.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'card']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.card.name}"


class UserCollection(models.Model):
    """
    User's card collections/decks.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class CollectionItem(models.Model):
    """
    Cards in a user's collection.
    """
    collection = models.ForeignKey(UserCollection, on_delete=models.CASCADE, related_name='items')
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True)
    
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['collection', 'card']
    
    def __str__(self):
        return f"{self.collection.name} - {self.card.name} (x{self.quantity})"
