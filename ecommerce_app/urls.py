from django.urls import path

from ecommerce_app.views.user import *
from ecommerce_app.views.admin import *

urlpatterns = [
    # user views
    # User API's
    path('create_user/', create_user, name='create_user'),
    path('login/', login, name= 'login'),
    path('user_list/', user_list, name= 'user_list'),
    path('get_user/<uuid:user_id>/', get_user, name= 'get_user'),
    path('update_user/<uuid:user_id>/', update_user, name= 'update_user'),
    path('delete_user/<uuid:user_id>/', delete_user, name= 'delete_user'),

    # admin views
    # Brand API's
    path('brands/', BrandListCreateView.as_view(), name='brand_list_create'),
    path('brands/<uuid:pk>/', BrandRetrieveUpdateDestroyView.as_view(), name='brand_detail'),
    
    # Category API's
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<uuid:pk>/', CategoryRetrieveUpdateDestroyView.as_view(), name='category-detail'),

]
