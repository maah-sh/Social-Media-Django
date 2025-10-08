from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueValidator
from django.db import transaction
from django.contrib.auth.models import User
from users.models import Profile, Follow, FollowRequest
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


     def get_posts_count(self, user):
         return user.posts.filter(is_archived=False).count()

     def get_posts(self, user):
         posts = user.posts.filter(is_archived=False)
         return PostSerializer(posts, many=True).data


class UserPrivateProfileSerializer(UserProfileSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('posts')


class FollowingSerializer(serializers.ModelSerializer):
    following_username = SerializerMethodField()

    class Meta:
        model = Follow
        fields = ['following_user_id', 'following_username']

    def get_following_username(self, obj):
        return obj.following_user.username


class FollowerSerializer(serializers.ModelSerializer):
    follower_username = SerializerMethodField()

    class Meta:
        model = Follow
        fields = ['follower_user_id', 'follower_username']

    def get_follower_username(self, obj):
        return obj.follower_user.username


class SentFollowRequestSerializer(serializers.ModelSerializer):
    to_username = SerializerMethodField()

    class Meta:
        model = FollowRequest
        fields = ['to_user_id', 'to_username', 'created_at']

    def get_to_username(self, obj):
        return obj.to_user.username

class ReceivedFollowRequestSerializer(serializers.ModelSerializer):
    from_username = SerializerMethodField()

    class Meta:
        model = FollowRequest
        fields = ['from_user_id', 'from_username', 'created_at']

    def get_from_username(self, obj):
        return obj.from_user.username