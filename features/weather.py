import requests, os

def get_weather(city):
    key = os.getenv("WEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric"

    try:
        d = requests.get(url).json()
        return f"{city}: {d['main']['temp']}°C"
    except:
        return "❌ lỗi thời tiết"