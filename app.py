from flask import request, render_template, Flask
import folium
import plotly.offline as plot
from folium.plugins import AntPath
from geopy.geocoders import Nominatim
import sqlite3
import numpy as np
import datetime
import plotly.graph_objs as go

metaData = {}
metaData2 = {}
locationMap = {}
citiesMap = {}
citiesMap2 = {}
ReverseMap = {}
AirlineMap = {}
conn = sqlite3.connect('flights.db')
c = conn.cursor()
query = '''SELECT IATA, LATITUDE, LONGITUDE, CITY, AIRPORT FROM airports'''
c.execute(query)
locs = c.fetchall()
for loc in locs:
    IATA = loc[0]
    latitude = loc[1]
    longitude = loc[2]
    city = loc[3]
    airport = loc[4]

    locationMap[IATA] = (loc[1:4])
    citiesMap[IATA] = f'{city} ({IATA})'
    citiesMap2[IATA] = city
    ReverseMap[f'{city} ({IATA})'] = IATA

query = '''SELECT Code,Description FROM airlines'''
c.execute(query)
result = c.fetchall()
for row in result:
    AirlineMap[row[0]] = row[1]
c.close()
conn.close()
# print(AirlineMap)
# List of cities to display in the drop-down menu
cities_list = list(citiesMap.values())

# List of years to display in the drop-down menu
years_list = [str(year) for year in range(1988, 2009)]

app = Flask(__name__)


@app.route('/')
def index():
    # Render the HTML form with the list of cities and years
    map = folium.Map(location=[37.0902, -95.7129], zoom_start=3.5)
    hasMap = {}
    map_html = map.get_root().render()
    return render_template('map.html', map_html=map_html, hasMap=hasMap, hasMap2=hasMap, cities=cities_list,
                           years=years_list)


