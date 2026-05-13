from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Article, CustomUser, Newsletter, Publisher


class CapstoneWorkflowTests(APITestCase):
	def setUp(self):
		self.publisher = Publisher.objects.create(name='Tech Daily')

		self.reader = CustomUser.objects.create_user(
			username='reader1',
			password='ReaderPass123!',
			role='reader',
			email='reader@example.com',
		)
		self.journalist = CustomUser.objects.create_user(
			username='journalist1',
			password='JournalistPass123!',
			role='journalist',
			email='journalist@example.com',
		)
		self.editor = CustomUser.objects.create_user(
			username='editor1',
			password='EditorPass123!',
			role='editor',
			email='editor@example.com',
		)

		self.approved_article = Article.objects.create(
			title='Approved News',
			content='approved content',
			author=self.journalist,
			approved=True,
			publisher=self.publisher,
		)
		self.pending_article = Article.objects.create(
			title='Pending News',
			content='pending content',
			author=self.journalist,
			approved=False,
			publisher=self.publisher,
		)

	def test_authentication_required_for_articles(self):
		response = self.client.get('/api/articles/')
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_jwt_token_login_works(self):
		response = self.client.post(
			reverse('token_obtain_pair'),
			{'username': 'reader1', 'password': 'ReaderPass123!'},
			format='json',
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn('access', response.data)

	def test_reader_sees_only_approved_articles(self):
		self.client.force_authenticate(user=self.reader)
		response = self.client.get('/api/articles/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		titles = [item['title'] for item in response.data]
		self.assertIn('Approved News', titles)
		self.assertNotIn('Pending News', titles)

	def test_reader_cannot_create_article(self):
		self.client.force_authenticate(user=self.reader)
		response = self.client.post(
			'/api/articles/',
			{
				'title': 'Reader Attempt',
				'content': 'nope',
				'publisher': self.publisher.id,
				'approved': False,
			},
			format='json',
		)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_journalist_can_create_article(self):
		self.client.force_authenticate(user=self.journalist)
		response = self.client.post(
			'/api/articles/',
			{
				'title': 'Journalist Story',
				'content': 'draft',
				'publisher': self.publisher.id,
			},
			format='json',
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertFalse(response.data['approved'])

	def test_journalist_cannot_approve_article(self):
		self.client.force_authenticate(user=self.journalist)
		response = self.client.post(
			'/api/approved/',
			{'article_id': self.pending_article.id},
			format='json',
		)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_editor_can_approve_article(self):
		self.client.force_authenticate(user=self.editor)
		response = self.client.post(
			'/api/approved/',
			{'article_id': self.pending_article.id},
			format='json',
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.pending_article.refresh_from_db()
		self.assertTrue(self.pending_article.approved)

	def test_newsletter_cannot_include_unapproved_article(self):
		self.client.force_authenticate(user=self.editor)
		response = self.client.post(
			'/api/newsletters/',
			{
				'title': 'Weekly Tech Roundup',
				'description': 'Top stories',
				'articles': [self.pending_article.id],
			},
			format='json',
		)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_newsletter_can_include_approved_article(self):
		self.client.force_authenticate(user=self.editor)
		response = self.client.post(
			'/api/newsletters/',
			{
				'title': 'Sports Weekly',
				'description': 'Approved stories only',
				'articles': [self.approved_article.id],
			},
			format='json',
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Newsletter.objects.count(), 1)

