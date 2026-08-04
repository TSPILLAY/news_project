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
    """Form to extend standard user creation with email and role selection."""
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'role',)


class ArticleForm(forms.ModelForm):
    """Form for creating and updating news articles."""
    
    class Meta:
        model = Article
        fields = ['title', 'content', 'publisher']


class NewsletterForm(forms.ModelForm):
    """Form for creating and updating curated newsletters."""
    
    class Meta:
        model = Newsletter
        fields = ['title', 'description', 'articles']


class PublisherForm(forms.ModelForm):
    """Form for creating and managing publishing organizations."""
    
    class Meta:
        model = Publisher
        fields = ['name', 'description', 'editors', 'journalists']
        widgets = {
            'editors': forms.CheckboxSelectMultiple,
            'journalists': forms.CheckboxSelectMultiple,
        }


class SubscriptionForm(forms.ModelForm):
    """Form for readers to manage their subscribed publishers and journalists."""
    
    class Meta:
        model = CustomUser
        fields = ['subscribed_publishers', 'subscribed_journalists']
        widgets = {
            'subscribed_publishers': forms.CheckboxSelectMultiple,
            'subscribed_journalists': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'subscribed_journalists' in self.fields:
            self.fields['subscribed_journalists'].queryset = CustomUser.objects.filter(role='journalist')


# Role Helper Checks
def is_editor(user):
    """Check if the user is authenticated and has an Editor role."""
    return user.is_authenticated and user.role == 'editor'


def is_journalist(user):
    """Check if the user is authenticated and has a Journalist role."""
    return user.is_authenticated and user.role == 'journalist'


def is_journalist_or_editor(user):
    """Check if the user is authenticated and is either a Journalist or Editor."""
    return user.is_authenticated and user.role in ['journalist', 'editor']


# Authentication & Registration Views
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


# Reader Workflows
@login_required
def manage_subscriptions_view(request):
    """Allow reader users to manage their publisher and journalist subscriptions."""
    if request.user.role != 'reader':
        return redirect('article_list')

    if request.method == 'POST':
        form = SubscriptionForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('manage_subscriptions')
    else:
        form = SubscriptionForm(instance=request.user)

    return render(request, 'news_app/manage_subscriptions.html', {'form': form})


# Editor Workflows & Publisher Management
@user_passes_test(is_editor)
def pending_articles_list(request):
    """Render pending articles for editor review."""
    articles = Article.objects.filter(approved=False)
    return render(request, 'news_app/approve_articles.html', {'articles': articles})


@user_passes_test(is_editor)
def approve_article_action(request, article_id):
    """Approve an article and trigger publication signals."""
    article = get_object_or_404(Article, id=article_id)
    article.approved = True
    article.save()
    return redirect('pending_articles')


@user_passes_test(is_editor)
def editor_edit_article_view(request, article_id):
    """Allow editors to edit any news article."""
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('article_list')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'news_app/edit_article.html', {'form': form, 'article': article})


@user_passes_test(is_editor)
def editor_delete_article_view(request, article_id):
    """Allow editors to delete any news article."""
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        article.delete()
        return redirect('article_list')
    return render(request, 'news_app/delete_article_confirm.html', {'article': article})


@user_passes_test(is_editor)
def manage_publishers_view(request):
    """Allow editors to create and manage publishers and assigned staff."""
    publishers = Publisher.objects.all()
    if request.method == 'POST':
        form = PublisherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_publishers')
    else:
        form = PublisherForm()
    return render(request, 'news_app/manage_publishers.html', {'publishers': publishers, 'form': form})


# Journalist Workflows (Create, Edit, Delete)
@user_passes_test(is_journalist)
def create_article_view(request):
    """Allow journalists to draft and submit new articles for review."""
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
    """Allow journalists to edit their own articles prior to or following approval."""
    article = get_object_or_404(Article, id=article_id, author=request.user)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            updated_article = form.save(commit=False)
            updated_article.approved = False  # Resets status to pending for re-review
            updated_article.save()
            return redirect('article_list')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'news_app/edit_article.html', {'form': form, 'article': article})


@user_passes_test(is_journalist)
def delete_article_view(request, article_id):
    """Allow journalists to delete their own articles regardless of approval state."""
    article = get_object_or_404(Article, id=article_id, author=request.user)
    if request.method == 'POST':
        article.delete()
        return redirect('article_list')
    return render(request, 'news_app/delete_article_confirm.html', {'article': article})


# Newsletter Workflows (Create, Edit, Delete)
def newsletter_list_view(request):
    """Public list of all curated newsletters."""
    newsletters = Newsletter.objects.all().order_by('-created_at')
    return render(request, 'news_app/newsletter_list.html', {'newsletters': newsletters})


@user_passes_test(is_journalist_or_editor)
def create_newsletter_view(request):
    """Allow journalists and editors to curate new newsletters."""
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
    """Allow journalists (their own) or editors to update existing newsletters."""
    if request.user.role == 'editor':
        newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    else:
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
    """Allow journalists (their own) or editors to delete existing newsletters."""
    if request.user.role == 'editor':
        newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    else:
        newsletter = get_object_or_404(Newsletter, id=newsletter_id, author=request.user)

    if request.method == 'POST':
        newsletter.delete()
        return redirect('newsletter_list')
    return render(request, 'news_app/delete_newsletter_confirm.html', {'newsletter': newsletter})


# REST API Endpoints
class ArticleViewSet(viewsets.ModelViewSet):
    """REST API ViewSet for retrieving and managing news articles."""
    
    serializer_class = ArticleSerializer

    def get_queryset(self):
        """Return all approved articles for standard listings."""
        return Article.objects.filter(approved=True)

    def get_permissions(self):
        """Restrict creation and editing actions to authenticated users."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(detail=False, methods=['get'])
    def subscribed(self, request):
        """Retrieve custom feed filtered by reader subscriptions."""
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
    """API endpoint target for article approval webhooks."""
    return Response({"status": "Article approval logged successfully"}, status=status.HTTP_200_OK)
