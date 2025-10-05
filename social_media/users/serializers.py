from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueValidator
from django.db import transaction
from django.contrib.auth.models import User
from users.models import Profile
from posts.serializers import PostSerializer


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['id', 'user', 'bio', 'image', 'is_private']
        extra_kwargs = {
            'user': {'read_only': True},
            'image': {'required': False},
        }


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only=True)
    password_confirmation = serializers.CharField(required=True, write_only=True)
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'password_confirmation', 'profile']
        extra_kwargs = {
            'username': {'required': True, 'validators': [UniqueValidator(queryset=User.objects.all())]},
            'email': {'required': True, 'validators': [UniqueValidator(queryset=User.objects.all())]},
        }

    def validate(self, data):
        # Check password and password_confirmation matched
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError("password and password_confirmation didn't match.")
        data.pop('password_confirmation')
        return data

    @transaction.atomic
    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        Profile.objects.create(user=user, **profile_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class UserReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        extra_kwargs = {
            'username': {'read_only': True},
            'first_name': {'read_only': True},
            'last_name': {'read_only': True},
            'email': {'read_only': True},
        }


class UserProfileSerializer(serializers.ModelSerializer):
     profile = ProfileSerializer()
     posts_count = SerializerMethodField()
     posts = SerializerMethodField()

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
         return user.posts.filter(is_archived=False).count()

     def get_posts(self, user):
         posts = user.posts.filter(is_archived=False)
         return PostSerializer(posts, many=True).data

