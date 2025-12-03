from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='users/profile_images', default='users/profile_images/profile.jpg')
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile object ({self.pk}) -> User ({self.user.username} : {self.user.first_name} {self.user.last_name})"


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
    REVOKED = 3, 'Revoked'

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


class ProfileCount(models.Model):
    all = models.PositiveBigIntegerField()
    public = models.PositiveBigIntegerField()
    private = models.PositiveBigIntegerField()
    created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Profile Count -> all: {self.all}, public: {self.public}, private: {self.private}"
