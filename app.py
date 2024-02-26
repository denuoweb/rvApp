from flask import Flask, render_template, request, current_app
import googlemaps
from datetime import datetime
import math
import requests

# Initialize Flask app
app = Flask(__name__, template_folder='template')

# Configuration
app.config['GOOGLE_MAPS_API_KEY'] = ''  # Ideally set in environment or config file

# Google Maps Client Initialization
def get_gmaps_client():
    return googlemaps.Client(key=current_app.config['GOOGLE_MAPS_API_KEY'])

# Utility Functions
def miles_to_km(miles):
    return miles * 1.60934

def haversine_distance(lat1, lon1, lat2, lon2):
    radius = 6371  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = radius * c
    return distance

def decode_polyline(polyline_str):
    index, lat, lng = 0, 0, 0
    coordinates = []

    while index < len(polyline_str):
        lat += _decode_chunk(polyline_str, index)
        index += _chunk_length(polyline_str, index)
        lng += _decode_chunk(polyline_str, index)
        index += _chunk_length(polyline_str, index)
        coordinates.append((lat / 1e5, lng / 1e5))

    return coordinates

def _decode_chunk(polyline_str, index):
    shift, result, b = 0, 0, 0x20
    while b >= 0x20:
        b = ord(polyline_str[index]) - 63
        index += 1
        result |= (b & 0x1f) << shift
        shift += 5
    delta = result >> 1
    return delta if (result & 1) == 0 else ~delta

def _chunk_length(polyline_str, index):
    shift, b = 0, 0x20
    while b >= 0x20:
        b = ord(polyline_str[index]) - 63
        index += 1
        shift += 5
    return shift // 5  # The number of iterations corresponds to the chunk length.


# Business Logic
def get_current_weather(lat, lng):
    # Base URL for the NWS API
    base_url = "https://api.weather.gov"
    
    # Find the nearest observation station
    points_url = f"{base_url}/points/{lat},{lng}"
    headers = {"User-Agent": "YourAppName contact@example.com"}
    points_response = requests.get(points_url, headers=headers).json()
    station_url = points_response['properties']['observationStations']
    
    # Fetch the list of observation stations
    stations_response = requests.get(station_url, headers=headers).json()
    if stations_response['observationStations']:
        # Use the first station in the list for simplicity
        station_id = stations_response['observationStations'][0].split("/")[-1]
        
        # Get the latest observation for the station
        observation_url = f"{base_url}/stations/{station_id}/observations/latest"
        observation_response = requests.get(observation_url, headers=headers).json()
        
        # Extract weather information
        weather = observation_response['properties']['textDescription']
        temperature_celsius = observation_response['properties']['temperature']['value']
        
        # Check if temperature is available before conversion
        if temperature_celsius is not None:
            temperature_fahrenheit = temperature_celsius * (9/5) + 32
            temperature_fahrenheit = round(temperature_fahrenheit, 2)  # Optional: round to 2 decimal places
            return f"Weather: {weather}, Temperature: {temperature_fahrenheit}°F"
        else:
            return f"Weather: {weather}, Temperature data not available"
    else:
        return "Weather data not available"

    
def find_cities_and_hotels(points, interval_km):
    cities_hotels_info = []
    cumulative_distance = 0
    overflow_distance = 0

    for i in range(1, len(points)):
        distance = haversine_distance(*points[i-1], *points[i])
        cumulative_distance += distance

        if cumulative_distance >= interval_km:
            overflow_distance = cumulative_distance - interval_km
            cumulative_distance = overflow_distance
            location = {'lat': points[i][0], 'lng': points[i][1]}
            city_name = reverse_geocode_location(location)
            hotels_info = fetch_nearby_hotels(location)
            weather_info = get_current_weather(points[i][0], points[i][1])

            cities_hotels_info.append({
                'city': city_name,
                'hotels': hotels_info,
                'weather': weather_info  # Include weather information
            })

    return cities_hotels_info

def reverse_geocode_location(location):
    gmaps = get_gmaps_client()
    try:
        # Broadening the scope to include various types of location results
        reverse_geocode_result = gmaps.reverse_geocode((location['lat'], location['lng']), result_type=["locality", "political", "administrative_area_level_1", "administrative_area_level_2"])
        
        # Improved logic to find the most appropriate location name
        for result in reverse_geocode_result:
            if "locality" in result["types"]:
                return result.get("formatted_address", "Unknown Location")
            elif "administrative_area_level_1" in result["types"]:
                return result.get("formatted_address", "Unknown Location")
            elif "administrative_area_level_2" in result["types"]:
                return result.get("formatted_address", "Unknown Location")
        return "Unknown Location"  # Return this if no suitable type was found
    except Exception as e:
        current_app.logger.error(f"Error during reverse geocoding: {e}")
        return "Reverse Geocoding Error"


def fetch_nearby_hotels(location):
    gmaps = get_gmaps_client()
    try:
        places_result = gmaps.places_nearby(location=location, radius=10000, type='lodging')
        hotels = [place['name'] for place in places_result.get('results', [])[:5]]  # Limit to top 5 hotels
        return hotels
    except Exception as e:
        current_app.logger.error(f"Error fetching nearby hotels: {e}")
        return ["Hotel fetching error"]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_address = request.form['start']
        end_address = request.form['end']
        mode = request.form.get('mode', 'driving')
        interval = miles_to_km(float(request.form['interval']))
        
        # Process waypoints
        waypoints_text = request.form.get('waypoints', '')
        waypoints = [wp.strip() for wp in waypoints_text.split(';') if wp.strip()]  # Split and strip waypoints

        gmaps = get_gmaps_client()
        directions_result = gmaps.directions(start_address, 
                                              end_address, 
                                              mode=mode, 
                                              waypoints=waypoints if waypoints else None, 
                                              optimize_waypoints=True, 
                                              departure_time=datetime.now())

        if directions_result:
            polyline = directions_result[0]['overview_polyline']['points']
            points = decode_polyline(polyline)
            cities_hotels_info = find_cities_and_hotels(points, interval)

            distance = directions_result[0]['legs'][0]['distance']['text']
            duration = directions_result[0]['legs'][0]['duration']['text']

            return render_template('results.html', distance=distance, duration=duration, cities_hotels_info=cities_hotels_info, interval=interval / 1.60934)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=False)
