from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from user_profile.models import Profile
from user_profile.serializers import ProfileSerializer, UserProfileSerializer


class ProfileUpdate(generics.UpdateAPIView):
    serializer_class = ProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = get_object_or_404(Profile, user=self.request.user)
        self.check_object_permissions(self.request, obj)
        return obj


class ProfileRetrieve(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        user = User.objects.get(username=username)
        if user == request.user or not user.profile.is_private:
            serializer = UserProfileSerializer(user)
        else:
            serializer = UserProfileSerializer(user, is_private = True)
        return Response(serializer.data)