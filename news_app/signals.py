"""
Signal handlers for news_app[cite: 2, 5].

Dispatches email notifications and triggers internal API callbacks
whenever an article reaches approved state[cite: 5].
"""

import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Article


@receiver(post_save, sender=Article)
def on_article_approved(sender, instance, created, **kwargs):
    """
    Signal receiver triggering upon Article save[cite: 5].
    
    When an article is approved, emails all readers subscribed to the article's
    publisher or author, and sends an HTTP POST notification to the internal API log[cite: 5].
    """
    if instance.approved:
        recipients = []
        if instance.publisher:
            subscribers = instance.publisher.reader_subscribers.all()
        else:
            subscribers = instance.author.journalist_subscribers.all()
        
        recipients = [user.email for user in subscribers if user.email]

        if recipients:
            send_mail(
                subject=f"New Approved Article: {instance.title}",
                message=instance.content,
                from_email="notifications@newsapp.com",
                recipient_list=recipients,
                fail_silently=True,
            )

        try:
            requests.post(
                "http://127.0.0.1:8000/api/approved/",
                json={
                    "article_id": instance.id,
                    "title": instance.title,
                    "author": instance.author.username
                },
                timeout=2
            )
        except Exception:
            pass
