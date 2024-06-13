from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .forms import RegisterForm
import pandas as pd
import pickle
from .models import Listing

from django.core.mail import send_mail
from django.contrib import messages

import folium
from django.shortcuts import render
from geopy.geocoders import Nominatim
import time
from django.db.models import Avg, Count
import json
import numpy as np


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
    
    # Format the predicted price to remove decimal points and include commas
    formatted_price = "Ksh. {:,}".format(int(round(predicted_price[0])))
    
    # Print parameters used in the database query
    print("Category:", category)
    print("Location:", location)
    print("Predicted Price:", formatted_price)
    
    # Query the database for listings within the predicted price range
    price_variation_range = 23800000  # Adjust as necessary
    listings = Listing.objects.filter(
        category=category,
        location=location,
        price__gte=predicted_price[0] - price_variation_range,
        price__lte=predicted_price[0] + price_variation_range
    )[:2]

    # Calculate analytics for the location
    location_listings = Listing.objects.filter(location=location)
    if location_listings.exists():
        avg_price = location_listings.aggregate(Avg('price'))['price__avg']
        prices = list(location_listings.values_list('price', flat=True))
        median_price = np.median(prices) if prices else None
        listing_count = location_listings.count()
        price_distribution = prices

        # Average price by number of bedrooms
        avg_price_by_bedrooms = location_listings.values('beds').annotate(avg_price=Avg('price')).order_by('beds')
        avg_price_by_bathrooms = location_listings.values('baths').annotate(avg_price=Avg('price')).order_by('baths')

        # Distribution of listings by price range
        bins = [0, 5000000, 10000000, 20000000, 50000000, 100000000]
        labels = ['<5M', '5M-10M', '10M-20M', '20M-50M', '>50M']
        price_distribution_by_range = pd.cut(prices, bins=bins, labels=labels).value_counts().to_dict()

        # Average price by category
        avg_price_by_category = location_listings.values('category').annotate(avg_price=Avg('price')).order_by('category')

        # Correlation analysis
        correlation_matrix = pd.DataFrame(location_listings.values('beds', 'baths', 'price')).corr().round(2).to_dict()

    else:
        avg_price = median_price = listing_count = price_distribution = None
        avg_price_by_bedrooms = avg_price_by_bathrooms = price_distribution_by_range = avg_price_by_category = correlation_matrix = []

    # Print the resulting queryset
    print("Query Result:", listings)
    
    # Render the result with listings and analytics
    return render(request, 'base-app/shop-listing.html', {
        'predicted_price': formatted_price,
        'category': category,
        'location': location,
        'beds': beds,
        'baths': baths,
        'listings': listings,
        'avg_price': avg_price,
        'median_price': median_price,
        'listing_count': listing_count,
        'price_distribution': json.dumps(price_distribution),  # Convert to JSON string for JavaScript
        'avg_price_by_bedrooms': json.dumps(list(avg_price_by_bedrooms), default=str),
        'avg_price_by_bathrooms': json.dumps(list(avg_price_by_bathrooms), default=str),
        'price_distribution_by_range': json.dumps(price_distribution_by_range),
        'avg_price_by_category': json.dumps(list(avg_price_by_category), default=str),
        'correlation_matrix': json.dumps(correlation_matrix)
    })


def contact(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Handle form data here (e.g., save to database, send email)
        send_mail(
            f"Contact form submission from {first_name} {last_name}",
            message,
            email,
            ['alvin858rpk@gmail.com'],
            fail_silently=False,
        )

        messages.success(request, 'Your message has been sent successfully!')
        return HttpResponseRedirect(reverse('contact'))

    return render(request, 'base-app/contact.html')


# def predict(request):
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
    
    # Format the predicted price to remove decimal points and include commas
    formatted_price = "Ksh. {:,}".format(int(round(predicted_price[0])))
    
    # Print parameters used in the database query
    print("Category:", category)
    print("Location:", location)
    print("Predicted Price:", formatted_price)
    
    # Query the database for listings within the predicted price range
    price_variation_range = 23800000  # Adjust as necessary
    listings = Listing.objects.filter(
        category=category,
        location=location,
        price__gte=predicted_price[0] - price_variation_range,
        price__lte=predicted_price[0] + price_variation_range
    )[:2]
    
    # Query the database for all listings with the same location
    location_listings = Listing.objects.filter(location=location)
    
    # Generate a map
    map_center = [location_listings[0].latitude, location_listings[0].longitude] if location_listings else [0, 0]
    map = folium.Map(location=map_center, zoom_start=13)
    
    for listing in location_listings:
        folium.Marker(
            location=[listing.latitude, listing.longitude],
            popup=f"{listing.title}: Ksh. {listing.price:,}"
        ).add_to(map)
    
    # Save the map as an HTML file
    map_file_path = '/Users/wepukhulu/Desktop/Directory/yr4/Final-yrProject/map.html'
    map.save(map_file_path)
    
    # Print the resulting queryset
    print("Query Result:", listings)
    
    # Render the result with listings and map
    return render(request, 'base-app/shop-listing.html', {
        'predicted_price': formatted_price,
        'category': category,
        'location': location,
        'beds': beds,
        'baths': baths,
        'listings': listings,
        'map_file_path': map_file_path
    })

# def fetch_coordinates(locations):
#     geolocator = Nominatim(user_agent="geoapiExercises")
#     coordinates = {}
#     for location in locations:
#         try:
#             loc_data = geolocator.geocode(location, timeout=10)
#             if loc_data:
#                 coordinates[location] = (loc_data.latitude, loc_data.longitude)
#             else:
#                 coordinates[location] = (None, None)
#         except Exception as e:
#             coordinates[location] = (None, None)
#         time.sleep(1)  # Pause to avoid overloading the geocode API
#     return coordinates

# def create_map(coordinates):
#     map = folium.Map(location=[-1.2921, 36.8219], zoom_start=10)  # Centered around Nairobi
#     for loc, coord in coordinates.items():
#         if coord[0] is not None and coord[1] is not None:
#             folium.Marker(
#                 location=[coord[0], coord[1]],
#                 popup=loc,
#                 icon=folium.Icon(icon="info-sign")
#             ).add_to(map)
#     return map

# def predict(request):