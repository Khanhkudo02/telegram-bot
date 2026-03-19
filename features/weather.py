import requests
import os

def get_weather(city="Ho Chi Minh"):
    try:
        api_key = os.getenv("WEATHER_API_KEY")

        if not api_key:
            return "❌ Chưa cấu hình WEATHER_API_KEY"

        url = "https://api.openweathermap.org/data/2.5/weather"

        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",
            "lang": "vi"
        }

        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        # ===== CHECK LỖI API =====
        if res.status_code != 200:
            return f"❌ Không tìm thấy thành phố: {city}"

        # ===== LẤY DỮ LIỆU =====
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        desc = data["weather"][0]["description"]

        return (
            f"🌤 Thời tiết tại {city}\n"
            f"🌡 Nhiệt độ: {temp}°C\n"
            f"💧 Độ ẩm: {humidity}%\n"
            f"☁️ Mô tả: {desc}"
        )

    except Exception as e:
        print("Weather error:", e)
        return "❌ Lỗi khi lấy thời tiết"