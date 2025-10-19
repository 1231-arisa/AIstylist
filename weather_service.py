"""
Weather service for AIstylist
"""
import requests
import os
from datetime import datetime, timedelta
from database import cache_weather, get_cached_weather
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local', override=True)

def get_weather_data(location="Vancouver"):
    """Get current weather data with caching"""
    print(f"[Weather Service] Getting weather for {location}")
    
    # Check cache first (with shorter cache time for more real-time updates)
    cached_data = get_cached_weather(location, max_age_hours=0.1)  # 6 minutes cache
    if cached_data:
        print(f"[Weather Service] Using cached data: {cached_data}")
        return cached_data
    
    # Fetch from API
    api_key = os.getenv("WEATHER_API_KEY")
    print(f"[Weather Service] API Key loaded: {'Yes' if api_key else 'No'}")
    
    if not api_key:
        print("[Weather Service] No API key found, using fallback data")
        # Return fallback data if no API key
        fallback_data = {
            "location": location,
            "temperature": 22,
            "condition": "Sunny",
            "icon": "☀️",
            "humidity": 60,
            "wind_speed": 10
        }
        cache_weather(location, fallback_data)
        return fallback_data
    
    try:
        url = "http://api.weatherapi.com/v1/current.json"
        params = {
            "key": api_key,
            "q": location,
            "aqi": "no"
        }
        
        print(f"[Weather Service] Calling API: {url}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        weather_data = {
            "location": data["location"]["name"],
            "temperature": round(data["current"]["temp_c"]),
            "condition": data["current"]["condition"]["text"],
            "icon": get_weather_icon(data["current"]["condition"]["code"]),
            "humidity": data["current"]["humidity"],
            "wind_speed": data["current"]["wind_kph"]
        }
        
        print(f"[Weather Service] API call successful: {weather_data}")
        
        # Cache the result
        cache_weather(location, weather_data)
        return weather_data
        
    except Exception as e:
        print(f"[Weather Service] API error: {e}")
        # Return fallback data
        fallback_data = {
            "location": location,
            "temperature": 22,
            "condition": "Sunny",
            "icon": "☀️",
            "humidity": 60,
            "wind_speed": 10
        }
        cache_weather(location, fallback_data)
        return fallback_data

def get_weather_icon(code):
    """Get weather icon based on condition code"""
    icon_map = {
        1000: "☀️",  # Sunny
        1003: "⛅",  # Partly cloudy
        1006: "☁️",  # Cloudy
        1009: "☁️",  # Overcast
        1030: "🌫️",  # Mist
        1063: "🌦️",  # Patchy rain possible
        1066: "🌨️",  # Patchy snow possible
        1069: "🌨️",  # Patchy sleet possible
        1072: "🌨️",  # Patchy freezing drizzle possible
        1087: "⛈️",  # Thundery outbreaks possible
        1114: "🌨️",  # Blowing snow
        1117: "🌨️",  # Blizzard
        1135: "🌫️",  # Fog
        1147: "🌫️",  # Freezing fog
        1150: "🌦️",  # Patchy light drizzle
        1153: "🌦️",  # Light drizzle
        1168: "🌦️",  # Freezing drizzle
        1171: "🌦️",  # Heavy freezing drizzle
        1180: "🌦️",  # Patchy light rain
        1183: "🌦️",  # Light rain
        1186: "🌦️",  # Moderate rain at times
        1189: "🌦️",  # Moderate rain
        1192: "🌧️",  # Heavy rain at times
        1195: "🌧️",  # Heavy rain
        1198: "🌦️",  # Light freezing rain
        1201: "🌧️",  # Moderate or heavy freezing rain
        1204: "🌨️",  # Light sleet
        1207: "🌨️",  # Moderate or heavy sleet
        1210: "🌨️",  # Patchy light snow
        1213: "🌨️",  # Light snow
        1216: "🌨️",  # Patchy moderate snow
        1219: "🌨️",  # Moderate snow
        1222: "🌨️",  # Patchy heavy snow
        1225: "🌨️",  # Heavy snow
        1237: "🌨️",  # Ice pellets
        1240: "🌦️",  # Light rain shower
        1243: "🌧️",  # Moderate or heavy rain shower
        1246: "🌧️",  # Torrential rain shower
        1249: "🌨️",  # Light sleet showers
        1252: "🌨️",  # Moderate or heavy sleet showers
        1255: "🌨️",  # Light snow showers
        1258: "🌨️",  # Moderate or heavy snow showers
        1261: "🌨️",  # Light showers of ice pellets
        1264: "🌨️",  # Moderate or heavy showers of ice pellets
        1273: "⛈️",  # Patchy light rain with thunder
        1276: "⛈️",  # Moderate or heavy rain with thunder
        1279: "⛈️",  # Patchy light snow with thunder
        1282: "⛈️",  # Moderate or heavy snow with thunder
    }
    
    return icon_map.get(code, "☀️")

def get_weather_recommendation(weather_data):
    """Get weather-based outfit recommendation"""
    temp = weather_data.get("temperature", 22)
    condition = weather_data.get("condition", "Sunny").lower()
    
    if temp < 10:
        return "Cold weather - wear warm layers, coats, and boots"
    elif temp < 20:
        return "Cool weather - light jackets and long sleeves recommended"
    elif "rain" in condition:
        return "Rainy weather - waterproof clothing and umbrellas essential"
    elif "sun" in condition:
        return "Sunny weather - light, breathable fabrics and sun protection"
    else:
        return "Moderate weather - versatile clothing options work well"

def get_weekly_forecast(location="Vancouver"):
    """Get 7-day weather forecast"""
    print(f"[Weather Service] Getting weekly forecast for {location}")
    
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        print("[Weather Service] No API key found, using fallback data")
        # Return fallback data for 7 days
        from datetime import datetime, timedelta
        fallback_data = []
        for i in range(7):
            date = datetime.now() + timedelta(days=i)
            fallback_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "day": date.strftime("%A"),
                "temperature": 22 + (i * 2),  # Vary temperature slightly
                "condition": "Sunny",
                "icon": "☀️",
                "humidity": 60,
                "wind_speed": 10
            })
        return fallback_data
    
    try:
        url = "http://api.weatherapi.com/v1/forecast.json"
        params = {
            "key": api_key,
            "q": location,
            "days": 7,
            "aqi": "no",
            "alerts": "no"
        }
        
        print(f"[Weather Service] Calling forecast API: {url}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        forecast_data = []
        for day in data["forecast"]["forecastday"]:
            from datetime import datetime
            forecast_data.append({
                "date": day["date"],
                "day": datetime.strptime(day["date"], "%Y-%m-%d").strftime("%A"),
                "temperature": round(day["day"]["avgtemp_c"]),
                "condition": day["day"]["condition"]["text"],
                "icon": get_weather_icon(day["day"]["condition"]["code"]),
                "humidity": day["day"]["avghumidity"],
                "wind_speed": day["day"]["maxwind_kph"]
            })
        
        print(f"[Weather Service] Forecast API call successful: {len(forecast_data)} days")
        return forecast_data
        
    except Exception as e:
        print(f"[Weather Service] Forecast API error: {e}")
        # Return fallback data
        from datetime import datetime, timedelta
        fallback_data = []
        for i in range(7):
            date = datetime.now() + timedelta(days=i)
            fallback_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "day": date.strftime("%A"),
                "temperature": 22 + (i * 2),
                "condition": "Sunny",
                "icon": "☀️",
                "humidity": 60,
                "wind_speed": 10
            })
        return fallback_data






