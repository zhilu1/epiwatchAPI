from rest_framework import serializers
from rest_framework_mongoengine import serializers as mongoserializers

from epiwatch.models import Article


class ArticleSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = Article
        fields = '__all__'
