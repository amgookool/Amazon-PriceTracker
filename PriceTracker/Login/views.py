from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
# Create your views here.
def LoginView(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username,password=password)
        if user is not None:
            login(request, user)
            return redirect('Home')
        else:
            # Return an Invalid Login error
            messages.error(request,"There was an error Logging into your Account")
            return redirect("Login")
    else:
        context = {}
        return render(request,'Login/Login.html', context=context)
