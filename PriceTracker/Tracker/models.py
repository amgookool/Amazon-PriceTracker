from django.db import models

# Create your models here.
class Product(models.Model):
    prod_url = models.URLField(verbose_name="Product URL", max_length=500)
    name = models.CharField(verbose_name="Product Name", max_length=300)
    img_url = models.URLField(verbose_name="Product Image URL", max_length=500)
    price = models.DecimalField(verbose_name="Product Price", decimal_places=2, max_digits=10)
    price_updated = models.DateTimeField(verbose_name="Last Updated Price", auto_now=True)

    def __str__(self) -> str:
        return self.name

class UserAgent(models.Model):
    user_agent = models.CharField(verbose_name="User Agent",max_length=200)

    def __str__(self) -> str:
        return self.user_agent


