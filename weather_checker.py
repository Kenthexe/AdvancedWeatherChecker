import requests
import json
import datetime
import os
import csv

def get_weather(city, api_key, units="metric"):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": units
    }
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        weather = {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "description": data["weather"][0]["description"].capitalize(),
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "sunrise": datetime.datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%H:%M:%S'),
            "sunset": datetime.datetime.fromtimestamp(data["sys"]["sunset"]).strftime('%H:%M:%S'),
            "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "units": "°C" if units == "metric" else "°F",
            "lat": data["coord"]["lat"],
            "lon": data["coord"]["lon"]
        }
        return weather
    except requests.RequestException as e:
        print(f"Error fetching weather: {e}")
    except (KeyError, json.JSONDecodeError):
        print("Error parsing weather data.")
    return None

def get_forecast(city, api_key, units="metric"):
    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": api_key,
        "units": units
    }
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        forecast_list = []
        for entry in data["list"]:
            dt_txt = entry["dt_txt"]
            temp = entry["main"]["temp"]
            desc = entry["weather"][0]["description"].capitalize()
            humidity = entry["main"]["humidity"]
            forecast_list.append({
                "datetime": dt_txt,
                "temperature": temp,
                "description": desc,
                "humidity": humidity
            })
        return forecast_list
    except Exception as e:
        print(f"Error fetching forecast: {e}")
        return None

def print_weather(weather):
    print(f"\nWeather in {weather['city']}, {weather['country']} ({weather['timestamp']}):")
    print(f"  Temperature: {weather['temperature']}{weather['units']} (Feels like: {weather['feels_like']}{weather['units']})")
    print(f"  Description: {weather['description']}")
    print(f"  Humidity: {weather['humidity']}%")
    print(f"  Wind Speed: {weather['wind_speed']} m/s")
    print(f"  Sunrise: {weather['sunrise']} | Sunset: {weather['sunset']}")
    print(f"  Weather Map Links:")
    print(f"    Precipitation: https://openweathermap.org/weathermap?basemap=map&cities=true&layer=precipitation&lat={weather['lat']}&lon={weather['lon']}&zoom=10")
    print(f"    Temperature:   https://openweathermap.org/weathermap?basemap=map&cities=true&layer=temperature&lat={weather['lat']}&lon={weather['lon']}&zoom=10")
    print(f"    Wind:          https://openweathermap.org/weathermap?basemap=map&cities=true&layer=wind&lat={weather['lat']}&lon={weather['lon']}&zoom=10")
    print_suggestion(weather)

def print_suggestion(weather):
    temp = weather['temperature']
    desc = weather['description'].lower()
    units = weather['units']
    suggestion = ""
    if "rain" in desc or "drizzle" in desc:
        suggestion += "🌧️ Bring an umbrella. "
    if "snow" in desc:
        suggestion += "❄️ Wear warm clothes and boots. "
    if "clear" in desc:
        suggestion += "☀️ Sunglasses recommended. "
    if temp < (0 if units == "°C" else 32):
        suggestion += "🧥 It's freezing! Dress warmly. "
    elif temp < (10 if units == "°C" else 50):
        suggestion += "🧣 It's cold, wear a jacket. "
    elif temp > (30 if units == "°C" else 86):
        suggestion += "🧢 Stay hydrated and wear light clothes. "
    if not suggestion:
        suggestion = "🙂 Weather looks moderate. Enjoy your day!"
    print(f"  Suggestion: {suggestion}")

def print_forecast(forecast, units="°C"):
    print("\n5-Day Forecast (3-hour intervals):")
    for entry in forecast[:10]:  # Show next 10 intervals (~1.5 days)
        print(f"  {entry['datetime']}: {entry['temperature']}{units}, {entry['description']}, Humidity: {entry['humidity']}%")
    print("  ... (more available)")

def save_history(weather, filename="weather_history.txt"):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(json.dumps(weather) + "\n")
    print(f"Weather data saved to {filename}.")

def show_history(filename="weather_history.txt"):
    if not os.path.exists(filename):
        print("No history found.")
        return
    print("\n--- Weather History ---")
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            try:
                weather = json.loads(line.strip())
                print(f"{weather['timestamp']} - {weather['city']}, {weather['country']}: {weather['temperature']}{weather['units']}, {weather['description']}")
            except Exception:
                continue
    print("-----------------------")

