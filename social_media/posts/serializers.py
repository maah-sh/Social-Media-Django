from django.db.models import Count
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from .models import Post, Comment
from django.contrib.contenttypes.models import ContentType


class CommentRelatedField(serializers.RelatedField):

    def to_representation(self, value):
        serializer = CommentSerializer(value)
        return serializer.data


class CommentedObjectRelatedField(serializers.RelatedField):

    def to_representation(self, value):
        if isinstance(value, Post):
            return 'post_id: ' + str(value.pk)
        elif isinstance(value, Comment):
            return 'comment_id: ' + str(value.pk)
        raise Exception('Unexpected type of commented object')


class CommentSerializer(serializers.ModelSerializer):
    replies = CommentRelatedField(many=True, required=False, read_only=True)
    content_object = CommentedObjectRelatedField(required=False, read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'content_object', 'owner', 'text', 'replies']
        extra_kwargs = {
            'owner': {'read_only': True},
        }


class PostSerializer(serializers.ModelSerializer):
    likes_count = SerializerMethodField()
    comments_count = SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'image', 'published', 'owner', 'created', 'updated', 'likes_count', 'comments_count']
        extra_kwargs = {
            'owner': {'read_only': True},
            'content' : {'required': False},
            'image': {'required': False},
        }

    def get_likes_count(self, post):
        return post.likes.count()

    def get_comments_count(self, post):
        comments = post.comments
        return comments.count() + comments.aggregate(Count('replies'))['replies__count']


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

