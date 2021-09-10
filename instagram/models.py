from django.db import models
from django.db.models.deletion import CASCADE

# Create your models here.
class Profile(models.Model):
    photo=models.ImageField(upload_to='mages')
    bio=models.TextField(max_length=1200)


class Image(models.Model):
    profile=models.ForeignKey(Profile,on_delete=CASCADE)
    image=models.ImageField(upload_to='images')
    name=models.CharField(max_length=30)
    caption=models.CharField(max_length=30)
    likes=models.IntegerField(default=0)
    comments=models.TextField(max_length=200)
