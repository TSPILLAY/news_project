import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Article


@receiver(post_save, sender=Article)
def on_article_approved(sender, instance, created, **kwargs):
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
                "http://127.0.0.1:8000/api/approved-log/",
                json={
                    "article_id": instance.id,
                    "title": instance.title,
                    "author": instance.author.username
                },
                timeout=2
            )
        except Exception:
            pass
