from flask import request, render_template, Flask
import folium
from folium.plugins import AntPath

from geopy.geocoders import Nominatim
import sqlite3
import numpy as np
import datetime



locationMap = {}
citiesMap = {}
ReverseMap = {}

conn = sqlite3.connect('flights.db')
c = conn.cursor()
stime = datetime.datetime.now()
query = '''SELECT IATA, LATITUDE, LONGITUDE, CITY FROM airports'''
c.execute(query)
locs = c.fetchall()
for loc in locs:
    locationMap[loc[0]] = (loc[1:4])
    citiesMap[loc[0]] = loc[3]
    ReverseMap[loc[3]] = loc[0]
c.close()
conn.close()

# List of cities to display in the drop-down menu
cities_list = list(citiesMap.values())

app = Flask(__name__)


@app.route('/')
def index():
    # Render the HTML form with the list of cities
    map = folium.Map(location=[37.0902, -95.7129], zoom_start=3.5)
    hasMap = {}
    map_html = map.get_root().render()
    return render_template('map.html', map_html=map_html, hasMap=hasMap,hasMap2=hasMap, cities=cities_list)


@app.route('/map', methods=['GET','POST'])
def generate_map():
    # Get the selected cities from the form
    city1 = request.form['city1']
    city2 = request.form['city2']

    prevCity1 = request.form.get('city1')
    prevCity2 = request.form.get('city2')

    # execute the query
    conn = sqlite3.connect('flights.db')
    c = conn.cursor()
    query = '''SELECT UniqueCarrier,Cancelled, COUNT(*)
                FROM table2002 WHERE Origin=? AND  Dest=?
                GROUP BY UniqueCarrier, Cancelled
            '''
    c.execute(query, (ReverseMap[city1], ReverseMap[city2]))
    result = c.fetchall()
    data = {(t[0],t[1]) : t[2]  for t in result}
    hasMap = {k[0]: v for k, v in data.items() if k[1] == 0}
    hasMap2 = {k[0]: v for k, v in data.items() if k[1] == 1}

    map = folium.Map(location=[37.0902, -95.7129], zoom_start=4)
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

    #Time Optimized using try except
    # Draw a curved line between the two cities
    Total = sum(data.values())
    print(Total,city1,city2,ReverseMap[city1],ReverseMap[city2])
    if Total > 0:
        AntPath(
            locations=points,
            dash_array=[50, 30],
            delay=400,
            weight=2,
            color='#8E44AD',
            pulse_color='#FFC300',
            tooltip=f'{Total}'
        ).add_to(map)

    c.close()
    conn.close()
    map_html = map.get_root().render()

    return render_template('map.html',
                           map_html=map_html,
                           hasMap=hasMap,
                           hasMap2= hasMap2,
                           cities=cities_list,
                           prev_city1=prevCity1,
                           prev_city2=prevCity2
                           )


if __name__ == '__main__':
    app.run(debug=True)
