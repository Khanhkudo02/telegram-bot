import requests
import os

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

def get_weather(city="Ho Chi Minh"):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=vi"
        data = requests.get(url).json()

        if "main" not in data:
            return "❌ Không lấy được thời tiết."

        return (
            f"🌤 {city}\n"
            f"🌡 {data['main']['temp']}°C\n"
            f"💧 {data['main']['humidity']}%\n"
            f"☁️ {data['weather'][0]['description']}"
        )

    except:
        return "❌ Lỗi thời tiết."
