
from django.urls import path
from .views import *

urlpatterns = [
    path("user_list/",user_list, name="user_list"),
    path("register_user/",register_user,name="register_user"),
    path("login/",login,name="login"),
    path("logout/",logout,name="logout"),
    path("update_user/<int:pk>/",update_user,name="update_user"),
    path("delete_user/<int:pk>/",delete_user,name="delete_user"),

]
