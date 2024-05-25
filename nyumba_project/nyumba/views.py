from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest

from django.contrib.auth.decorators import login_required

from .forms import RegisterForm
import pandas as pd
import pickle

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
    # Load the model
    model_path = '/Users/wepukhulu/Desktop/Directory/yr4/Final-yrProject/hse_model.pickle'
    with open(model_path, 'rb') as model_file:
        model = pickle.load(model_file)
    
    # Load the scaler
    scaler_path = '/Users/wepukhulu/Desktop/Directory/yr4/Final-yrProject/scaler.pickle'
    with open(scaler_path, 'rb') as scaler_file:
        scaler = pickle.load(scaler_file)
    
    # Load the feature names
    with open('/Users/wepukhulu/Desktop/Directory/yr4/Final-yrProject/feature_names.txt', 'r') as f:
        feature_names = [line.strip() for line in f]
    
    # Define the category and location columns based on training data
    category_columns = [col for col in feature_names if col.startswith('Cat_')]
    location_columns = [col for col in feature_names if col.startswith('Loc_')]
    
    # Get form data
    category = request.GET.get('category')
    location = request.GET.get('location')
    beds = request.GET.get('beds')
    baths = request.GET.get('baths')
    
    # Check for missing data and return a bad request response if any parameter is missing
    if not category or not location or not beds or not baths:
        return HttpResponseBadRequest("Missing one or more required parameters.")
    
    # Convert to appropriate types
    try:
        beds = int(beds)
        baths = int(baths)
    except ValueError:
        return HttpResponseBadRequest("Invalid number format for beds or baths.")
    
    # Create DataFrame and preprocess data
    input_data = pd.DataFrame({
        'Beds': [beds],
        'Baths': [baths],
        'Category': [category],
        'Location': [location]
    })
    
    # One-hot encode categorical variables
    input_data = input_data.join(pd.get_dummies(input_data['Category'], prefix='Cat')).drop(['Category'], axis=1)
    input_data = input_data.join(pd.get_dummies(input_data['Location'], prefix='Loc')).drop(['Location'], axis=1)
    
    # Ensure all feature columns are present
    for cat_col in category_columns:
        if cat_col not in input_data.columns:
            input_data[cat_col] = 0
    for loc_col in location_columns:
        if loc_col not in input_data.columns:
            input_data[loc_col] = 0
    
    # Reorder columns to match training data
    input_data = input_data[['Beds', 'Baths'] + category_columns + location_columns]
    
    # Scale numerical features
    input_data[['Beds', 'Baths']] = scaler.transform(input_data[['Beds', 'Baths']])
    
    # Predict the price
    predicted_price = model.predict(input_data)
    
    # Render the result
    return render(request, 'base-app/shop-listing.html', {
        'predicted_price': predicted_price[0],
        'category': category,
        'location': location,
        'beds': beds,
        'baths': baths
    })