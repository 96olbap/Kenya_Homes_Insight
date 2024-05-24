from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required

from .forms import RegisterForm
import pandas as pd

# Create your views here.

def home(request):
    return render(request, 'base-app/home.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/signup.html', {'form':form})

def predict(request):
    model = pd.read_pickle('hse_model.pickle')

    category = request.GET['category']
    location = request.GET['location']
    beds = request.GET['beds']
    baths = request.GET['baths']

    prd_data = pd.DataFrame({
        'category': [category],
        'location': [location],
        'beds': [int(beds)],
        'baths': [int(baths)]
    })

    predicted_price = model.predict(prd_data)

    return render(request, 'base-app/shop-listing.html')
