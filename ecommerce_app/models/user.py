from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid

from ecommerce_app.models.admin import Product
from ecommerce_app.utils import STATUS_CHOICES, USER_CURRENCY, ADDRESS_TYPES, ORDER_STATUS


class UsersManager(BaseUserManager):

    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have an email address.')
        
        if not password:
            raise ValueError('Users must have a password.')

        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        kwargs.setdefault('is_admin', True)
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superadmin', True)

        return self.create_user(email, password, **kwargs)


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    region_code = models.CharField(max_length=10, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    first_name = models.CharField(max_length=256, blank=True, null=True)
    last_name = models.CharField(max_length=256, blank=True, null=True)
    user_currency = models.CharField(max_length=10, blank= True, null= True, choices=USER_CURRENCY)
    profile_image = models.ImageField(blank=True, null=True, upload_to='media/profile_image/')

    is_superadmin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    status = models.PositiveIntegerField(default= STATUS_CHOICES[1][0], choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UsersManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    def has_perm(self, perm, obj=None):
        return self.is_superadmin

    def has_module_perms(self, app_label):
        return self.is_superadmin

    @property
    def get_full_name(self):
        return f'{self.first_name} {self.last_name if self.last_name else ""}'.strip()


    def __str__(self):
        return self.email

class Address(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=256)
    phone = models.PositiveBigIntegerField()
    pincode = models.CharField(max_length=10)
    locality = models.CharField(max_length=256)
    city = models.CharField(max_length=256)
    state = models.CharField(max_length=256)
    land_mark = models.TextField(null=True, blank=True)
    alternative_phone = models.PositiveBigIntegerField(null=True, blank=True)
    address_type = models.IntegerField(null=True, blank=True, choices=ADDRESS_TYPES)
    status = models.PositiveBigIntegerField(default=STATUS_CHOICES[1][0], choices= STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null= True, related_name= 'cart_user')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null= True, related_name='cart_product')
    quantity = models.PositiveIntegerField()
    status = models.PositiveBigIntegerField(default=STATUS_CHOICES[1][0], choices=STATUS_CHOICES)
    session_id = models.CharField(max_length=256, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ProductPurchase(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="productpurchase_user")
    address =  models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='productpurchase_address')
    Product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='productpurchase_product')
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    payment_status = models.BooleanField(default=False)
    order_status = models.IntegerField(default=ORDER_STATUS[0][0], choices=ORDER_STATUS)
    status = models.PositiveBigIntegerField(default=STATUS_CHOICES[1][0], choices= STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
