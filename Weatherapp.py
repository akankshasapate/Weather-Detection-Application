from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from datetime import datetime, timedelta
import requests
import pytz
import os
from PIL import Image, ImageTk

# Initialize the main window
root = tk.Tk()
root.title("Weather App")
root.geometry("890x470+300+200")
root.configure(bg="#57adff")
root.resizable(False, False)

API_KEY = "df0fb183c8f5fa88b0aef4ef53cec0e6"


def getWeather():
    city = textfield.get().strip()

    if not city:
        messagebox.showerror("Error", "Please enter a city name")
        return

    try:
        # Geolocation
        geolocator = Nominatim(user_agent="weather_app_geolocation")
        location = geolocator.geocode(city)

        if location is None:
            messagebox.showerror("Error", "City not found! Try again.")
            return

        obj = TimezoneFinder()
        result = obj.timezone_at(lng=location.longitude, lat=location.latitude)

        if result:
            timezone.config(text=f"{result}")
            long_lat.config(text=f"{round(location.latitude, 3)}°N, {round(location.longitude, 3)}°E")

            # Get local time
            home = pytz.timezone(result)
            local_time = datetime.now(home)
            current_time = local_time.strftime("%I:%M %p")
            clock.config(text=current_time)

            # Fetch current weather data
            weather_api = f"https://api.openweathermap.org/data/2.5/weather?lat={location.latitude}&lon={location.longitude}&units=metric&appid={API_KEY}"
            weather_response = requests.get(weather_api)
            weather_data = weather_response.json()

            if weather_data.get("cod") != 200:
                messagebox.showerror("Error", f"Weather data not found! ({weather_data.get('message')})")
                return

            # Extract current weather details
            temp = weather_data['main']['temp']
            humidity = weather_data['main']['humidity']
            pressure = weather_data['main']['pressure']
            wind_speed = weather_data['wind']['speed']
            description = weather_data['weather'][0]['description'].title()
            current_icon = weather_data['weather'][0]['icon']

            # Update UI for current weather
            temperature_label.config(text=f"{temp:.1f} °C")
            humidity_label.config(text=f"{humidity} %")
            pressure_label.config(text=f"{pressure} hPa")
            wind_label.config(text=f"{wind_speed:.1f} m/s")
            description_label.config(text=description)

            # Fetch 5-day forecast data (free API)
            forecast_api = f"https://api.openweathermap.org/data/2.5/forecast?lat={location.latitude}&lon={location.longitude}&units=metric&appid={API_KEY}"
            forecast_response = requests.get(forecast_api)
            forecast_data = forecast_response.json()

            if forecast_data.get("cod") != "200":
                messagebox.showerror("Error", f"Forecast data not available ({forecast_data.get('message')})")
                return

            # Parse the 5-day forecast
            forecast_list = forecast_data['list']

            # Get dates for the next 7 days
            today = datetime.now()
            dates = [today + timedelta(days=i) for i in range(7)]
            day_names = [date.strftime("%A") for date in dates]

            # Config day names
            day1.config(text=day_names[0])
            day2.config(text=day_names[1])
            day3.config(text=day_names[2])
            day4.config(text=day_names[3])
            day5.config(text=day_names[4])
            day6.config(text=day_names[5])
            day7.config(text=day_names[6])

            # Process today's weather (from current weather data)
            try:
                icon_path = f"icon/{current_icon}@2x.png"
                if not os.path.exists(icon_path):
                    # Create icon directory if it doesn't exist
                    os.makedirs("icon", exist_ok=True)

                    icon_url = f"https://openweathermap.org/img/wn/{current_icon}@2x.png"
                    response = requests.get(icon_url)
                    if response.status_code == 200:
                        with open(icon_path, "wb") as file:
                            file.write(response.content)
                    else:
                        print(f"Failed to download icon: {icon_url}")

                # Load the image after ensuring it exists
                if os.path.exists(icon_path):
                    img = Image.open(icon_path)
                    photo1 = ImageTk.PhotoImage(img)
                    firstimage.config(image=photo1)
                    firstimage.image = photo1  # Keep a reference
            except Exception as e:
                print(f"Error loading today's weather icon: {e}")

            # Set today's temperature
            day_temp = temp
            night_temp = temp - 5.0  # Estimate for demonstration
            day1temp.config(text=f"Day: {day_temp:.1f}°C\nNight: {night_temp:.1f}°C")

            # Create a dictionary to store forecasted data by day
            daily_forecasts = {}

            # Process the forecast list (which comes in 3-hour intervals)
            for item in forecast_list:
                # Get the date from the timestamp
                timestamp = item['dt']
                date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                hour = datetime.fromtimestamp(timestamp).hour

                # If this date is not yet in our dictionary, initialize it
                if date not in daily_forecasts:
                    daily_forecasts[date] = {
                        'day_temp': [],
                        'night_temp': [],
                        'icon': None
                    }

                # Add temperatures based on time of day
                temp = item['main']['temp']
                if 6 <= hour < 18:  # Day time
                    daily_forecasts[date]['day_temp'].append(temp)
                    # Use noon (or closest to noon) icon for the day
                    if hour == 12 or (hour > 12 and hour <= 15 and daily_forecasts[date]['icon'] is None):
                        daily_forecasts[date]['icon'] = item['weather'][0]['icon']
                else:  # Night time
                    daily_forecasts[date]['night_temp'].append(temp)

                # If no day icon was found, use any icon
                if daily_forecasts[date]['icon'] is None:
                    daily_forecasts[date]['icon'] = item['weather'][0]['icon']

            # Sort the dates to get the next 6 days (today is already handled)
            future_dates = sorted(list(daily_forecasts.keys()))[0:6]

            # Process forecasts for the next 6 days
            day_configs = [
                (2, secondimage, day2temp),
                (3, thirdimage, day3temp),
                (4, fourthimage, day4temp),
                (5, fifthimage, day5temp),
                (6, sixthimage, day6temp),
                (7, seventhimage, day7temp)
            ]

            for i, date in enumerate(future_dates):
                if i < len(day_configs):
                    day_num, image_label, temp_label = day_configs[i]

                    forecast = daily_forecasts[date]
                    day_temp = sum(forecast['day_temp']) / len(forecast['day_temp']) if forecast['day_temp'] else None
                    night_temp = sum(forecast['night_temp']) / len(forecast['night_temp']) if forecast[
                        'night_temp'] else None

                    # If we don't have day or night temps, make an estimate
                    if day_temp is None and night_temp is not None:
                        day_temp = night_temp + 5.0
                    elif night_temp is None and day_temp is not None:
                        night_temp = day_temp - 5.0
                    elif day_temp is None and night_temp is None:
                        # Default values if no data is available
                        day_temp = 20.0
                        night_temp = 15.0

                    try:
                        # Download icon if it doesn't exist
                        icon_path = f"icon/{forecast['icon']}@2x.png"
                        if not os.path.exists(icon_path):
                            icon_url = f"https://openweathermap.org/img/wn/{forecast['icon']}@2x.png"
                            response = requests.get(icon_url)
                            if response.status_code == 200:
                                with open(icon_path, "wb") as file:
                                    file.write(response.content)
                            else:
                                print(f"Failed to download icon: {icon_url}")

                        # Load image if it exists
                        if os.path.exists(icon_path):
                            img = Image.open(icon_path)
                            resized_image = img.resize((50, 50))
                            photo = ImageTk.PhotoImage(resized_image)
                            image_label.config(image=photo)
                            image_label.image = photo  # Keep a reference
                    except Exception as e:
                        print(f"Error loading day {day_num} image: {e}")

                    temp_label.config(text=f"Day: {day_temp:.1f}°C\nNight: {night_temp:.1f}°C")

        else:
            timezone.config(text="Timezone: Not Found")
            long_lat.config(text="Longitude and latitude Not Found")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to get data: {str(e)}")
        # Print detailed error for debugging
        import traceback
        traceback.print_exc()


