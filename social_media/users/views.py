from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from users.models import Profile
from users.serializers import UserRegisterSerializer, UserLoginSerializer, UserReadOnlySerializer
from users.serializers import ProfileSerializer, UserProfileSerializer


class Register(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):
    def post(self, request):
        login_serializer = UserLoginSerializer(data=request.data)
        if not login_serializer.is_valid():
            return Response(login_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, username=request.data['username'])
        if not user.check_password(request.data['password']):
            return Response({"details": "Password doesn't match"}, status=status.HTTP_404_NOT_FOUND)

        refresh_token = RefreshToken.for_user(user)
        user_serializer = UserReadOnlySerializer(instance=user)
        return Response(
            {
                "token": {
                    'refresh': str(refresh_token),
                    'access': str(refresh_token.access_token),
                },
                "user": user_serializer.data
            },
            status=status.HTTP_200_OK
        )


class Logout(APIView):
    def post(self, request):
        if not "refresh" in request.data:
            return Response({"details": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            RefreshToken(request.data['refresh']).blacklist()
            return Response({"details": "Logged out"}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({"details": "Token Error"}, status=status.HTTP_400_BAD_REQUEST)


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