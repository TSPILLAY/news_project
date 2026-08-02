from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    
    Supports three distinct user roles: Reader, Editor, and Journalist.
    Tracks subscribed publishers and journalists for Reader accounts.
    """
    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('editor', 'Editor'),
        ('journalist', 'Journalist'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='reader')

    subscribed_publishers = models.ManyToManyField(
        'Publisher', blank=True, related_name='reader_subscribers'
    )
    subscribed_journalists = models.ManyToManyField(
        'self', symmetrical=False, blank=True, related_name='journalist_subscribers'
    )

    def save(self, *args, **kwargs):
        """
        Override standard save behavior.
        Clears publisher and journalist subscriptions if role is non-reader.
        """
        super().save(*args, **kwargs)
        if self.role != 'reader':
            self.subscribed_publishers.clear()
            self.subscribed_journalists.clear()


class Publisher(models.Model):
    """Represents a publishing organization employing editors and journalists."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    editors = models.ManyToManyField(
        CustomUser, related_name='publisher_editors', limit_choices_to={'role': 'editor'}
    )
    journalists = models.ManyToManyField(
        CustomUser, related_name='publisher_journalists', limit_choices_to={'role': 'journalist'}
    )

    def __str__(self):
        return self.name


class Article(models.Model):
    """Represents a news article written by a journalist."""
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='articles', limit_choices_to={'role': 'journalist'}
    )
    publisher = models.ForeignKey(
        Publisher, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles'
    )
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    """Represents a newsletter curated by a journalist, containing multiple articles."""
    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='newsletters', limit_choices_to={'role': 'journalist'}
    )
    articles = models.ManyToManyField(Article, related_name='newsletters')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    