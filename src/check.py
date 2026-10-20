import duckdb

con = duckdb.connect("weather.duckdb")
print(con.execute("""
    SELECT city, COUNT(*) AS rows, MIN(time) AS first, MAX(time) AS last
    FROM weather
    GROUP BY city
    ORDER BY city
""").df())