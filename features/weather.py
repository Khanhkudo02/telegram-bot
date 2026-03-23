import requests
import os

def get_weather(city="Hồ Chí Minh"):
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return "❌ Chưa cấu hình WEATHER_API_KEY trong biến môi trường."

    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",
            "lang": "vi"
        }
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()

        if data.get("cod") != 200:
            return f"❌ Không tìm thấy thành phố: {city}"

        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        desc = data["weather"][0]["description"].capitalize()

        return (
            f"🌤 Thời tiết tại **{city}**\n"
            f"🌡️ Nhiệt độ: {temp}°C (cảm giác {feels_like}°C)\n"
            f"💧 Độ ẩm: {humidity}%\n"
            f"☁️ {desc}"
        )

    except Exception as e:
        print(f"WEATHER ERROR: {e}")
        return "❌ Lỗi khi lấy thông tin thời tiết. Kiểm tra tên thành phố."