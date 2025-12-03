from celery import shared_task
from django.core.mail import send_mail
from django.db.models import Count, Q
from users.models import Profile, ProfileCount


@shared_task
def profile_count():
    count = Profile.objects.aggregate(
        all = Count('pk'),
        public = Count('pk', filter=Q(is_private=False)),
        private = Count('pk', filter=Q(is_private=True))
    )

    ProfileCount.objects.create(all = count['all'], public = count['public'], private = count['private'])


@shared_task
def send_email_to_user(subject, message, user_email):
    send_mail(
        subject,
        message,
        'test_social_media@example.com',
        [user_email]
    )
