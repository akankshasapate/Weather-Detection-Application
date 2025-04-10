# 🌦️ Weather Detection Application

A Python-based GUI application that provides **real-time weather updates** and a **7-day forecast** for any city in the world. Built using **Tkinter**, the app fetches and displays weather data like temperature, humidity, wind speed, and more using the **OpenWeatherMap API**.

---

## 📌 Objectives

- Create an interactive weather detection system.
- Fetch real-time weather data using OpenWeatherMap API.
- Display temperature, humidity, wind speed, pressure, and weather conditions.
- Show a 7-day weather forecast with icons for better UX.

---

## 🛠 Technologies Used

| Component             | Technology Used          |
|----------------------|--------------------------|
| Programming Language | Python                   |
| GUI Framework        | Tkinter                  |
| Weather API          | OpenWeatherMap API       |
| Geolocation Service  | Geopy, TimezoneFinder    |
| Date & Time Handling | Datetime, Pytz           |
| Image Handling       | Pillow (PIL)             |
| IDE                  | PyCharm                  |

---

## ✨ Features

- 🌍 **City-based Search:** Enter any city to get real-time weather updates.
- 🌡️ **Live Weather Info:** Displays temperature, humidity, pressure, and wind speed.
- ☁️ **Weather Description:** Clear, cloudy, rainy, etc.
- 📅 **7-Day Forecast:** View day and night temperature for the next 7 days.
- 🖼️ **Weather Icons:** Forecasts include descriptive icons.
- ❌ **Error Handling:** Manages invalid city input and API failures gracefully.

---

## ⚙️ Working Mechanism

1. **User Input:** User enters a city name in the search bar.
2. **Geolocation Fetching:** City’s latitude and longitude are retrieved using `Geopy`.
3. **Timezone Detection:** TimezoneFinder gets the local timezone for the city.
4. **API Call:** OpenWeatherMap API fetches current weather and forecast.
5. **Data Processing:**
   - Extracts temperature, humidity, pressure, and wind speed.
   - Parses weather descriptions and links icons accordingly.
6. **UI Update:** Data is dynamically shown on the Tkinter interface.

---

## 📥 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/weather-detection-app.git
   cd weather-detection-app
