from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import CustomUser, Publisher, Article, Newsletter


class NewsAppFullTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.reader = CustomUser.objects.create_user(username='reader1', password='password123', role='reader')
        self.journalist = CustomUser.objects.create_user(username='writer1', password='password123', role='journalist')
        self.editor = CustomUser.objects.create_user(username='editor1', password='password123', role='editor')
        
        self.publisher = Publisher.objects.create(name="Tech Times")
        self.article = Article.objects.create(
            title="Django Capstone",
            content="Testing suite details...",
            author=self.journalist,
            publisher=self.publisher,
            approved=True
        )

    def test_registration_view_renders_and_creates_user(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

        post_data = {
            'username': 'newuser',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'role': 'reader',
            'email': 'newuser@example.com'
        }
        res = self.client.post(reverse('register'), post_data)
        self.assertTrue(CustomUser.objects.filter(username='newuser').exists())

    def test_role_change_clears_reader_subscriptions(self):
        self.reader.subscribed_publishers.add(self.publisher)
        self.assertEqual(self.reader.subscribed_publishers.count(), 1)
        
        # Change role to journalist
        self.reader.role = 'journalist'
        self.reader.save()
        self.assertEqual(self.reader.subscribed_publishers.count(), 0)

    def test_article_list_view_renders(self):
        response = self.client.get(reverse('article_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Capstone")

    def test_editor_access_to_pending_articles(self):
        self.client.force_login(self.editor)
        res_editor = self.client.get(reverse('pending_articles'))
        self.assertEqual(res_editor.status_code, 200)
