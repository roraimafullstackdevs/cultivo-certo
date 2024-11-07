import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error.  Caching is HIGHLY recommended
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)  # expire_after=-1 for persistent cache
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)



def get_openmeteo_data(latitude, longitude, start_date, end_date):
    # ... (same as before)
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ["temperature_2m_max", "temperature_2m_min", "temperature_2m_mean", "rain_sum",
                    "precipitation_hours"],
        "timezone": "auto"  # Use "auto" for automatic timezone detection
    }

    try:
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]  # Process the first location

        daily = response.Daily()
        daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
        daily_temperature_2m_mean = daily.Variables(2).ValuesAsNumpy()
        daily_rain_sum = daily.Variables(3).ValuesAsNumpy()
        daily_precipitation_hours = daily.Variables(4).ValuesAsNumpy()

        # Calculate averages:
        avg_temperature_2m_max = daily_temperature_2m_max.mean()
        avg_temperature_2m_min = daily_temperature_2m_min.mean()
        avg_temperature_2m_mean = daily_temperature_2m_mean.mean()
        avg_rain_sum = daily_rain_sum.mean()
        avg_precipitation_hours = daily_precipitation_hours.mean()


        return {
            "avg_temperature_max": avg_temperature_2m_max,
            "avg_temperature_min": avg_temperature_2m_min,
            "avg_temperature_mean": avg_temperature_2m_mean,
            "avg_rain_sum": avg_rain_sum,
            #"avg_precipitation_hours": avg_precipitation_hours
        }

    except Exception as e:
        print(f"Error: {e}")
        return None


