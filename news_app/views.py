from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django import forms
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.db.models import Q

from .models import Article, CustomUser, Publisher, Newsletter
from .serializers import ArticleSerializer, UserSerializer, PublisherSerializer, NewsletterSerializer


# Forms
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'role',)


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'publisher']


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['title', 'description', 'articles']


# Authentication & Registration
def register_view(request):
    """Render and process user registration with designated role selection."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            if user.role == 'editor':
                return redirect('pending_articles')
            elif user.role == 'journalist':
                return redirect('create_article')
            else:
                return redirect('article_list')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'news_app/register.html', {'form': form})


def article_list_view(request):
    """Public news feed showing all approved articles."""
    articles = Article.objects.filter(approved=True).order_by('-created_at')
    return render(request, 'news_app/article_list.html', {'articles': articles})


# Role Checks
def is_editor(user):
    return user.is_authenticated and user.role == 'editor'

def is_journalist(user):
    return user.is_authenticated and user.role == 'journalist'

def is_journalist_or_editor(user):
    return user.is_authenticated and user.role in ['journalist', 'editor']


# Editor Approval Views
@user_passes_test(is_editor)
def pending_articles_list(request):
    """Render pending articles for editor review."""
    articles = Article.objects.filter(approved=False)
    return render(request, 'news_app/approve_articles.html', {'articles': articles})


@user_passes_test(is_editor)
def approve_article_action(request, article_id):
    """Approve article and trigger publication signals."""
    article = get_object_or_404(Article, id=article_id)
    article.approved = True
    article.save()
    return redirect('pending_articles')


# Journalist Article Workflows (Create, Edit, Delete)
@user_passes_test(is_journalist)
def create_article_view(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.approved = False
            article.save()
            return redirect('article_list')
    else:
        form = ArticleForm()
    return render(request, 'news_app/create_article.html', {'form': form})


@user_passes_test(is_journalist)
def edit_article_view(request, article_id):
    article = get_object_or_404(Article, id=article_id, author=request.user)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            updated_article = form.save(commit=False)
            updated_article.approved = False  # Reset approval on edit
            updated_article.save()
            return redirect('article_list')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'news_app/edit_article.html', {'form': form, 'article': article})


@user_passes_test(is_journalist)
def delete_article_view(request, article_id):
    article = get_object_or_404(Article, id=article_id, author=request.user)
    if request.method == 'POST':
        article.delete()
        return redirect('article_list')
    return render(request, 'news_app/delete_article_confirm.html', {'article': article})


# Newsletter Workflows (Create, Edit, Delete)
def newsletter_list_view(request):
    newsletters = Newsletter.objects.all().order_by('-created_at')
    return render(request, 'news_app/newsletter_list.html', {'newsletters': newsletters})


@user_passes_test(is_journalist_or_editor)
def create_newsletter_view(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.author = request.user
            newsletter.save()
            form.save_m2m()
            return redirect('newsletter_list')
    else:
        form = NewsletterForm()
    return render(request, 'news_app/create_newsletter.html', {'form': form})


@user_passes_test(is_journalist_or_editor)
def edit_newsletter_view(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id, author=request.user)
    if request.method == 'POST':
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            form.save()
            return redirect('newsletter_list')
    else:
        form = NewsletterForm(instance=newsletter)
    return render(request, 'news_app/edit_newsletter.html', {'form': form, 'newsletter': newsletter})


@user_passes_test(is_journalist_or_editor)
def delete_newsletter_view(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id, author=request.user)
    if request.method == 'POST':
        newsletter.delete()
        return redirect('newsletter_list')
    return render(request, 'news_app/delete_newsletter_confirm.html', {'newsletter': newsletter})


# DRF API ViewSet
class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return Article.objects.filter(approved=True)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(detail=False, methods=['get'])
    def subscribed(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
    
        if getattr(request.user, 'role', None) != 'reader':
            return Response(
                {"detail": "Only readers can access subscribed articles."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        fav_publishers = request.user.subscribed_publishers.all()
        fav_journalists = request.user.subscribed_journalists.all()

        articles = Article.objects.filter(approved=True).filter(
            Q(publisher__in=fav_publishers) | Q(author__in=fav_journalists)
        ).distinct()

        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)


@api_view(['POST'])
def api_approved_log(request):
    return Response({"status": "Article approval logged successfully"}, status=status.HTTP_200_OK)
