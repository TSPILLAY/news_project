"""
Admin configuration module registering core models into Django Admin interface[cite: 1].
"""

from django.contrib import admin
from .models import CustomUser, Publisher, Article, Newsletter

admin.site.register(CustomUser)
admin.site.register(Publisher)
admin.site.register(Article)
admin.site.register(Newsletter)