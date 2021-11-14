from django.shortcuts import render, redirect

# Create your views here.
def HomeView(request):
    context = {}
    return render(request,'Tracker/Home.html',context=context)
