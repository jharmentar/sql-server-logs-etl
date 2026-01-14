import duckdb
import os

con = duckdb.connect()


print("Extract: Loading Data...")
con.execute("""
    CREATE TABLE logs AS 
    SELECT * FROM read_json_auto('data/logs.json')
""")

print("Transform: Calculating Metrics...")
# Most used endpoints
endpoints = con.execute("""
WITH endpoints AS (
SELECT endpoint, 
COUNT(*) as requests,
ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM logs), 2) as percent
FROM logs
GROUP BY endpoint
ORDER BY requests DESC
)
SELECT * from endpoints
LIMIT 10
""").fetchdf()

# Analysis of endpoints with error 500
errors = con.execute("""
WITH errors AS(
SELECT 
    endpoint,
    COUNT(*) as total_errors,
    COUNT(DISTINCT user_id) as affected_users,
    ROUND(AVG(response_time_ms), 2) as avg_response_time
FROM logs
WHERE status_code >= 500
GROUP BY endpoint
ORDER BY total_errors DESC
)
SELECT * from errors
LIMIT 10
""").fetchdf()


#Performance of endpoints ¿Which endpoint is the slowest?
performance = con.execute("""
WITH performance AS (
SELECT 
    endpoint,
    COUNT(*) as requests,
    ROUND(AVG(response_time_ms), 2) as avg_response_time,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY response_time_ms), 2) as p50,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms), 2) as p95,
    MAX(response_time_ms) as max_time
FROM logs
WHERE status_code < 500 --Requests exitosas
GROUP BY endpoint
HAVING COUNT(*) > 100
ORDER BY p95 DESC
)
SELECT * from performance
LIMIT 10
""").fetchdf()

#Trend by hour 
trend_hour = con.execute("""
WITH trend_hour AS (
SELECT 
    EXTRACT(HOUR FROM timestamp) as hour,
    COUNT(*) as requests,
    ROUND(AVG(response_time_ms), 2) as avg_response_time,
    SUM(CASE WHEN status_code >= 500 THEN 1 ELSE 0 END) as total_errors
FROM logs
GROUP BY hour
ORDER BY hour
)
SELECT * from trend_hour
LIMIT 10
""").fetchdf()

#Top 3 request slowest
slowest = con.execute("""
WITH ranked AS (
    SELECT 
        endpoint,
        timestamp,
        response_time_ms,
        user_id,
        ROW_NUMBER() OVER (
            PARTITION BY endpoint 
            ORDER BY response_time_ms DESC
        ) as rank
    FROM logs
    WHERE status_code < 500 and user_id IS NOT NULL
)
SELECT * FROM ranked 
WHERE rank <= 3
ORDER BY endpoint, rank;
""").fetchdf()

#Comparison with previous period
daily = con.execute("""
WITH daily_stats AS (
    SELECT 
        DATE(timestamp) as date,
        COUNT(*) as requests,
        ROUND(AVG(response_time_ms), 2) as avg_time
    FROM logs
    GROUP BY DATE(timestamp)
)
SELECT 
    date,
    requests,
    LAG(requests) OVER (ORDER BY date) as request_previous_day,
    requests - LAG(requests) OVER (ORDER BY date) as difference,
    ROUND(
        (requests - LAG(requests) OVER (ORDER BY date)) * 100.0 / 
        LAG(requests) OVER (ORDER BY date), 
        2
    ) as percentage_change
FROM daily_stats
ORDER BY date
""").fetchdf()

#Save metrics
print("Load: Saving Data...")
os.makedirs('output', exist_ok=True)
daily.to_csv(f'output/daily_metrics.csv', index=False)
slowest.to_csv(f'output/slowest_requests.csv', index=False)
performance.to_csv(f'output/performance_metrics.csv', index=False)
trend_hour.to_csv(f'output/trend_hour.csv', index=False)
errors.to_csv(f'output/errors_metrics.csv', index=False)
endpoints.to_csv(f'output/endpoints_metrics.csv', index=False)
print("Data saved successfully.")
