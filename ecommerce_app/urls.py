from django.urls import path
from ecommerce_app.views.user import *

urlpatterns = [
    # user views
    path('create_user/', create_user, name='create_user'),
    path('login/', login, name= 'login'),
    
]
