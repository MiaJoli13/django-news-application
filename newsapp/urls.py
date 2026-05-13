from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ApproveArticleView, ArticleViewSet, NewsletterViewSet, PublisherViewSet

router = DefaultRouter()
router.register('articles', ArticleViewSet, basename='articles')
router.register('publishers', PublisherViewSet, basename='publishers')
router.register('newsletters', NewsletterViewSet, basename='newsletters')

urlpatterns = [
    path('', include(router.urls)),
    path('approved/', ApproveArticleView.as_view(), name='approved-article'),
]
