import re
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.http import Http404, request
from django.urls import reverse

# Create your models here.
class Profile(models.Model):
    '''Model that defines a user profile and its methods'''
    user = models.OneToOneField(User,related_name='profile', on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to='images/', blank=True, null=True)
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length = 10,blank =True)
        
    @classmethod
    def get_profiles(cls):
        '''Retrieves all the profile instances from the database'''
        return cls.objects.all()

    @classmethod
    def get_single_profile(cls,profile_id):
        '''Retrieves a single profile instance from the database by id'''
        try:
            return cls.objects.filter(id=profile_id).get()
        except Profile.DoesNotExist:
            return Http404

    def get_absolute_url(self):
        return reverse('profile', kwargs={'pk': self.pk})   

    def __str__(self):
        return self.user.username
    
class Wishlist(models.Model):
    '''Model that defines the properties user adds to withlist'''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listings = models.ManyToManyField('listinds.Listing') # referencing Listing model in listings app