# 🌤️ WeatherFit

Weather that actually makes sense — and AI-powered outfit tips to match.

## The Problem
Weather apps show you numbers ("68°F, 12mph wind") but most people don't intuitively
know what that *feels* like or what to wear for it. WeatherFit translates raw weather
data into plain language and gives a friendly, practical outfit recommendation.

## How it works
1. You enter your city.
2. WeatherFit fetches live weather data from Open-Meteo (temperature, wind, conditions).
3. That data is sent to Claude (Anthropic's AI), which explains what the weather will
   actually feel like and recommends what to wear.

## Tech Stack
- **Frontend/App:** Streamlit
- **Weather data:** Open-Meteo API (free, no key required)
- **AI:** Anthropic Claude API

## Running it locally
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Set your Anthropic API key as an environment variable:
   ```
   export ANTHROPIC_API_KEY=your_key_here
   ```
3. Run the app:
   ```
   streamlit run app.py
   ```

## License
MIT — see LICENSE file.
