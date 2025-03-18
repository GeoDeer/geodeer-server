from django.shortcuts import render, redirect

# Create your views here.
# game/views.py
from django.http import HttpResponse

def index(request):
    return HttpResponse("GeoDeer!")

def create(request):
    return render(request, 'game/create.html')

def monitor(request):
    
    return render(request, 'game/monitor.html')
