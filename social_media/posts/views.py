from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer, CommentCreationSerializer
from .permissions import IsOwner, IsOwnerOrReadOnlyPublished


class UserPostsList(generics.ListAPIView):
    serializer_class = PostSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(owner=self.request.user)


class PublishedPostsList(generics.ListAPIView):
    queryset = Post.objects.filter(published=True)
    serializer_class = PostSerializer


class PostCreate(generics.CreateAPIView):
    serializer_class = PostSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnlyPublished]


class CommentCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CommentCreationSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(owner=self.request.user)
            comment_serializer = CommentSerializer(instance=comment)
            return Response(comment_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]


class PostCommentsList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnlyPublished]

    def get(self, request, pk, format=None):
        comments = Comment.objects.filter(post__pk=pk)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class LikePost(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    dislike = False

    def post(self, request):
        if 'post_id' not in request.data:
            return Response({"post_id": "This field is required"}, status=status.HTTP_400_BAD_REQUEST)

        post = get_object_or_404(Post, id=request.data['post_id'])
        if self.dislike:
            post.likes.remove(self.request.user)
        else:
            post.likes.add(self.request.user)

        return Response({"posts_count": post.likes.count()}, status=status.HTTP_200_OK)
