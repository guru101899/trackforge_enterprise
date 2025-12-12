from xxlimited import Str

from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse

from .models import CustomUser
from .forms import CustomUserForm


# def user_list(request):
#     users = list(CustomUser.objects.values("first_name", "last_name", "email"))
#     return JsonResponse({"users": users})

def user_list(request):
    users = CustomUser.objects.all()
    return render(request,"user_list.html",{"users":users})

def create_user(request):
    if request.method == "POST":
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/accounts/user_list")

    else:
        form = CustomUserForm()
    return render(request,"create_user.html",{"form":form})


