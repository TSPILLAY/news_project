from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'articles', views.ArticleViewSet, basename='article')

urlpatterns = [
    # Auth & Account Management
    path('login/', auth_views.LoginView.as_view(template_name='news_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register_view, name='register'),

    # Entry Point & Main Feed
    path('', views.article_list_view, name='article_list'),
    path('feed/', views.article_list_view, name='article_list'),
    
    # Journalist Workflows
    path('articles/create/', views.create_article_view, name='create_article'),
    path('articles/<int:article_id>/edit/', views.edit_article_view, name='edit_article'),
    path('articles/<int:article_id>/delete/', views.delete_article_view, name='delete_article'),
    
    # Editor Dashboard
    path('pending/', views.pending_articles_list, name='pending_articles'),
    path('approve/<int:article_id>/', views.approve_article_action, name='approve_article'),
    
    # Newsletters
    path('newsletters/', views.newsletter_list_view, name='newsletter_list'),
    path('newsletters/create/', views.create_newsletter_view, name='create_newsletter'),
    path('newsletters/<int:newsletter_id>/edit/', views.edit_newsletter_view, name='edit_newsletter'),
    path('newsletters/<int:newsletter_id>/delete/', views.delete_newsletter_view, name='delete_newsletter'),
    
    # REST API
    path('api/', include(router.urls)),
    path('api/approved-log/', views.api_approved_log, name='api_approved_log'),
]
