from rest_framework import serializers
from .models import Post, Comment
from django.contrib.contenttypes.models import ContentType


class CommentedObjectRelatedField(serializers.RelatedField):

    def to_representation(self, value):
        if isinstance(value, Post):
            serializer = PostSerializer(value)
        elif isinstance(value, Comment):
            serializer = CommentSerializer(value)
        else:
            raise Exception('Unexpected type of commented object')

        return serializer.data


class PostSerializer(serializers.ModelSerializer):
    comments = CommentedObjectRelatedField(many=True, required=False, read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'image', 'published', 'owner', 'comments', 'created', 'updated']
        extra_kwargs = {
            'owner': {'read_only': True},
        }


class CommentSerializer(serializers.ModelSerializer):
    replies = CommentedObjectRelatedField(many=True, required=False, read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'owner', 'text', 'replies']
        extra_kwargs = {
            'owner': {'read_only': True},
        }

class CommentCreationSerializer(serializers.Serializer):
    text = serializers.CharField(required=True)
    app_label = serializers.CharField(required=True)
    model = serializers.CharField(required=True)
    object_id = serializers.IntegerField(required=True)

    def validate(self, data):
        content_type = ContentType.objects.get_by_natural_key(data['app_label'], data['model'])
        data['content_type'] = content_type
        data.pop('app_label')
        data.pop('model')
        return data

    def create(self, validated_data):
        return Comment.objects.create(**validated_data)

