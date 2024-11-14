from flask import Flask, render_template, request, jsonify, redirect, url_for
from sklearn.linear_model import LinearRegression
import numpy as np
import requests

app = Flask(__name__)

# Predict cost function
def predict_cost(distance, fuel_efficiency, fuel_cost, vehicle_type):
    fuel_needed = distance / fuel_efficiency
    type_multiplier = {
        'car': 1.0,
        'truck': 2.0,
        'motorbike': 0.5
    }

    if vehicle_type not in type_multiplier:
        vehicle_type = 'car'  # Default to car if vehicle type is invalid

    total_cost = fuel_needed * fuel_cost * type_multiplier[vehicle_type]
    return total_cost

# User credentials for login
USER_CREDENTIALS = {
    "username": "admin",
    "password": "password123"
}
@app.route('/logout')
def logout(): 
    return render_template('username.html')
# Login route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == USER_CREDENTIALS['username'] and password == USER_CREDENTIALS['password']:
            return redirect(url_for('dashboard'))
        else:
            return render_template('username.html', error="Invalid username or password.")
    
    return render_template('username.html')

# Dashboard route (after login)
@app.route('/dashboard')
def dashboard():
    return render_template('index.html')
a=10
b=10
# Prediction route
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    try:
        global a,b
        distance = float(data['distance'])
        fuel_efficiency = float(data['fuelEfficiency'])
        fuel_cost = float(data['fuelCost'])
        vehicle_type = data['vehicleType']
        vehicle_type1 = data['from']
        vehicle_type2 = data['to']
        a=vehicle_type1
        b=vehicle_type2
        cost = predict_cost(distance, fuel_efficiency, fuel_cost, vehicle_type)
        
        return jsonify({'cost': round(cost, 2)})

    except KeyError as e:
        return jsonify({'error': f'Missing parameter: {str(e)}'}), 400
    except ValueError as e:
        return jsonify({'error': 'Invalid input value'}), 400

# Geocode function to get latitude and longitude
opencage_api_key = 'ea9407a7cf9f45eba3b131c944c44769'

def geocode_place(place_name):
    url = f'https://api.opencagedata.com/geocode/v1/json'
    params = {
        'q': place_name,
        'key': opencage_api_key,
        'limit': 1 
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            lat = data['results'][0]['geometry']['lat']
            lng = data['results'][0]['geometry']['lng']
            return lat, lng
        else:
            return None
    else:
        return None

# Map view route with dynamic place names
@app.route('/mapper')
def map_view():
    global a,b
    start_place = a
    end_place = b

    start_coords = geocode_place(start_place)
    end_coords = geocode_place(end_place)

    if start_coords and end_coords:
        start_lat, start_lng = start_coords
        end_lat, end_lng = end_coords
        
        # Constructing the Graphhopper URL
        gh_url = f"https://graphhopper.com/maps/?point={start_lat},{start_lng}&point={end_lat},{end_lng}&locale=en&vehicle=truck&weighting=fastest&elevation=false"
        
        return render_template('red.html', gh_url=gh_url)
    else:
        return "Failed to get coordinates for one or both places."

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