@app.route('/map', methods=['GET', 'POST'])
def generate_map():
    # Get the selected cities and year from the form
    city1 = request.form['city1']
    year = request.form['year']

    prevCity1 = request.form.get('city1')
    prevYear = request.form.get('year')

    # execute the query
    startTime = datetime.datetime.now()
    conn = sqlite3.connect('flights.db')
    c = conn.cursor()
    query = f'''
    SELECT Dest,COUNT(*) FROM table{year} WHERE Origin=? GROUP BY Dest;
    '''
    c.execute(query, (ReverseMap[city1],))
    result1 = c.fetchall()
    print(f'TIME TAKEN TO FETCH 1: {datetime.datetime.now() - startTime}')
    map = folium.Map(location=[37.0902, -95.7129], zoom_start=4)
    startTime = datetime.datetime.now()
    geolocator = Nominatim(user_agent="my-app")

    try:
        loc1 = locationMap[ReverseMap[city1]]
        marker1 = folium.Marker(location=[loc1[0], loc1[1]], popup=city1)
        tempL1 = loc1[0]
        tempL2 = loc1[1]
        marker1.add_to(map)
    except KeyError:
        # print(f"FETCHING... {city1}")
        location1 = geolocator.geocode(city1)
        tempL1 = location1.latitude
        tempL2 = location1.longitude
        marker2 = folium.Marker(location=[location1.latitude, location1.longitude], popup=city1)
        marker2.add_to(map)
    print(f'TIME TAKEN TO FETCH 2: {datetime.datetime.now() - startTime}')
    startTime = datetime.datetime.now()

    for row in result1:
        # print(row[0])
        try:
            loc2 = locationMap[row[0]]
            marker2 = folium.Marker(location=[loc2[0], loc2[1]], popup=citiesMap[row[0]], icon=folium.Icon(color='red'))
            points = np.array([[tempL1, tempL2], [loc2[0], loc2[1]]])
            marker2.add_to(map)
            AntPath(
                locations=points,
                dash_array=[50, 30],
                delay=400,
                weight=2,
                color='#8E44AD',
                pulse_color='#FFC300',
                tooltip=f'{citiesMap[row[0]]} {row[1]}'
            ).add_to(map)
        except KeyError:
            # print(f'FETCHING FOR {row}')
            try:
                city = citiesMap2[row[0]]
                location2 = geolocator.geocode(city)
                # Add markers for the selected cities
                marker2 = folium.Marker(location=[location2.latitude, location2.longitude], popup=citiesMap[row[0]],
                                        icon=folium.Icon(color='red'))
                points = np.array([[tempL1, tempL2], [location2.latitude, location2.longitude]])
                marker2.add_to(map)
                AntPath(
                    locations=points,
                    dash_array=[50, 30],
                    delay=400,
                    weight=2,
                    color='#8E44AD',
                    pulse_color='#FFC300',
                    tooltip=f'{citiesMap[row[0]]} {row[1]}'
                ).add_to(map)
            except KeyError:
                print(f'NOT FOUND {row[0]}')
    print(f'TIME TAKEN TO FETCH 3: {datetime.datetime.now() - startTime}')
    map_html = map.get_root().render()

    query1 = f'''SELECT UniqueCarrier,COUNT(*) FROM table{year} WHERE Origin=? GROUP BY UniqueCarrier'''
    c.execute(query1, (ReverseMap[city1],))
    result2 = c.fetchall()
    hasMap = dict(result2)
    # print(hasMap)

    query2 = f'''SELECT
  CASE
    WHEN Distance < 200 THEN '0-199'
    WHEN Distance < 500 THEN '200-499'
    WHEN Distance < 750 THEN '500-749'
    WHEN Distance < 1000 THEN '750-999'
    WHEN Distance < 1500 THEN '1000-1499'
    WHEN Distance < 2000 THEN '1500-1999'
    WHEN Distance < 3000 THEN '2000-2999'
    WHEN Distance < 4000 THEN '3000-3999'
    ELSE '4000+'
  END AS DistanceRange,
      COUNT(*) AS Count
    FROM table2005 WHERE Origin=?
    GROUP BY DistanceRange ORDER BY CASE
        WHEN DistanceRange = '0-199' THEN 1
        WHEN DistanceRange = '200-499' THEN 2
        WHEN DistanceRange = '500-749' THEN 3
        WHEN DistanceRange = '750-999' THEN 4
        WHEN DistanceRange = '1000-1499' THEN 5
        WHEN DistanceRange = '1500-1999' THEN 6
        WHEN DistanceRange = '2000-2999' THEN 7
        WHEN DistanceRange = '3000-3999' THEN 8
        ELSE 9
        END
'''
    c.execute(query2, (ReverseMap[city1],))
    result3 = c.fetchall()

    query4 = f'''SELECT Month,
               AVG(SecurityDelay) AS AverageSecurityDelay,
               AVG(WeatherDelay) AS AverageWeatherDelay,
               AVG(DepDelay) AS AverageDepartureDelay,
               AVG(LateAircraftDelay) AS AverageLateAircraftDelay,
               AVG(CarrierDelay) AS AverageCarrierDelay,
               AVG(NASDelay) AS AverageNASDelay
        FROM table{year}
        WHERE Origin = ?
        GROUP BY Month
    '''

    temp = ['SecurityDelay','WeatherDelay','DepDelay','LateAirCraftDelay','CarrierDelay','NASDeleay']
    c.execute(query4, (ReverseMap[city1],))
    data = c.fetchall()
    print(data)
    traces = []
    try:
        for i in range(1, len(data[0])):
            y_vals = [d[i] for d in data]
            trace = go.Scatter(
                x=[d[0] for d in data],
                y=y_vals,
                mode='markers+lines',
                name=f'{temp[i]}'
            )
            traces.append(trace)
    except IndexError:
        print("")

    layout = go.Layout(
        title='Connected Scatter Plot for Various Delay',
        xaxis=dict(title='Month'),
        yaxis=dict(title='Time (minutes)')
    )

    fig = go.Figure(data=traces, layout=layout)

    html_string = fig.to_html(full_html=False)
    c.close()
    conn.close()
    return render_template('map.html',
                           map_html=map_html,
                           cities=cities_list,
                           years=years_list,
                           hasMap=hasMap,
                           fullname=AirlineMap,
                           prev_city1=prevCity1,
                           data=result3,
                           scatterPlot=html_string,
                           prev_year=prevYear
                           )