# Create icon directory if it doesn't exist
os.makedirs("icon", exist_ok=True)

# Load application icon
try:
    image_icon = PhotoImage(file="logo.png")
    root.iconphoto(False, image_icon)
except Exception as e:
    print(f"Could not load logo: {e}")

try:
    Round_box = PhotoImage(file="Rounded Rectangle 1.png")
    Label(root, image=Round_box, bg="#57adff").place(x=25, y=110)
except Exception as e:
    print(f"Could not load rounded rectangle: {e}")
    # Create a fallback rounded rectangle
    frame_box = Frame(root, width=230, height=120, bg="#203243")
    frame_box.place(x=25, y=110)

# Labels for weather information
label1 = Label(root, text="Temperature", font=('Helvetica', 11), fg="white", bg="#203243")
label1.place(x=40, y=120)

label2 = Label(root, text="Humidity", font=('Helvetica', 11), fg="white", bg="#203243")
label2.place(x=40, y=140)

label3 = Label(root, text="Pressure", font=('Helvetica', 11), fg="white", bg="#203243")
label3.place(x=40, y=160)

label4 = Label(root, text="Wind speed", font=('Helvetica', 11), fg="white", bg="#203243")
label4.place(x=40, y=180)

label5 = Label(root, text="Description", font=('Helvetica', 11), fg="white", bg="#203243")
label5.place(x=40, y=200)

