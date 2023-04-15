from flask import Flask, render_template, request
import folium
import pandas as pd
from geopy.geocoders import Nominatim

cities = pd.read_csv('../airports.csv')
citiesMap = {}
for i in range(1 , len(cities)):
    citiesMap[cities.iloc[i]["IATA"]] = cities.iloc[i]["CITY"]

# print(citiesMap)

app = Flask(__name__)


@app.route('/')
def index():
    # List of cities to display in the drop-down menu
    cities = citiesMap.values()

    # Render the HTML form with the list of cities
    return render_template('index.html', cities=cities)

@app.route('/map', methods=['POST'])
def generate_map():
    # Get the selected cities from the form
    city1 = request.form['city1']
    city2 = request.form['city2']

    # Get latitude and longitude coordinates for the cities
    geolocator = Nominatim(user_agent="my-app")
    location1 = geolocator.geocode(city1)
    location2 = geolocator.geocode(city2)

    print(location1.latitude)

    # Create map centered on the US
    map = folium.Map(location=[37.0902, -95.7129], zoom_start=4)

    # Add markers for the selected cities
    marker1 = folium.Marker(location=[location1.latitude, location1.longitude], popup=city1)
    marker2 = folium.Marker(location=[location2.latitude, location2.longitude], popup=city2)

    marker1.add_to(map)
    marker2.add_to(map)

    # Save the map as an HTML file and render it
    map.save('templates/map.html')
    return render_template('map.html')

if __name__ == '__main__':
    app.run(debug=True)
