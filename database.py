import sqlite3
import pandas as pd

# Connect to db
conn = sqlite3.connect('flights.db')

# create table
conn.execute('''CREATE TABLE flights (
                ActualElapsedTime INTEGER,
                AirTime REAL,
                ArrDelay REAL,
                ArrTime REAL,
                CRSArrTime REAL,
                CRSDepTime INTEGER,
                CRSElapsedTime INTEGER,
                CancellationCode TEXT,
                Cancelled INTEGER,
                CarrierDelay REAL,
                DayOfWeek INTEGER,
                DayOfMonth INTEGER,
                DepDelay REAL,
                DepTime REAL,
                Dest TEXT,
                Distance REAL,
                Diverted INTEGER,
                FlightNum INTEGER,
                LateAircraftDelay REAL,
                Month INTEGER,
                NASDelay REAL,
                Origin TEXT,
                SecurityDelay REAL,
                TailNum TEXT,
                TaxiIn REAL,
                TaxiOut REAL,
                UniqueCarrier TEXT,
                WeatherDelay REAL,
                Year INTEGER
                );''')

chunkSize = 10000
cnt = 0
year = 2002
while year < 2003:
    for chunk in pd.read_csv(f'../DataExtraction/2002.csv', chunksize=chunkSize):
        cnt = cnt + 1
        chunk.to_sql(f'table{year}', conn, if_exists='append', index=False)
    print(f'COMPLETED FOR YEAR {year}')
    year = year + 1
# commit changes and close connection
conn.commit()
conn.close()
