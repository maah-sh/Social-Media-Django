from user_profile.models import Profile
from rest_framework import serializers


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['id', 'user', 'bio', 'image', 'is_private']
        extra_kwargs = {
            'user': {'read_only': True},
            'image': {'required': False},
        }