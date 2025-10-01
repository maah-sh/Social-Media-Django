from django.db import DatabaseError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserReadOnlySerializer


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