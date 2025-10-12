def post(self, request):
    follow_service = super().post(request)


follow_service.follow()


def post(self, request):
    if not 'following_username' in request.data:
        raise ValidationError({"following_username": "Field is required"})

    following_user = get_object_or_404(User, username=request.data['following_username'])
    follow_service = FollowService(follower_user=request.user, following_user=following_user)


return follow_service