
from django.contrib import admin
from django.urls import path,include
from .views import user_list , create_user

urlpatterns = [
    path("user_list/",user_list, name="user_list"),
    path("create_user/",create_user,name="create_user"),
]
