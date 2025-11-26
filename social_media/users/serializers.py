from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueValidator
from django.db import transaction
from django.contrib.auth.models import User
from users.models import Profile, Follow, FollowRequest, FollowRequestStatus
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

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'password_confirmation']
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
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
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
     follow_status = SerializerMethodField()
     followers_count = SerializerMethodField()
     following_count = SerializerMethodField()
     posts_count = SerializerMethodField()
     posts = SerializerMethodField()

     class Meta:
         model = User
         fields = ['username', 'first_name', 'last_name', 'profile', 'follow_status', 'followers_count', 'following_count',
                   'posts_count', 'posts']
         extra_kwargs = {
             'username': {'read_only': True},
             'first_name': {'read_only': True},
             'last_name': {'read_only': True},
         }


     def get_follow_status(self, user):
         if self.context['request'].user == user:
             return 'your profile'
         elif user.followers.filter(follower_user_id = self.context['request'].user.id).exists():
             return 'followed'
         elif user.received_follow_requests.filter(from_user_id = self.context['request'].user.id, status=FollowRequestStatus.PENDING).exists():
             return 'requested'
         else:
             return 'not followed'


     def get_followers_count(self, user):
         return user.followers.count()


     def get_following_count(self, user):
         return user.following.count()


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


class UserSearchSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(source='profile.image')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'profile_image']
        extra_kwargs = {
            'username': {'read_only': True},
            'first_name': {'read_only': True},
            'last_name': {'read_only': True},
            'profile_image': {'read_only': True},
        }