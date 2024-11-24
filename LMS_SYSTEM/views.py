# LMS_SYSTEM/views.py

from django.shortcuts import render

def home_view(request):
    return render(request, 'home.html')  # Create a 'home.html' template for this
