from rest_framework import serializers

from .models import Article, CustomUser, Newsletter, Publisher


class ArticleSerializer(serializers.ModelSerializer):
    def validate_approved(self, value):
        request = self.context.get('request')
        if not value:
            return value

        if request and request.user and (request.user.is_staff or request.user.role == 'editor'):
            return value

        raise serializers.ValidationError('Only editors can mark an article as approved.')

    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ('author', 'created_at')


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'


class NewsletterSerializer(serializers.ModelSerializer):
    def validate_articles(self, value):
        if any(not article.approved for article in value):
            raise serializers.ValidationError('Newsletters can only include approved articles.')
        return value

    class Meta:
        model = Newsletter
        fields = '__all__'
        read_only_fields = ('author', 'created_at')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
