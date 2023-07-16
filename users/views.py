from django.shortcuts import render, redirect
from users.forms import UserRegisterForm
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout
def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("Created Successfully")
        else:
            return render(request, 'users/register.html', {'form': form})
    else:
        form = UserRegisterForm()
        return render(request, 'users/register.html', {'form': form})


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username = username, password = password)
        if user is not None:
            login(request, user)
            return HttpResponse("user logged in successfully")
        else:
            return HttpResponse("Username or password does not exist")
    else:
        return render(request, "users/login.html")

def logout_user(request):
    if request.method == "POST":
        username = request.user.username
        logout(request)
        return HttpResponse("logged out successfully")
    else:
        return render(request, "users/logout.html", {"firstname": request.user.first_name})
