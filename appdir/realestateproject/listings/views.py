from django.shortcuts import render
from django.http import JsonResponse
from .models import House

def search(request):
    beds = request.GET.get('beds', 0)
    baths = request.GET.get('baths', 0)
    location = request.GET.get('location', '')

    houses = House.objects.filter(beds__gte=beds, baths__gte=baths, location__icontains=location)
    data = list(houses.values())
    return JsonResponse(data, safe=False)