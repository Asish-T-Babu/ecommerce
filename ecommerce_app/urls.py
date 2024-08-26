from django.urls import path
from ecommerce_app.views.user import *

urlpatterns = [
    # user views
    path('create_user/', create_user, name='create_user'),
    path('login/', login, name= 'login'),
    path('user_list/', user_list, name= 'user_list'),
    path('get_user/<uuid:user_id>/', get_user, name= 'get_user'),
    path('update_user/<uuid:user_id>/', update_user, name= 'update_user'),
    path('delete_user/<uuid:user_id>/', delete_user, name= 'delete_user'),
    
]
