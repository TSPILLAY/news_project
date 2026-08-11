from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import Group
from .models import CustomUser, Publisher, Article, Newsletter


class NewsAppFullTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.reader = CustomUser.objects.create_user(username='reader1', email='reader1@example.com', password='password123', role='reader')
        self.journalist = CustomUser.objects.create_user(username='writer1', email='writer1@example.com', password='password123', role='journalist')
        self.editor = CustomUser.objects.create_user(username='editor1', email='editor1@example.com', password='password123', role='editor')
        
        self.publisher = Publisher.objects.create(name="Tech Times")
        self.approved_article = Article.objects.create(
            title="Approved Capstone",
            content="Testing suite details...",
            author=self.journalist,
            publisher=self.publisher,
            approved=True
        )
        self.pending_article = Article.objects.create(
            title="Pending Draft Article",
            content="Draft content awaiting review...",
            author=self.journalist,
            publisher=self.publisher,
            approved=False
        )

    def test_automatic_group_assignment(self):
        """Verify users are automatically assigned to Django Groups matching their role."""
        self.assertTrue(self.reader.groups.filter(name='Reader').exists())
        self.assertTrue(self.journalist.groups.filter(name='Journalist').exists())
        self.assertTrue(self.editor.groups.filter(name='Editor').exists())

    def test_jwt_token_endpoints(self):
        """Verify JWT token obtain and refresh endpoints work correctly."""
        res = self.client.post(reverse('token_obtain_pair'), {'username': 'reader1', 'password': 'password123'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_api_post_article_restricted_to_journalists(self):
        """Verify only journalists can submit new articles through the REST API."""
        # Reader attempt (should fail)
        self.client.force_authenticate(user=self.reader)
        res_reader = self.client.post('/api/articles/', {'title': 'Reader Fail', 'content': 'Content'})
        self.assertEqual(res_reader.status_code, status.HTTP_403_FORBIDDEN)

        # Journalist attempt (should succeed)
        self.client.force_authenticate(user=self.journalist)
        res_journalist = self.client.post('/api/articles/', {'title': 'Journalist Article', 'content': 'Valid text'})
        self.assertEqual(res_journalist.status_code, status.HTTP_201_CREATED)

    def test_editor_can_create_newsletter(self):
        """Verify editors can curate and publish newsletters."""
        newsletter = Newsletter.objects.create(
            title="Editor Digest",
            description="Weekly summary",
            author=self.editor
        )
        newsletter.articles.add(self.approved_article)
        self.assertEqual(newsletter.author.role, 'editor')

    def test_registration_prevents_duplicate_emails(self):
        post_data = {
            'username': 'newuser',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'role': 'reader',
            'email': 'reader1@example.com'
        }
        res = self.client.post(reverse('register'), post_data)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(CustomUser.objects.filter(username='newuser').exists())

    def test_journalist_can_view_unapproved_articles(self):
        self.client.force_login(self.journalist)
        response = self.client.get(reverse('my_articles'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pending Draft Article")

    def test_newsletter_form_only_allows_approved_articles(self):
        self.client.force_login(self.journalist)
        response = self.client.get(reverse('create_newsletter'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Approved Capstone")
        self.assertNotContains(response, "Pending Draft Article")

    def test_editor_access_pending_articles(self):
        self.client.force_login(self.editor)
        res_editor = self.client.get(reverse('pending_articles'))
        self.assertEqual(res_editor.status_code, 200)
        self.assertContains(res_editor, "Pending Draft Article")
