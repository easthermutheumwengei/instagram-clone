from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    photo = models.ImageField(upload_to='images')
    bio = models.TextField(max_length=1200)
    followers = models.ManyToManyField(User, related_name='followers')
    following = models.ManyToManyField(User, related_name='following')

    @receiver(post_save, sender=User)
    def update_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)
        try:
            instance.profile.save()
        except AttributeError:
            pass


class Comment(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, related_name='commentor')
    comment = models.TextField(max_length=200)
    created_at = models.DateTimeField(default=timezone.now)


class Image(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, related_name='profile')
    image = models.ImageField(upload_to='images')
    caption = models.CharField(max_length=300)
    likes = ArrayField(models.IntegerField(), default=list)
    comment = models.ManyToManyField(Comment)
    created_at = models.DateTimeField(default=timezone.now)
