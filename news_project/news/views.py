from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Article
from .permissions import ArticleRolePermission
from .serializers import ArticleSerializer


def home(request):
	return HttpResponse("Welcome to the News Application")


class ArticleViewSet(viewsets.ModelViewSet):
	queryset = Article.objects.all()
	serializer_class = ArticleSerializer
	permission_classes = [IsAuthenticatedOrReadOnly, ArticleRolePermission]

	def perform_create(self, serializer):
		serializer.save(author=self.request.user)
