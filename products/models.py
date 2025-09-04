from django.db import models

# Create your models here.

class Product(models.Model):
    title = models.CharField(max_length=255)
    image_url = models.URLField()
    description = models.TextField(blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    source = models.CharField(max_length=50)  # e.g. Amazon, Myntra
    product_url = models.URLField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.source}"
