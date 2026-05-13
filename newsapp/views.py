from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Article, Newsletter, Publisher
from .serializers import ArticleSerializer, NewsletterSerializer, PublisherSerializer


class ArticleRolePermission(permissions.BasePermission):
	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return True
		if not request.user or not request.user.is_authenticated:
			return False

		if request.method == 'POST':
			return request.user.is_staff or request.user.role == 'journalist'

		if request.method in {'PUT', 'PATCH'}:
			return request.user.is_staff or request.user.role in {'journalist', 'editor'}

		if request.method == 'DELETE':
			return request.user.is_staff or request.user.role == 'editor'

		return False

	def has_object_permission(self, request, view, obj):
		if request.method in permissions.SAFE_METHODS:
			return True

		if request.user.is_staff:
			return True

		if request.user.role == 'editor':
			return True

		if request.user.role == 'journalist' and request.method in {'PUT', 'PATCH'}:
			return obj.author_id == request.user.id

		return False


class NewsletterRolePermission(permissions.BasePermission):
	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return True
		if not request.user or not request.user.is_authenticated:
			return False
		return request.user.is_staff or request.user.role in {'editor', 'journalist'}


class ArticleViewSet(viewsets.ModelViewSet):
	serializer_class = ArticleSerializer
	permission_classes = [permissions.IsAuthenticated, ArticleRolePermission]

	def get_queryset(self):
		user = self.request.user
		if user.is_staff or user.role in {'editor', 'journalist'}:
			if user.role == 'journalist':
				return Article.objects.filter(Q(approved=True) | Q(author=user)).order_by('-created_at')
			return Article.objects.all().order_by('-created_at')
		return Article.objects.filter(approved=True).order_by('-created_at')

	def perform_create(self, serializer):
		serializer.save(author=self.request.user, approved=False)


class PublisherViewSet(viewsets.ModelViewSet):
	queryset = Publisher.objects.all().order_by('name')
	serializer_class = PublisherSerializer
	permission_classes = [permissions.IsAuthenticated]


class NewsletterViewSet(viewsets.ModelViewSet):
	queryset = Newsletter.objects.all().order_by('-created_at')
	serializer_class = NewsletterSerializer
	permission_classes = [permissions.IsAuthenticated, NewsletterRolePermission]

	def perform_create(self, serializer):
		serializer.save(author=self.request.user)


class ApproveArticleView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request):
		if not (request.user.is_staff or request.user.role == 'editor'):
			return Response({'detail': 'Only editors can approve articles.'}, status=status.HTTP_403_FORBIDDEN)

		article_id = request.data.get('article_id')
		if not article_id:
			return Response({'detail': 'article_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

		article = get_object_or_404(Article, id=article_id)
		article.approved = True
		article.save(update_fields=['approved'])

		if article.author.email:
			send_mail(
				subject='Your article was approved',
				message=f'Your article "{article.title}" has been approved by an editor.',
				from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@newsapp.local'),
				recipient_list=[article.author.email],
				fail_silently=True,
			)

		return Response(ArticleSerializer(article).data, status=status.HTTP_200_OK)
