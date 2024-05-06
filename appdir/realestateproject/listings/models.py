from django.db import models

class Listing(models.Model):
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    beds = models.FloatField()
    baths = models.FloatField()
    price = models.FloatField()
    
    def __str__(self):
        return f"{self.location} House with {self.beds} Beds and {self.baths} Baths"