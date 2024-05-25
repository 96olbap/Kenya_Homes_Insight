import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import time
import folium
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import pickle

def read_data(file_path):
    try:
        data = pd.read_csv(file_path, sep=';')
        print("Data loaded successfully.")
        return data
    except Exception as e:
        print("An error occurred while loading the data:", e)
        return None

def fetch_coordinates(locations):
    geolocator = Nominatim(user_agent="geoapiExercises")
    coordinates = {}
    for location in locations:
        try:
            loc_data = geolocator.geocode(location, timeout=10)
            if loc_data:
                coordinates[location] = (loc_data.latitude, loc_data.longitude)
            else:
                coordinates[location] = (None, None)
        except Exception as e:
            coordinates[location] = (None, None)
        time.sleep(1)  # Pause to avoid overloading the geocode API
    return coordinates

def create_map(coordinates):
    map = folium.Map(location=[-1.2921, 36.8219], zoom_start=10)  # Centered around Nairobi
    for loc, coord in coordinates.items():
        if coord[0] is not None and coord[1] is not None:
            folium.Marker(
                location=[coord[0], coord[1]],
                popup=loc,
                icon=folium.Icon(icon="info-sign")
            ).add_to(map)
    return map

def preprocess_data(data):
    imputer = SimpleImputer(strategy='median')
    data[['Beds', 'Baths']] = imputer.fit_transform(data[['Beds', 'Baths']])
    
    scaler = StandardScaler()
    data[['Beds', 'Baths']] = scaler.fit_transform(data[['Beds', 'Baths']])
    
    data = data.join(pd.get_dummies(data['Category'], prefix='Cat')).drop(['Category'], axis=1)
    data = data.join(pd.get_dummies(data['Location'], prefix='Loc')).drop(['Location'], axis=1)
    data = data.drop(['Title'], axis=1)
    
    return data, scaler

def split_data(data):
    x = data.drop(['Price'], axis=1)
    y = data['Price']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)
    return x_train, x_test, y_train, y_test

def train_linear_regression(x_train, y_train):
    model = LinearRegression()
    model.fit(x_train, y_train)
    return model

def train_random_forest(x_train, y_train):
    forest = RandomForestRegressor()
    param_grid = {"n_estimators": [3, 10, 30], "max_features": [2, 4, 6, 8]}
    grid_search = GridSearchCV(forest, param_grid, cv=5, scoring="neg_mean_squared_error", return_train_score=True)
    fn = grid_search.fit(x_train, y_train)

    pd.to_pickle(fn, 'hse_model.pickle')

    return fn.best_estimator_

def evaluate_model(model, x_test, y_test):
    return model.score(x_test, y_test)

def predict_price(model, scaler, category_columns, location_columns):
    user_input = {}
    user_input['Beds'] = float(input("Enter the number of beds: "))
    user_input['Baths'] = float(input("Enter the number of baths: "))
    user_input['Category'] = input(f"Enter the category ({', '.join(category_columns)}): ")
    user_input['Location'] = input(f"Enter the location ({', '.join(location_columns)}): ")

    input_df = pd.DataFrame([user_input])
    
    input_df = input_df.join(pd.get_dummies(input_df['Category'], prefix='Cat')).drop(['Category'], axis=1)
    input_df = input_df.join(pd.get_dummies(input_df['Location'], prefix='Loc')).drop(['Location'], axis=1)
    
    for cat_col in category_columns:
        if f'Cat_{cat_col}' not in input_df.columns:
            input_df[f'Cat_{cat_col}'] = 0
    for loc_col in location_columns:
        if f'Loc_{loc_col}' not in input_df.columns:
            input_df[f'Loc_{loc_col}'] = 0

    input_df = input_df[['Beds', 'Baths'] + [f'Cat_{col}' for col in category_columns] + [f'Loc_{col}' for col in location_columns]]
    
    input_df[['Beds', 'Baths']] = scaler.transform(input_df[['Beds', 'Baths']])
    
    predicted_price = model.predict(input_df)
    return predicted_price[0]

if __name__ == "__main__":
    data_path = "real_estate_nrb_cleaned.csv"
    data = read_data(data_path)
    if data is not None:
        unique_locations = data['Location'].unique().tolist()
        coordinates = fetch_coordinates(unique_locations)
        print("Coordinates fetched:", coordinates)
        
        map = create_map(coordinates)
        map.save('map.html')  # Save the map as an HTML file

        data, scaler = preprocess_data(data)
        
        # Save the scaler
        with open('scaler.pickle', 'wb') as f:
            pickle.dump(scaler, f)
        
        # Save the feature names
        feature_names = data.columns.tolist()
        with open('feature_names.txt', 'w') as f:
            for feature in feature_names:
                f.write(f"{feature}\n")

        x_train, x_test, y_train, y_test = split_data(data)
        lin_reg = train_linear_regression(x_train, y_train)
        rf_model = train_random_forest(x_train, y_train)
        print("Linear Regression Score:", evaluate_model(lin_reg, x_test, y_test))
        print("Random Forest Score:", evaluate_model(rf_model, x_test, y_test))

        category_columns = [col.split('_', 1)[1] for col in data.columns if col.startswith('Cat_')]
        location_columns = [col.split('_', 1)[1] for col in data.columns if col.startswith('Loc_')]
        
        while True:
            predicted_price = predict_price(rf_model, scaler, category_columns, location_columns)
            print(f"The predicted price is: {predicted_price}")

            another_prediction = input("Would you like to check another house? (yes/no): ").strip().lower()
            if another_prediction != 'yes':
                print("Exiting prediction loop.")
                break
