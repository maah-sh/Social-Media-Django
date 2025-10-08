from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from users.models import  Follow, FollowRequest, FollowRequestStatus

class FollowService:

    def __init__(self, follower_user, following_user):
        self.follower_user = follower_user
        self.following_user = following_user
        self.__result = ''


    def result(self):
        return self.__result


    def follow(self):
        if self.follower_user == self.following_user:
            raise ValidationError("User can't follow itself")
        try:
            Follow.objects.get(follower_user=self.follower_user, following_user=self.following_user)
            raise ValidationError('User already followed')
        except Follow.DoesNotExist:
            if self.following_user.profile.is_private:
                self.send_follow_request()
            else:
                Follow.objects.create(follower_user=self.follower_user, following_user=self.following_user)
                self.__result = 'User followed'


    def unfollow(self):
        follow_instance = get_object_or_404(Follow, follower_user=self.follower_user, following_user=self.following_user)
        follow_instance.delete()
        self.__result = 'User unfollowed'


    def send_follow_request(self):
        try:
            FollowRequest.objects.get(
                from_user=self.follower_user,
                to_user=self.following_user,
                status=FollowRequestStatus.PENDING
            )
            raise ValidationError('Follow request already sent')
        except FollowRequest.DoesNotExist:
            FollowRequest.objects.create(
                from_user=self.follower_user,
                to_user=self.following_user,
                status=FollowRequestStatus.PENDING
            )
            self.__result = 'Follow request sent'


    def __get_or_404_follow_request(self):
        return get_object_or_404(
            FollowRequest,
            from_user=self.follower_user,
            to_user=self.following_user,
            status=FollowRequestStatus.PENDING
        )


    @transaction.atomic
    def accept_follow_request(self):
        follow_request = self.__get_or_404_follow_request()
        follow_request.status = FollowRequestStatus.ACCEPTED
        follow_request.save()
        Follow.objects.get_or_create(follower_user=self.follower_user, following_user=self.following_user)
        self.__result = 'Follow request accepted. Followed by ' + self.follower_user.username


    def reject_follow_request(self):
        follow_request = self.__get_or_404_follow_request()
        follow_request.status = FollowRequestStatus.REJECTED
        follow_request.save()
        self.__result = 'Follow request rejected'


    def revoke_follow_request(self):
        follow_request = self.__get_or_404_follow_request()
        follow_request.status = FollowRequestStatus.REVOKED
        follow_request.save()
        self.__result = 'Follow request revoked'