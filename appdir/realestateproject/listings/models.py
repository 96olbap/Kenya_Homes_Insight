from django.db import models

class House(models.Model):
    beds = models.FloatField()
    baths = models.FloatField()
    price = models.FloatField()
    location = models.CharField(max_length=100)
    bedroom_ratio = models.FloatField()

    def __str__(self):
        return f"{self.location} House with {self.beds} Beds and {self.baths} Baths"