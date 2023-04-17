import sqlite3

# connect to database
conn = sqlite3.connect('flights.db')
c = conn.cursor()

# execute the query
c.execute("SELECT COUNT(*) FROM mytable WHERE origin = 'BHM' AND dest = 'MSY'")
result = c.fetchone()[0]

# print the result
print(f"Number of entries where origin is PVD and dest is ORD: {result}")

# print the results

# close the connection
conn.close()
