from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from django.contrib.auth.models import User
from user_profile.models import Profile
from posts.serializers import PostSerializer


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['id', 'user', 'bio', 'image', 'is_private']
        extra_kwargs = {
            'user': {'read_only': True},
            'image': {'required': False},
        }


class UserProfileSerializer(serializers.ModelSerializer):
     profile = ProfileSerializer()
     posts_count = SerializerMethodField()
     posts = PostSerializer(many=True)

     class Meta:
         model = User
         fields = ['username', 'first_name', 'last_name', 'profile', 'posts_count', 'posts']
         extra_kwargs = {
             'username': {'read_only': True},
             'first_name': {'read_only': True},
             'last_name': {'read_only': True},
         }

     def __init__(self, *args, **kwargs):
         is_private = kwargs.pop('is_private', False)
         super().__init__(*args, **kwargs)

         if is_private:
             self.fields.pop('posts')


     def get_posts_count(self, user):
         return user.posts.count()

