from rest_framework import serializers
from .models import CustomUser, Publisher, Article, Newsletter


class UserSerializer(serializers.ModelSerializer):
    """Serializer for CustomUser model representation."""

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']


class PublisherSerializer(serializers.ModelSerializer):
    """Serializer for Publisher organization details."""

    class Meta:
        model = Publisher
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for news articles."""

    class Meta:
        model = Article
        fields = '__all__'


class NewsletterSerializer(serializers.ModelSerializer):
    """Serializer for curated newsletters."""

    class Meta:
        model = Newsletter
        fields = '__all__'
