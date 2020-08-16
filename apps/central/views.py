from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, "central/central.html")

def privacy(request):
    return render(request, "central/privacy.html")
