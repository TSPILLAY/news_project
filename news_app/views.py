"""
View handlers and REST API viewsets for news_app[cite: 8, 9].

Manages registration, article moderation, subscription workflows,
and REST endpoints for external clients[cite: 8, 9].
"""

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


# DRF Custom Permission Classes
class IsJournalist(permissions.BasePermission):
    """Permission class restricting access strictly to authenticated users with the Journalist role[cite: 8, 9]."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'journalist'


class IsEditor(permissions.BasePermission):
    """Permission class restricting access strictly to authenticated users with the Editor role[cite: 8, 9]."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'editor'


# Forms
class CustomUserCreationForm(UserCreationForm):
    """Form extending standard user registration with role selection and unique email validation[cite: 8, 9]."""
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'role',)

    def clean_email(self):
        """Validate that the provided email is non-empty and unique across accounts[cite: 8, 9]."""
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email address is required.")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email


class ArticleForm(forms.ModelForm):
    """Form for journalists and editors to input article details[cite: 8, 9]."""
    class Meta:
        model = Article
        fields = ['title', 'content', 'publisher']


class NewsletterForm(forms.ModelForm):
    """Form to curate newsletters from approved articles[cite: 8, 9]."""
    class Meta:
        model = Newsletter
        fields = ['title', 'description', 'articles']

    def __init__(self, *args, **kwargs):
        """Restrict article selection field to approved articles only[cite: 8, 9]."""
        super().__init__(*args, **kwargs)
        self.fields['articles'].queryset = Article.objects.filter(approved=True)


class PublisherForm(forms.ModelForm):
    """Form to create and update Publisher organizations and staff assignments[cite: 8, 9]."""
    class Meta:
        model = Publisher
        fields = ['name', 'description', 'editors', 'journalists']
        widgets = {
            'editors': forms.CheckboxSelectMultiple,
            'journalists': forms.CheckboxSelectMultiple,
        }


