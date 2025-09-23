from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'image', 'published', 'owner', 'created', 'updated']
        extra_kwargs = {
            'owner': {'read_only': True},
        }