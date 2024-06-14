from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    profile_photo = models.ImageField(upload_to='images/', blank=True, null=True)
    bio = models.CharField(max_length=60)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.bio

    def save_profile(self):
        self.save()

    def delete_profile(self):
        self.delete()
    
    class Meta:
        db_table = 'user_profile'

class Listing(models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=255, null=True, blank=True)  # Adjust based on your requirements
    location = models.CharField(max_length=255, null=True, blank=True)  # Adjust based on your requirements
    beds = models.IntegerField(null=True, blank=True)
    baths = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=2)  # Increased precision
    
    def __str__(self):
        return f"{self.location} House with {self.beds} Beds and {self.baths} Baths"

    class Meta:
        db_table = 'house_listing'