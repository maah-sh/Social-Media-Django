from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='users/profile_images', blank=True)
    is_private = models.BooleanField(default=False)


class Follow(models.Model):
    follower_user = models.ForeignKey(User, related_name='following',on_delete=models.CASCADE)
    following_user = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower_user_id', 'following_user_id'], name='unique_following')
        ]


class FollowRequestStatus(models.IntegerChoices):
    PENDING = 0, 'Pending'
    ACCEPTED = 1, 'Accepted'
    REJECTED = 2, 'Rejected'

class FollowRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_follow_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_follow_requests', on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(choices=FollowRequestStatus, default=FollowRequestStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['from_user', 'to_user'],
                condition=Q(status=FollowRequestStatus.PENDING),
                name='unique_pending_follow_request'
            )
        ]