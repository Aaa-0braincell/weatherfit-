import streamlit as st
import requests
import anthropic

# ----------------------------
# Page setup
# ----------------------------
st.set_page_config(page_title="WeatherFit", page_icon="🌤️")
st.title("🌤️ WeatherFit")
st.write("Weather that actually makes sense, and outfit tips to match.")

# ----------------------------
# Step 1: Get the city from the user
# ----------------------------
city = st.text_input("Enter your city", placeholder="e.g. New York")

def get_coordinates(city_name):
    """Turn a city name into latitude/longitude using Open-Meteo's free geocoding API."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name, "count": 1}
    response = requests.get(url, params=params)
    data = response.json()

    if "results" not in data or len(data["results"]) == 0:
        return None

    result = data["results"][0]
    return {
        "lat": result["latitude"],
        "lon": result["longitude"],
        "name": result["name"],
        "country": result.get("country", ""),
    }


def get_weather(lat, lon):
    """Get current weather for a location using Open-Meteo (no API key needed)."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,apparent_temperature,precipitation,wind_speed_10m,weather_code",
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
    }
    response = requests.get(url, params=params)
    return response.json()["current"]


def weather_code_to_description(code):
    """Convert Open-Meteo's numeric weather code into a plain description."""
    mapping = {
        0: "clear sky",
        1: "mostly clear", 2: "partly cloudy", 3: "overcast",
        45: "foggy", 48: "foggy",
        51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
        61: "light rain", 63: "rain", 65: "heavy rain",
        71: "light snow", 73: "snow", 75: "heavy snow",
        80: "rain showers", 81: "rain showers", 82: "violent rain showers",
        95: "thunderstorm",
    }
    return mapping.get(code, "unusual weather")


def get_api_key():
    """Get the Anthropic API key from Streamlit secrets (cloud) or environment (local)."""
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        import os
        return os.environ.get("ANTHROPIC_API_KEY")


def get_styling_advice(weather_summary):
    """Ask Claude to turn raw weather data into a friendly explanation + outfit advice."""
    api_key = get_api_key()
    if not api_key:
        return "⚠️ No API key found. Please add ANTHROPIC_API_KEY in your app's Secrets settings."

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""You are a friendly, practical personal stylist. A user gave you this weather data:

{weather_summary}

Write a response with two short sections:
1. "How it'll actually feel" — 1-2 plain-English sentences translating the numbers into what it will actually feel like outside (don't just repeat the numbers).
2. "What to wear" — a specific, practical outfit recommendation (layers, footwear, accessories like umbrella/sunglasses if relevant) for this weather.

Keep it warm, concise, and easy to read. No markdown headers, just two short paragraphs."""

    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


# ----------------------------
# Step 2: Main app flow
# ----------------------------
if st.button("Get my outfit tips") and city:
    with st.spinner("Checking the weather..."):
        location = get_coordinates(city)

    if location is None:
        st.error("Couldn't find that city. Try a different spelling or add a country, e.g. 'Paris, France'.")
    else:
        weather = get_weather(location["lat"], location["lon"])
        description = weather_code_to_description(weather["weather_code"])

        st.subheader(f"📍 {location['name']}, {location['country']}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Temperature", f"{weather['temperature_2m']}°F")
        col2.metric("Feels like", f"{weather['apparent_temperature']}°F")
        col3.metric("Wind", f"{weather['wind_speed_10m']} mph")

        st.write(f"Conditions: **{description}**")

        weather_summary = (
            f"Temperature: {weather['temperature_2m']}°F, "
            f"feels like {weather['apparent_temperature']}°F, "
            f"conditions: {description}, "
            f"wind: {weather['wind_speed_10m']} mph, "
            f"precipitation: {weather['precipitation']} mm"
        )

        with st.spinner("Getting your styling tips..."):
            advice = get_styling_advice(weather_summary)

        st.subheader("👔 Your Outfit Tips")
        st.write(advice)
