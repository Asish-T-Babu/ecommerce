from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid

from ecommerce_app.models.admin import Product
from ecommerce_app.utils import STATUS_CHOICES

USER_CURRENCY = (
    ('rupee', 'rupee'),
    ('dollar', 'dollar')
)

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
    user_currency = models.CharField(max_length=10, blank= True, null= True, choices= USER_CURRENCY)
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

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null= True, related_name= 'cart_user')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null= True, related_name='cart_product')
    quantity = models.PositiveIntegerField()