class SubscriptionForm(forms.ModelForm):
    """Form enabling Reader users to subscribe to Publishers and Journalists[cite: 8, 9]."""
    class Meta:
        model = CustomUser
        fields = ['subscribed_publishers', 'subscribed_journalists']
        widgets = {
            'subscribed_publishers': forms.CheckboxSelectMultiple,
            'subscribed_journalists': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        """Filter selectable journalists to active users possessing the Journalist role[cite: 8, 9]."""
        super().__init__(*args, **kwargs)
        if 'subscribed_journalists' in self.fields:
            self.fields['subscribed_journalists'].queryset = CustomUser.objects.filter(role='journalist')


# Role Helper Functions
def is_editor(user):
    """Check if the user is authenticated and holds the Editor role[cite: 8, 9]."""
    return user.is_authenticated and user.role == 'editor'

def is_journalist(user):
    """Check if the user is authenticated and holds the Journalist role[cite: 8, 9]."""
    return user.is_authenticated and user.role == 'journalist'

def is_journalist_or_editor(user):
    """Check if the user is authenticated and holds either Journalist or Editor role[cite: 8, 9]."""
    return user.is_authenticated and user.role in ['journalist', 'editor']


# Views
def register_view(request):
    """Handle new user registration and redirect to role-specific dashboards[cite: 8, 9]."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.role == 'editor':
                return redirect('pending_articles')
            elif user.role == 'journalist':
                return redirect('my_articles')
            else:
                return redirect('article_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'news_app/register.html', {'form': form})


def article_list_view(request):
    """Render public news feed displaying all approved articles ordered by creation date[cite: 8, 9]."""
    articles = Article.objects.filter(approved=True).order_by('-created_at')
    return render(request, 'news_app/article_list.html', {'articles': articles})


@login_required
def manage_subscriptions_view(request):
    """Allow authenticated reader users to update publisher and journalist subscriptions[cite: 8, 9]."""
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


@user_passes_test(is_editor)
def pending_articles_list(request):
    """Display pending articles review queue alongside live published articles for editors[cite: 8, 9]."""
    pending_articles = Article.objects.filter(approved=False).order_by('-created_at')
    approved_articles = Article.objects.filter(approved=True).order_by('-created_at')
    return render(request, 'news_app/approve_articles.html', {
        'articles': pending_articles,
        'approved_articles': approved_articles
    })


@user_passes_test(is_editor)
def approve_article_action(request, article_id):
    """Approve a pending article submission and make it visible on public feeds[cite: 8, 9]."""
    article = get_object_or_404(Article, id=article_id)
    article.approved = True
    article.save()
    return redirect('pending_articles')


@user_passes_test(is_editor)
def editor_edit_article_view(request, article_id):
    """Allow editors to modify existing articles directly[cite: 8, 9]."""
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('pending_articles' if not article.approved else 'article_list')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'news_app/edit_article.html', {'form': form, 'article': article})


@user_passes_test(is_editor)
def editor_delete_article_view(request, article_id):
    """Allow editors to delete any article entry[cite: 8, 9]."""
    article = get_object_or_404(Article, id=article_id)
    was_approved = article.approved
    if request.method == 'POST':
        article.delete()
        return redirect('article_list' if was_approved else 'pending_articles')
    return render(request, 'news_app/delete_article_confirm.html', {'article': article})


@user_passes_test(is_editor)
def manage_publishers_view(request):
    """Display publisher listings and handle new publisher creation[cite: 8, 9]."""
    publishers = Publisher.objects.all()
    if request.method == 'POST':
        form = PublisherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_publishers')
    else:
        form = PublisherForm()
    return render(request, 'news_app/manage_publishers.html', {'publishers': publishers, 'form': form})


@user_passes_test(is_journalist)
def create_article_view(request):
    """Enable journalists to compose and submit articles for editor review[cite: 8, 9]."""
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.approved = False
            article.save()
            return redirect('my_articles')
    else:
        form = ArticleForm()
    return render(request, 'news_app/create_article.html', {'form': form})


@user_passes_test(is_journalist)
def my_articles_view(request):
    """Display articles authored by the currently logged-in journalist[cite: 8, 9]."""
    articles = Article.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'news_app/my_articles.html', {'articles': articles})


@user_passes_test(is_journalist)
def edit_article_view(request, article_id):
    """Allow journalists to edit their own articles, resetting approval status upon save[cite: 8, 9]."""
    article = get_object_or_404(Article, id=article_id, author=request.user)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.approved = False
            updated.save()
            return redirect('my_articles')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'news_app/edit_article.html', {'form': form, 'article': article})


@user_passes_test(is_journalist)
def delete_article_view(request, article_id):
    """Allow journalists to delete their own articles[cite: 8, 9]."""
    article = get_object_or_404(Article, id=article_id, author=request.user)
    if request.method == 'POST':
        article.delete()
        return redirect('my_articles')
    return render(request, 'news_app/delete_article_confirm.html', {'article': article})


def newsletter_list_view(request):
    """Display public directory of all published newsletters[cite: 8, 9]."""
    newsletters = Newsletter.objects.all().order_by('-created_at')
    return render(request, 'news_app/newsletter_list.html', {'newsletters': newsletters})


@user_passes_test(is_journalist_or_editor)
def create_newsletter_view(request):
    """Allow journalists and editors to assemble and publish a newsletter[cite: 8, 9]."""
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
    """Allow editors (or the authoring journalist) to edit newsletter details[cite: 8, 9]."""
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
    """Allow editors (or the authoring journalist) to delete a newsletter[cite: 8, 9]."""
    if request.user.role == 'editor':
        newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    else:
        newsletter = get_object_or_404(Newsletter, id=newsletter_id, author=request.user)

    if request.method == 'POST':
        newsletter.delete()
        return redirect('newsletter_list')
    return render(request, 'news_app/delete_newsletter_confirm.html', {'newsletter': newsletter})


# REST API ViewSet
class ArticleViewSet(viewsets.ModelViewSet):
    """
    REST API ViewSet enforcing role permissions across standard and custom endpoints[cite: 8, 9].
    """
    serializer_class = ArticleSerializer

    def get_queryset(self):
        """Retrieve approved articles for public REST listings[cite: 8, 9]."""
        return Article.objects.filter(approved=True)

    def get_permissions(self):
        """Assign role-based permissions depending on requested action[cite: 8, 9]."""
        if self.action == 'create':
            return [IsJournalist()]
        elif self.action in ['update', 'partial_update', 'destroy', 'approve']:
            return [IsEditor()]
        elif self.action == 'subscribed':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        """Attach authenticated user as author and force unapproved status upon submission[cite: 8, 9]."""
        serializer.save(author=self.request.user, approved=False)

    @action(detail=True, methods=['post'], permission_classes=[IsEditor])
    def approve(self, request, pk=None):
        """API endpoint allowing editors to approve pending article submissions[cite: 8, 9]."""
        article = get_object_or_404(Article, pk=pk)
        article.approved = True
        article.save()
        return Response({'status': 'Article approved successfully'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def subscribed(self, request):
        """API endpoint returning articles from publishers and journalists subscribed to by the reader[cite: 8, 9]."""
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
    """Internal webhook endpoint logging article approval events triggered by signals[cite: 5, 8, 9]."""
    article_id = request.data.get('article_id')
    
    if not article_id:
        return Response({'error': 'article_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        return Response({'error': 'Article does not exist.'}, status=status.HTTP_404_NOT_FOUND)
    except (ValueError, TypeError):
        return Response({'error': 'Invalid article_id format.'}, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {
            "status": "Article approval logged successfully",
            "article_id": article.id,
            "title": article.title
        }, 
        status=status.HTTP_200_OK
    )
