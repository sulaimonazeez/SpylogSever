from django.db import models
from django.contrib.auth.models import User


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username}'s Wallet"


class IconModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.ImageField(upload_to="product_icons/")

    def __str__(self):
        return self.name


class ProductType(models.Model):
    name = models.CharField(max_length=255)  # Example: Facebook, VPN
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    icon = models.ForeignKey(IconModel, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def in_stock_count(self):
        return self.credentials.filter(is_sold=False).count()


class ProductCredential(models.Model):
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name="credentials")
    access_info = models.TextField(help_text="Multiple login:password lines or JSON")
    is_sold = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product_type.name} - Log #{self.id}"


class TransactionHistory(models.Model):
    STATUS_CHOICES = [
        ("completed", "Completed"),
        ("pending", "Pending"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductCredential, on_delete=models.SET_NULL, null=True, blank=True)
    product_type = models.ForeignKey(ProductType, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="completed")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product_type.name if self.product_type else 'Deleted'} - {self.status}"
        


class AccountDetails(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  account = models.CharField(max_length=255)
  bank_name = models.CharField(max_length=50)
  order_ref = models.CharField(max_length=100)
  
  def __str__(self):
    return f"{self.user.username} - {self.account}"
    
    

class FundHistory(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  amount = models.DecimalField(max_digits=10, decimal_places=2)
  reference = models.CharField(max_length=500)
  
  def __str__(self):
    return self.user.username
  
  
  


class Messages(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Latest messages appear first