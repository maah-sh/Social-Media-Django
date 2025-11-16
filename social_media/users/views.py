from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from users.models import Profile, Follow, FollowRequest, FollowRequestStatus
from users.serializers import UserRegisterSerializer, UserLoginSerializer, UserReadOnlySerializer
from users.serializers import ProfileSerializer, UserProfileSerializer, UserPrivateProfileSerializer
from users.serializers import FollowingSerializer, FollowerSerializer, SentFollowRequestSerializer, ReceivedFollowRequestSerializer
from users.services import FollowService


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


class ProfileRetrieve(generics.RetrieveAPIView):
    queryset = User.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'username'

    def get_serializer_class(self):
        user = self.get_object()
        if user == self.request.user or not user.profile.is_private or user.followers.filter(follower_user=self.request.user):
            return UserProfileSerializer
        return UserPrivateProfileSerializer


class FollowUser(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not 'following_username' in request.data:
            raise ValidationError({"following_username": "Field is required"})

        following_user = get_object_or_404(User, username=request.data['following_username'])
        follow_service = FollowService(follower_user=request.user, following_user=following_user)
        follow_service.follow()
        return Response(follow_service.result(),status=status.HTTP_201_CREATED)


class UnfollowUser(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not 'following_username' in request.data:
            raise ValidationError({"following_username": "Field is required"})

        following_user = get_object_or_404(User, username=request.data['following_username'])
        follow_service = FollowService(follower_user=request.user, following_user=following_user)
        follow_service.unfollow()
        return Response(follow_service.result(),status=status.HTTP_201_CREATED)


class FollowRequestAccept(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not 'sender_username' in request.data:
            raise ValidationError({"sender_username": "Field is required"})

        sender_user = get_object_or_404(User, username=request.data['sender_username'])
        follow_service = FollowService(follower_user=sender_user, following_user=request.user)
        follow_service.accept_follow_request()
        return Response(follow_service.result(), status=status.HTTP_200_OK)


class FollowRequestReject(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not 'sender_username' in request.data:
            raise ValidationError({"sender_username": "Field is required"})

        sender_user = get_object_or_404(User, username=request.data['sender_username'])
        follow_service = FollowService(follower_user=sender_user, following_user=request.user)
        follow_service.reject_follow_request()
        return Response(follow_service.result(), status=status.HTTP_200_OK)


class FollowRequestRevoke(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not 'receiver_username' in request.data:
            raise ValidationError({"receiver_username": "Field is required"})

        receiver_user = get_object_or_404(User, username=request.data['receiver_username'])
        follow_service = FollowService(follower_user=request.user, following_user=receiver_user)
        follow_service.revoke_follow_request()
        return Response(follow_service.result(), status=status.HTTP_200_OK)


class FollowingList(generics.ListAPIView):
    serializer_class = FollowingSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return self.request.user.following.order_by('following_user__username')


class FollowersList(generics.ListAPIView):
    serializer_class = FollowerSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return self.request.user.followers.order_by('follower_user__username')


class SentFollowRequestsList(generics.ListAPIView):
    serializer_class = SentFollowRequestSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return self.request.user.sent_follow_requests.filter(status=FollowRequestStatus.PENDING)


class ReceivedFollowRequestsList(generics.ListAPIView):
    serializer_class = ReceivedFollowRequestSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return self.request.user.received_follow_requests.filter(status=FollowRequestStatus.PENDING)