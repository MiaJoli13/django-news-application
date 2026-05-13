from django.contrib.auth.models import AbstractUser
from django.db import models


ROLE_CHOICES = (
	('reader', 'Reader'),
	('editor', 'Editor'),
	('journalist', 'Journalist'),
)


class Publisher(models.Model):
	name = models.CharField(max_length=255)

	def __str__(self):
		return self.name


class CustomUser(AbstractUser):
	role = models.CharField(max_length=20, choices=ROLE_CHOICES)
	subscribed_publishers = models.ManyToManyField(Publisher, blank=True)
	subscribed_journalists = models.ManyToManyField('self', blank=True, symmetrical=False)


class Article(models.Model):
	title = models.CharField(max_length=255)
	content = models.TextField()
	author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	approved = models.BooleanField(default=False)
	publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return self.title


class Newsletter(models.Model):
	title = models.CharField(max_length=255)
	description = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
	articles = models.ManyToManyField(Article)

	def __str__(self):
		return self.title
