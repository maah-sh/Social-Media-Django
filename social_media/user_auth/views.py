from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserProfileSerializer


@api_view(['POST'])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    login_serializer = UserLoginSerializer(data=request.data)
    if not login_serializer.is_valid():
        return Response(login_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response({"details": "Password doesn't match"}, status=status.HTTP_404_NOT_FOUND)

    refresh_token = RefreshToken.for_user(user)
    profile_serializer = UserProfileSerializer(instance=user)
    return Response(
        {
            "token": {
                'refresh': str(refresh_token),
                'access': str(refresh_token.access_token),
            },
            "user": profile_serializer.data
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
def logout(request):
    if not "refresh" in request.data:
        return Response({"details": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        RefreshToken(request.data['refresh']).blacklist()
        return Response({"details": "Logged out"}, status=status.HTTP_200_OK)
    except TokenError:
        return Response({"details": "Token Error"}, status=status.HTTP_400_BAD_REQUEST)