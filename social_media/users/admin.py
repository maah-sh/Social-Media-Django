from django.contrib import admin
from .models import Profile, Follow, FollowRequest


class ProfileGroup(admin.ModelAdmin):
    search_fields = ['=user__username']

admin.site.register(Profile, ProfileGroup)
admin.site.register(Follow)
admin.site.register(FollowRequest)
