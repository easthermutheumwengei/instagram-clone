from django.contrib.auth.models import User
from django.db import models
from django.db.models.deletion import CASCADE

# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,null=True)
    photo=models.ImageField(upload_to='mages')
    bio=models.TextField(max_length=1200)
    followers=models.ManyToManyField(User,related_name='followers')
    following=models.ManyToManyField(User,related_name='following')
@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

class Image(models.Model):
    profile=models.ForeignKey(Profile,on_delete=models.CASCADE,null=True)
    image=models.ImageField(upload_to='images')
    name=models.CharField(max_length=30)
    caption=models.CharField(max_length=30)
    likes=models.IntegerField(default=0)
    comments=models.TextField(max_length=200)