# Search box
try:
    Search_image = PhotoImage(file="Rounded Rectangle 3.png")
    myimage = Label(image=Search_image, bg="#57adff")
    myimage.place(x=270, y=120)
except Exception as e:
    print(f"Could not load search box image: {e}")
    # Create a fallback search box
    search_frame = Frame(root, width=420, height=60, bg="#203243")
    search_frame.place(x=270, y=120)

try:
    weat_image = PhotoImage(file="Layer 7.png")
    weatherimage = Label(root, image=weat_image, bg="#203243")
    weatherimage.place(x=290, y=130)
except Exception as e:
    print(f"Could not load weather icon: {e}")

# Search text field
textfield = tk.Entry(root, justify='center', width=15, font=('poppins', 25, 'bold'), bg="#203243", border=0, fg='white')
textfield.place(x=370, y=135)
textfield.focus()

# Search button
try:
    Search_icon = PhotoImage(file="Layer 6.png")
    myimage_icon = Button(image=Search_icon, borderwidth=0, cursor="hand2", bg="#203243", command=getWeather)
    myimage_icon.place(x=640, y=124)
except Exception as e:
    print(f"Could not load search icon: {e}")
    # Create a fallback search button
    search_button = Button(root, text="Search", bg="#203243", fg="white", font=('Helvetica', 12),
                           borderwidth=0, cursor="hand2", command=getWeather)
    search_button.place(x=640, y=135)

# Bottom Box
frame = Frame(root, width=900, height=180, bg="#212120")
frame.pack(side=BOTTOM)

# Bottom boxes for forecast
try:
    firstbox = PhotoImage(file="Rounded Rectangle 2.png")
    secondbox = PhotoImage(file="Rounded Rectangle 2 copy.png")

    Label(frame, image=firstbox, bg="#212120").place(x=30, y=20)
    Label(frame, image=secondbox, bg="#212120").place(x=300, y=30)
    Label(frame, image=secondbox, bg="#212120").place(x=400, y=30)
    Label(frame, image=secondbox, bg="#212120").place(x=500, y=30)
    Label(frame, image=secondbox, bg="#212120").place(x=600, y=30)
    Label(frame, image=secondbox, bg="#212120").place(x=700, y=30)
    Label(frame, image=secondbox, bg="#212120").place(x=800, y=30)
except Exception as e:
    print(f"Could not load bottom boxes: {e}")

# Clock (where we will place time)
clock = Label(root, font=("Helvetica", 30, 'bold'), fg="white", bg="#57adff")
clock.place(x=30, y=20)

# Timezone and coordinates
timezone = Label(root, font=("Helvetica", 20), fg="white", bg="#57adff")
timezone.place(x=680, y=20)

