from rest_framework import serializers
from .models import CustomUser, Publisher, Article, Newsletter


class UserSerializer(serializers.ModelSerializer):
    """Serializer for CustomUser model representation[cite: 14]."""

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']


class PublisherSerializer(serializers.ModelSerializer):
    """Serializer for Publisher organization details[cite: 14]."""

    class Meta:
        model = Publisher
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for news articles[cite: 14]."""

    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ['author', 'approved']


class NewsletterSerializer(serializers.ModelSerializer):
    """Serializer for curated newsletters[cite: 14]."""

    class Meta:
        model = Newsletter
        fields = '__all__'
