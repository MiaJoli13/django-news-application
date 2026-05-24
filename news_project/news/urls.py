from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ArticleViewSet, home

router = DefaultRouter()
router.register(r'articles', ArticleViewSet)

urlpatterns = [
    path('', home, name='home'),
    path('api/', include(router.urls)),
]
