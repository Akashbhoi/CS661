from flask import Flask, render_template, request
import folium
from folium.plugins import AntPath
import pandas as pd
from geopy.geocoders import Nominatim
import sqlite3
import numpy as np



cities = pd.read_csv('../airports.csv')
citiesMap = {}
ReverseMap = {}
for i in range(1 , len(cities)):
    citiesMap[cities.iloc[i]["IATA"]] = cities.iloc[i]["CITY"]
    ReverseMap[cities.iloc[i]["CITY"]] = cities.iloc[i]["IATA"]


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
  
    # execute the query
    conn = sqlite3.connect('flights.db')
    c = conn.cursor()
    query = '''SELECT COUNT(*) FROM mytable WHERE origin=? AND dest=?'''
    c.execute(query,(ReverseMap[city1],ReverseMap[city2]))
    result = c.fetchone()[0]
    # print the result
    print(f"Number of entries where origin is {ReverseMap[city1]} and dest is {ReverseMap[city2]}: {result}")
    conn.close()

    # Get latitude and longitude coordinates for the cities
    geolocator = Nominatim(user_agent="my-app")
    location1 = geolocator.geocode(city1)
    location2 = geolocator.geocode(city2)

    # Create map centered on the US
    map = folium.Map(location=[37.0902, -95.7129], zoom_start=4)

    # Add markers for the selected cities
    marker1 = folium.Marker(location=[location1.latitude, location1.longitude], popup=city1)
    marker2 = folium.Marker(location=[location2.latitude, location2.longitude], popup=city2)

    marker1.add_to(map)
    marker2.add_to(map)

    # Draw a curved line between the two cities

   # Crea# Create polyline object for the curve
    points = np.array([[location1.latitude, location1.longitude], [location2.latitude, location2.longitude]])
    midpoint = points.mean(axis=0)

    AntPath(
        locations=points,
        dash_array=[50, 30],
        delay=800,
        weight=5,
        color='#8E44AD',
        pulse_color='#FFC300',
        tooltip='Curved Path'
    ).add_to(map)

    # Render the map.html file
    return render_template('map.html', map=map._repr_html_())


if __name__ == '__main__':
    app.run(debug=True)
    

