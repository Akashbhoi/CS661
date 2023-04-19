from flask import request, render_template, Flask
import folium
from folium.plugins import AntPath
import pandas as pd
from geopy.geocoders import Nominatim
import sqlite3
import numpy as np
import datetime

cities = pd.read_csv('airports.csv')
citiesMap = {}
ReverseMap = {}
locationMap = {}
for i in range(1, len(cities)):
    citiesMap[cities.iloc[i]["IATA"]] = cities.iloc[i]["CITY"]
    ReverseMap[cities.iloc[i]["CITY"]] = cities.iloc[i]["IATA"]

conn = sqlite3.connect('flights.db')
c = conn.cursor()
stime = datetime.datetime.now()
query = '''SELECT IATA, LATITUDE, LONGITUDE, CITY FROM airports'''
c.execute(query)
locs = c.fetchall()
for loc in locs:
    locationMap[loc[0]] = (loc[1:4])
c.close()
conn.close()

app = Flask(__name__)


@app.route('/')
def index():
    # List of cities to display in the drop-down menu
    cities_list = list(citiesMap.values())
    # Render the HTML form with the list of cities
    return render_template('index.html', cities=cities_list)


@app.route('/map', methods=['POST'])
def generate_map():
    # Get the selected cities from the form
    city1 = request.form['city1']
    city2 = request.form['city2']

    # execute the query
    conn = sqlite3.connect('flights.db')
    c = conn.cursor()
    query = '''SELECT COUNT(*) FROM table2002 WHERE origin=? AND dest=?'''
    c.execute(query, (ReverseMap[city1], ReverseMap[city2]))
    result = c.fetchone()[0]

    # Create map centered on the US
    map = folium.Map(location=[37.0902, -95.7129], zoom_start=4)

    sTime = datetime.datetime.now()
    points = None
    try:
        loc1 = locationMap[ReverseMap[city1]]
        loc2 = locationMap[ReverseMap[city2]]

        marker1 = folium.Marker(location=[loc1[0],loc1[1]],popup=city1)
        marker2 = folium.Marker(location=[loc2[0],loc2[1]],popup=city2)
        points = np.array([[loc1[0],loc1[1]],[loc2[0],loc2[1]]])
        marker1.add_to(map)
        marker2.add_to(map)

    except KeyError:
        geolocator = Nominatim(user_agent="my-app")
        location1 = geolocator.geocode(city1)
        location2 = geolocator.geocode(city2)

        # Add markers for the selected cities
        marker1 = folium.Marker(location=[location1.latitude, location1.longitude], popup=city1)
        marker2 = folium.Marker(location=[location2.latitude, location2.longitude], popup=city2)
        points = np.array([[location1.latitude, location1.longitude], [location2.latitude, location2.longitude]])
        marker1.add_to(map)
        marker2.add_to(map)

    print(datetime.datetime.now()-sTime)
    #Time Optimized using
    # Draw a curved line between the two cities
    AntPath(
        locations=points,
        dash_array=[50, 30],
        delay=800,
        weight=5,
        color='#8E44AD',
        pulse_color='#FFC300',
        tooltip=f'{result}'
    ).add_to(map)
    #
    # query = '''SELECT UniqueCarrier, COUNT(*) as num_flights
    #   FROM table2002 WHERE Origin=? AND Dest=?
    #   GROUP BY UniqueCarrier
    #   ORDER BY num_flights DESC
    #   LIMIT 11
    # '''
    # c.execute(query, (ReverseMap[city1], ReverseMap[city2]))
    # result = c.fetchall()
    # hasMap = {k: v for k, v in result}
    # print(city1,city2,hasMap)

    conn.close()

    map.save('./templates/map.html')
    return render_template('map.html')


if __name__ == '__main__':
    app.run(debug=True)