long_lat = Label(root, font=("Helvetica", 10), fg="white", bg="#57adff")
long_lat.place(x=700, y=50)

# Weather information labels
temperature_label = Label(root, font=("Helvetica", 11), fg="white", bg="#203243")
temperature_label.place(x=135, y=120)

humidity_label = Label(root, font=("Helvetica", 11), fg="white", bg="#203243")
humidity_label.place(x=135, y=140)

pressure_label = Label(root, font=("Helvetica", 11), fg="white", bg="#203243")
pressure_label.place(x=135, y=160)

wind_label = Label(root, font=("Helvetica", 11), fg="white", bg="#203243")
wind_label.place(x=135, y=180)

description_label = Label(root, font=("Helvetica", 11), fg="white", bg="#203243")
description_label.place(x=130, y=200)

# First cell (today's forecast)
firstframe = Frame(root, width=230, height=132, bg="#282829")
firstframe.place(x=35, y=315)

day1 = Label(firstframe, font="arial 20", bg="#282829", fg="#fff")
day1.place(x=100, y=5)

firstimage = Label(firstframe, bg="#282829")
firstimage.place(x=1, y=15)

day1temp = Label(firstframe, bg="#282829", fg="#57adff", font="arial 15 bold")
day1temp.place(x=100, y=50)

# Second cell
secondframe = Frame(root, width=70, height=115, bg="#282829")
secondframe.place(x=305, y=325)

day2 = Label(secondframe, bg="#282829", fg="#fff")
day2.place(x=10, y=5)

secondimage = Label(secondframe, bg="#282829")
secondimage.place(x=7, y=20)

day2temp = Label(secondframe, bg="#282829", fg="#fff")
day2temp.place(x=10, y=70)

# Third cell
thirdframe = Frame(root, width=70, height=115, bg="#282829")
thirdframe.place(x=405, y=325)

day3 = Label(thirdframe, bg="#282829", fg="#fff")
day3.place(x=10, y=5)

thirdimage = Label(thirdframe, bg="#282829")
thirdimage.place(x=7, y=20)

day3temp = Label(thirdframe, bg="#282829", fg="#fff")
day3temp.place(x=10, y=70)

# Fourth cell
fourthframe = Frame(root, width=70, height=115, bg="#282829")
fourthframe.place(x=505, y=325)

day4 = Label(fourthframe, bg="#282829", fg="#fff")
day4.place(x=10, y=5)

fourthimage = Label(fourthframe, bg="#282829")
fourthimage.place(x=7, y=20)

day4temp = Label(fourthframe, bg="#282829", fg="#fff")
day4temp.place(x=10, y=70)

# Fifth cell
fifthframe = Frame(root, width=70, height=115, bg="#282829")
fifthframe.place(x=605, y=325)

day5 = Label(fifthframe, bg="#282829", fg="#fff")
day5.place(x=10, y=5)

fifthimage = Label(fifthframe, bg="#282829")
fifthimage.place(x=7, y=20)

day5temp = Label(fifthframe, bg="#282829", fg="#fff")
day5temp.place(x=10, y=70)

# Sixth cell
sixthframe = Frame(root, width=70, height=115, bg="#282829")
sixthframe.place(x=705, y=325)

day6 = Label(sixthframe, bg="#282829", fg="#fff")
day6.place(x=10, y=5)

sixthimage = Label(sixthframe, bg="#282829")
sixthimage.place(x=7, y=20)

day6temp = Label(sixthframe, bg="#282829", fg="#fff")
day6temp.place(x=10, y=70)

# Seventh cell
seventhframe = Frame(root, width=70, height=115, bg="#282829")
seventhframe.place(x=805, y=325)

day7 = Label(seventhframe, bg="#282829", fg="#fff")
day7.place(x=10, y=5)

seventhimage = Label(seventhframe, bg="#282829")
seventhimage.place(x=7, y=20)

day7temp = Label(seventhframe, bg="#282829", fg="#fff")
day7temp.place(x=10, y=70)

# Start the application
root.mainloop()