def export_history_csv(filename="weather_history.txt", csv_filename="weather_history.csv"):
    if not os.path.exists(filename):
        print("No history to export.")
        return
    with open(filename, "r", encoding="utf-8") as f, open(csv_filename, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "city", "country", "temperature", "feels_like", "description", "humidity", "wind_speed", "sunrise", "sunset", "units"])
        for line in f:
            try:
                weather = json.loads(line.strip())
                writer.writerow([
                    weather.get("timestamp", ""),
                    weather.get("city", ""),
                    weather.get("country", ""),
                    weather.get("temperature", ""),
                    weather.get("feels_like", ""),
                    weather.get("description", ""),
                    weather.get("humidity", ""),
                    weather.get("wind_speed", ""),
                    weather.get("sunrise", ""),
                    weather.get("sunset", ""),
                    weather.get("units", "")
                ])
            except Exception:
                continue
    print(f"History exported to {csv_filename}.")

def search_history(filename="weather_history.txt"):
    if not os.path.exists(filename):
        print("No history found.")
        return
    query = input("Enter city name or date (YYYY-MM-DD) to search: ").strip().lower()
    found = False
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            try:
                weather = json.loads(line.strip())
                if (query in weather.get("city", "").lower()) or (query in weather.get("timestamp", "")):
                    print(f"{weather['timestamp']} - {weather['city']}, {weather['country']}: {weather['temperature']}{weather['units']}, {weather['description']}")
                    found = True
            except Exception:
                continue
    if not found:
        print("No matching records found.")

def compare_cities(api_key, units="metric"):
    city1 = input("Enter first city: ").strip()
    city2 = input("Enter second city: ").strip()
    w1 = get_weather(city1, api_key, units)
    w2 = get_weather(city2, api_key, units)
    if w1 and w2:
        print("\nComparison:")
        print(f"{w1['city']}: {w1['temperature']}{w1['units']}, {w1['description']}")
        print(f"{w2['city']}: {w2['temperature']}{w2['units']}, {w2['description']}")
        diff = w1['temperature'] - w2['temperature']
        print(f"Temperature difference: {abs(diff):.2f}{w1['units']} ({w1['city']} is {'warmer' if diff > 0 else 'colder' if diff < 0 else 'the same temperature'} than {w2['city']})")
    else:
        print("Could not retrieve weather for one or both cities.")

def main():
    print("=== Weather Checker Pro ===")
    api_key = input("Enter your OpenWeatherMap API key: ").strip()
    units = "metric"
    while True:
        print("\nOptions:")
        print("  1. Check weather for a city")
        print("  2. Show weather history")
        print("  3. Compare two cities")
        print("  4. Change units (currently: Celsius)" if units == "metric" else "  4. Change units (currently: Fahrenheit)")
        print("  5. Get 5-day forecast for a city")
        print("  6. Export history to CSV")
        print("  7. Search history")
        print("  8. Quit")
        choice = input("Select an option (1-8): ").strip()
        if choice == "1":
            city = input("Enter city name: ").strip()
            weather = get_weather(city, api_key, units)
            if weather:
                print_weather(weather)
                save = input("Save this result to history? (y/n): ").strip().lower()
                if save == "y":
                    save_history(weather)
            else:
                print("Could not retrieve weather data. Please try again.")
        elif choice == "2":
            show_history()
        elif choice == "3":
            compare_cities(api_key, units)
        elif choice == "4":
            units = "imperial" if units == "metric" else "metric"
            print(f"Units changed to {'Fahrenheit' if units == 'imperial' else 'Celsius'}.")
        elif choice == "5":
            city = input("Enter city name for forecast: ").strip()
            forecast = get_forecast(city, api_key, units)
            if forecast:
                print_forecast(forecast, "°C" if units == "metric" else "°F")
            else:
                print("Could not retrieve forecast.")
        elif choice == "6":
            export_history_csv()
        elif choice == "7":
            search_history()
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please select 1-8.")

if __name__ == "__main__":
    main()