@app.route('/air', methods=['GET', 'POST'])
def air():
    fromMap = request.args.get('fromMap')
    connection = sqlite3.connect('flights.db')
    prev_year = request.form.get('year')

    c = connection.cursor()
    if fromMap:
        try:
            dbResult = metaData['1988']
        except KeyError:
            # print("FOR THE FIRST TIME 1988")
            dbQuery = f'''SELECT UniqueCarrier, COUNT(DISTINCT FlightNum),COUNT(*) FROM table1988 GROUP BY UniqueCarrier;'''
            c.execute(dbQuery)
            dbResult = c.fetchall()
            metaData['1988'] = dbResult
    else:
        year = request.form.get('year')
        try:
            dbResult = metaData[year]
            # print(f"NOW FROM METADATA {year}")
        except KeyError:
            # print(f"FOR THE FIRST TIME {year}")
            dbQuery = f'''SELECT UniqueCarrier, COUNT(DISTINCT FlightNum),COUNT(*) FROM table{year} GROUP BY UniqueCarrier;'''
            c.execute(dbQuery)
            dbResult = c.fetchall()
            metaData[year] = dbResult

    hashMap = {k[0]: k[1:] for k in dbResult}
    # Create a list of full names of airlines
    full_names = [AirlineMap[k] for k in hashMap.keys()]

    # Create hover text for each bar
    hover_text_1 = ['<b>#Flight:</b> {}<br> {}'.format(d[0], full_names[i]) for i, d
                    in enumerate(hashMap.values())]
    hover_text_2 = ['<b>Trip Covered:</b> {}<br> {}'.format(d[1], full_names[i]) for
                    i, d in enumerate(hashMap.values())]

    trace1 = go.Bar(x=list(hashMap.keys()), y=[d[0] for d in hashMap.values()], name='No. of flights owned', opacity=1,
                    marker=dict(color='blue'), hovertext=hover_text_1)
    trace2 = go.Bar(x=list(hashMap.keys()), y=[d[1] / 100 for d in hashMap.values()], name='(Trip Covered)/100',
                    opacity=1, marker=dict(color='orange'), hovertext=hover_text_2)

    layout = go.Layout(barmode='group')

    fig = go.Figure(data=[trace1, trace2], layout=layout)

    html_string = fig.to_html(full_html=False)

    c.close()
    connection.close()
    return render_template('air.html',
                           years=years_list,
                           prev_year=prev_year,
                           html_str=html_string,
                           fullname=AirlineMap
                           )


@app.route('/carrier', methods=['GET', 'POST'])
def carrier():
    causes = ['DepDelay', 'SecurityDelay', 'NASDelay', 'WeatherDelay', 'LateAircraftDelay']
    fromMap = request.args.get('fromAir')
    connection = sqlite3.connect('flights.db')
    prevYear = request.form.get('year')
    prevCause = request.form.get('cause')

    c = connection.cursor()
    if fromMap:
        try:
            dbResult = metaData2['1998-DepDelay']
            # airLines = c.execute('''SELECT DISTINCT UniqueCarrier from table1988''').fetchall()
            # print(f"METADATA 1998-DepDealy")
            prevCause = 'DepDelay'
            prevYear = '1988'
        except KeyError:
            # airLines = c.execute(
            # '''SELECT DISTINCT UniqueCarrier from table1988 ORDER BY UniqueCarrier ASC''').fetchall()
            dbQuery = '''SELECT Month,UniqueCarrier, AVG(DepDelay) from table1988 GROUP BY Month, UniqueCarrier'''
            c.execute(dbQuery)
            dbResult = c.fetchall()
            prevCause = 'DepDelay'
            prevYear = '1988'
            metaData2['1998-DepDelay'] = dbResult
    else:
        year = request.form.get('year')
        # airLines = c.execute(
        #     f'''SELECT DISTINCT UniqueCarrier from table{year} ORDER BY UniqueCarrier ASC ''').fetchall()
        cause = request.form.get('cause')
        # print(f"CAUSE = {cause} ADM YEAR = {year} .... .... .")
        if cause is None:
            prev_cause = 'DepDelay'
            cause = 'DepDelay'
            year = '1988'
        try:
            dbResult = metaData2[f'{year}-{cause}']
            # print(f"METADATA {year}-{cause}")
        except KeyError:
            dbQuery = f'''SELECT Month,UniqueCarrier, AVG({cause}) FROM table{year} GROUP BY Month,UniqueCarrier'''
            c.execute(dbQuery)
            dbResult = c.fetchall()
            metaData2[f'{year}-{cause}'] = dbResult

    data = [(d[0], d[1], d[2]) if d[2] is not None else (d[0], d[1], 0) for d in dbResult]
    td = {}
    for kv in data:
        try:
            td[kv[1]].append((kv[0], kv[2]))
        except KeyError:
            td[kv[1]] = []
            td[kv[1]].append((kv[0], kv[2]))

    traces = []
    for k in td.keys():
        s = sorted(td[k])
        y_val = [v[1] for v in s]
        x_val = [v[0] for v in s]
        trace = go.Scatter(
            x=x_val,
            y=y_val,
            mode='markers+lines',
            name=f'Trace {k}'
        )
        traces.append(trace)

    layout = go.Layout(
        title=f'Connected Scatter Plot For different Airlines based of {prevCause}',
        xaxis=dict(title='Month'),
        yaxis=dict(title='Time (minutes)')
    )

    fig = go.Figure(data=traces, layout=layout)
    html_string = fig.to_html(full_html=False)

    return render_template('carrier.html'
                           , html_str=html_string
                           , causes=causes
                           , prev_cause=prevCause
                           , prev_year=prevYear
                           , years=years_list
                           )


if __name__ == '__main__':
    app.run(debug=True)
