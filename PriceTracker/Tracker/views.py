from django.shortcuts import render, redirect
from .models import UserAgent

# Create your views here.
def HomeView(request):
    context = {}
    return render(request,'Tracker/Home.html',context=context)

def SettingsView(request):
    user_agents = UserAgent.objects.all()
    agents = [a for a in user_agents]
    context = {"uagents" :agents }
    return render(request,'Tracker/Settings.html',context=context)

def TrackingView(request):
    context = {}
    return render(request,'Tracker/Tracking.html',context=context)
