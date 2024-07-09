from django.db import models

# Create your models here.
# from django.db import models

class UserProductOrderTable(models.Model):
    # user_id = models.IntegerField(auto_created=True)
    ordered_product_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_transaction_link = models.URLField(max_length=500, null=True, blank=True)
    # Add other fields as necessary

    def __str__(self):
        return self.user_id
# paypal_integration/models.py
from django.db import models

class Payment(models.Model):
    payment_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50)
    email = models.EmailField()
    account_id = models.CharField(max_length=255)
    account_status = models.CharField(max_length=50)
    payer_id = models.CharField(max_length=255)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    payment_country_code = models.CharField(max_length=3)

    def __str__(self):
        return self.payment_id
