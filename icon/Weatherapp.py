from sqlite3.dbapi2 import apilevel
from tkinter import *
import tkinter as tk

from django.db.models.expressions import result
from geopy.geocoders import Nominatim
from tkinter import ttk, messagebox

from numpy.ma.core import resize
from timezonefinder import TimezoneFinder
from datetime import datetime, timedelta
import requests
import pytz
import json
from PIL import Image, ImageTk

# Initialize the main window
root = tk.Tk()  # Corrected from TK() to tk.Tk()
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
            weather_data = requests.get(weather_api).json()

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
            temperature_label.config(text=(f"{temp:.1f}", "°C"))
            humidity_label.config(text=(humidity, "%"))
            pressure_label.config(text=(pressure, "hPa"))
            wind_label.config(text=(f"{wind_speed:.1f}", "m/s"))
            description_label.config(text=description)

            # Fetch 5-day forecast data (free API)
            forecast_api = f"https://api.openweathermap.org/data/2.5/forecast?lat={location.latitude}&lon={location.longitude}&units=metric&appid={API_KEY}"
            forecast_data = requests.get(forecast_api).json()

            if forecast_data.get("cod") != "200":
                messagebox.showerror("Error", f"Forecast data not available ({forecast_data.get('message')})")
                return

            # Parse the 5-day forecast (every 3 hours, we'll take data at noon each day)
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
                photo1 = ImageTk.PhotoImage(file=f"icon/{current_icon}@2x.png")
                firstimage.config(image=photo1)
                firstimage.image = photo1  # Keep a reference
            except Exception as e:
                print(f"Error loading today's weather icon: {e}")

            day_temp = temp
            night_temp = temp - 5.0  # Estimate for demonstration
            day1temp.config(text=f"Day:{day_temp:.1f}\n Night:{night_temp:.1f}")

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
                        img = Image.open(f"icon/{forecast['icon']}@2x.png")
                        resized_image = img.resize((50, 50))
                        photo = ImageTk.PhotoImage(resized_image)
                        image_label.config(image=photo)
                        image_label.image = photo  # Keep a reference
                    except Exception as e:
                        print(f"Error loading day {day_num} image: {e}")

                    temp_label.config(text=f"Day:{day_temp:.1f}\n Night:{night_temp:.1f}")

        else:
            timezone.config(text="Timezone: Not Found")
            long_lat.config(text="Longitude and latitude Not Found")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to get data: {str(e)}")
        # Print detailed error for debugging
        import traceback
        traceback.print_exc()


##icon
image_icon = PhotoImage(file="logo.png")
root.iconphoto(False,image_icon)

Round_box = PhotoImage(file="Rounded Rectangle 1.png")
Label(root,image=Round_box, bg="#57adff").place(x=25, y=110)


#label
label1 = Label(root, text="Temperature", font=('Helvetica',11), fg="white", bg="#203243")
label1.place(x=40, y=120)

label2 = Label(root, text="Humidity", font=('Helvetica',11), fg="white", bg="#203243")
label2.place(x=40, y=140)

label3 = Label(root, text="Pressure", font=('Helvetica',11), fg="white", bg="#203243")
label3.place(x=40, y=160)

label4 = Label(root, text="Wind speed", font=('Helvetica',11), fg="white", bg="#203243")
label4.place(x=40, y=180)

label5 = Label(root, text="Description", font=('Helvetica',11), fg="white", bg="#203243")
label5.place(x=40, y=200)


##search box
Search_image = PhotoImage(file="Rounded Rectangle 3.png")
myimage = Label(image=Search_image, bg="#57adff")
myimage.place(x=270, y=120)

weat_image = PhotoImage(file="Layer 7.png")
weatherimage = Label(root, image=weat_image, bg="#203243")
weatherimage.place(x=290, y=130)
# weatherimage.place(x=290, y=140)


textfield = tk.Entry(root, justify='center', width=15, font=('poppins', 25, 'bold'), bg="#203243", border=0, fg='white')
textfield.place(x=370, y=135)
textfield.focus()


Search_icon = PhotoImage(file="Layer 6.png")
myimage_icon = Button(image=Search_icon, borderwidth=0, cursor="hand2", bg="#203243", command=getWeather)
myimage_icon.place(x=640, y=124)


##Bottom Box
frame= Frame(root, width=900, height=180, bg="#212120")
frame.pack(side=BOTTOM)


##bottom boxes
firstbox = PhotoImage(file="Rounded Rectangle 2.png")
secondbox = PhotoImage(file="Rounded Rectangle 2 copy.png")


Label(frame, image=firstbox, bg="#212120").place(x=30, y=20)
Label(frame, image=secondbox, bg="#212120").place(x=300,y=30)
Label(frame, image=secondbox, bg="#212120").place(x=400,y=30)
Label(frame, image=secondbox, bg="#212120").place(x=500,y=30)
Label(frame, image=secondbox, bg="#212120").place(x=600,y=30)
Label(frame, image=secondbox, bg="#212120").place(x=700,y=30)
Label(frame, image=secondbox, bg="#212120").place(x=800,y=30)


#clock (here we will place time)
clock = Label(root, font=("Helvetica", 30, 'bold'), fg="white", bg="#57adff")
clock.place(x=30, y=20)



#timezone
timezone = Label(root, font=("Helvetica", 20), fg="white", bg="#57adff")
timezone.place(x=680, y=20)

long_lat = Label(root, font=("Helvetica", 10), fg="white", bg="#57adff")
long_lat.place(x=700, y=50)

#thpwd
# t = Label(root, text="temp", font=("Helvetica", 11), fg="white", bg="#203243")
# t.place(x=150, y=120)


clock = Label(root, font=("Helvetica", 30, 'bold'), fg="white", bg="#57adff")
clock.place(x=30, y=20)

temperature_label = Label(root,  font=("Helvetica", 11), fg="white", bg="#203243")
temperature_label.place(x=135, y=120)

humidity_label = Label(root, font=("Helvetica", 11), fg="white", bg="#203243")
humidity_label.place(x=135, y=140)

pressure_label = Label(root, font=("Helvetica", 11), fg="white", bg="#203243")
pressure_label.place(x=135, y=160)

wind_label = Label(root, font=("Helvetica", 11), fg="white", bg="#203243")
wind_label.place(x=135, y=180)

description_label = Label(root, font=("Helvetica", 11), fg="white", bg="#203243")
description_label.place(x=130, y=200)


#first cell
firstframe = Frame(root, width=230, height=132, bg="#282829")
firstframe.place(x=35, y=315)

day1 = Label(firstframe, font="arial 20", bg="#282829", fg="#fff")
day1.place(x=100, y=5)

firstimage = Label(firstframe, bg="#282829")
firstimage.place(x=1, y=15)

day1temp = Label(firstframe, bg="#282829", fg="#57adff", font="arial 15 bold")
day1temp.place(x=100, y=50)

##second cell
secondframe = Frame(root, width=70, height=115, bg="#282829")
secondframe.place(x=305, y=325)

day2 = Label(secondframe, bg="#282829", fg="#fff")
day2.place(x=10, y=5)

secondimage = Label(secondframe, bg="#282829")
secondimage.place(x=7, y=20)

day2temp = Label(secondframe, bg="#282829", fg="#fff")
day2temp.place(x=10, y=70)


##third cell
thirdframe = Frame(root, width=70, height=115, bg="#282829")
thirdframe.place(x=405, y=325)

day3 = Label(thirdframe, bg="#282829", fg="#fff")
day3.place(x=10, y=5)

thirdimage = Label(thirdframe, bg="#282829")
thirdimage.place(x=7, y=20)

day3temp = Label(thirdframe, bg="#282829", fg="#fff")
day3temp.place(x=10, y=70)

##fourth cell
fourthframe = Frame(root, width=70, height=115, bg="#282829")
fourthframe.place(x=505, y=325)

day4 = Label(fourthframe, bg="#282829", fg="#fff")
day4.place(x=10, y=5)

fourthimage = Label(fourthframe, bg="#282829")
fourthimage.place(x=7, y=20)

day4temp = Label(fourthframe, bg="#282829", fg="#fff")
day4temp.place(x=10, y=70)

##fifth cell
fifthframe = Frame(root, width=70, height=115, bg="#282829")
fifthframe.place(x=605, y=325)

day5 = Label(fifthframe, bg="#282829", fg="#fff")
day5.place(x=10, y=5)

fifthimage = Label(fifthframe, bg="#282829")
fifthimage.place(x=7, y=20)

day5temp = Label(fifthframe, bg="#282829", fg="#fff")
day5temp.place(x=10, y=70)

##sixth cell
sixthframe = Frame(root, width=70, height=115, bg="#282829")
sixthframe.place(x=705, y=325)

day6 = Label(sixthframe, bg="#282829", fg="#fff")
day6.place(x=10, y=5)

sixthimage = Label(sixthframe, bg="#282829")
sixthimage.place(x=7, y=20)

day6temp = Label(sixthframe, bg="#282829", fg="#fff")
day6temp.place(x=10, y=70)

##seventh cell
seventhframe = Frame(root, width=70, height=115, bg="#282829")
seventhframe.place(x=805, y=325)

day7 = Label(seventhframe, bg="#282829", fg="#fff")
day7.place(x=10, y=5)

seventhimage = Label(seventhframe, bg="#282829")
seventhimage.place(x=7, y=20)

day7temp = Label(seventhframe, bg="#282829", fg="#fff")
day7temp.place(x=10, y=70)









root.mainloop()  # Ensure mainloop is called to run the app


# import tkinter as tk
# from tkinter import ttk, messagebox
# from geopy.geocoders import Nominatim
# from timezonefinder import TimezoneFinder
# from datetime import datetime, timedelta
# import requests
# import pytz
# from PIL import Image, ImageTk
#
# # Initialize the main window
# root = tk.Tk()
# root.title("Weather App")
# root.geometry("890x470+300+200")
# root.configure(bg="#57adff")
# root.resizable(False, False)
#
# API_KEY = "df0fb183c8f5fa88b0aef4ef53cec0e6"
#
#
# def getWeather():
#     city = textfield.get().strip()
#     if not city:
#         messagebox.showerror("Error", "Please enter a city name")
#         return
#
#     try:
#         geolocator = Nominatim(user_agent="weather_app")
#         location = geolocator.geocode(city)
#         if location is None:
#             messagebox.showerror("Error", "City not found! Try again.")
#             return
#
#         obj = TimezoneFinder()
#         timezone_name = obj.timezone_at(lng=location.longitude, lat=location.latitude)
#         if timezone_name:
#             timezone.config(text=f"{timezone_name}")
#             long_lat.config(text=f"{round(location.latitude, 3)}°N, {round(location.longitude, 3)}°E")
#             home = pytz.timezone(timezone_name)
#             local_time = datetime.now(home).strftime("%I:%M %p")
#             clock.config(text=local_time)
#
#             api = f"https://api.openweathermap.org/data/2.5/weather?lat={location.latitude}&lon={location.longitude}&units=metric&appid={API_KEY}"
#             response = requests.get(api_url)
#             json_data = response.json()
#
#             if "cod" in json_data and json_data["cod"] != 200:
#                 messagebox.showerror("Error", json_data.get("message", "Weather data not found!"))
#                 return
#
#             current = json_data['current']
#             temperature_label.config(text=f"{current['temp']} °C")
#             humidity_label.config(text=f"{current['humidity']} %")
#             pressure_label.config(text=f"{current['pressure']} hPa")
#             wind_label.config(text=f"{current['wind_speed']} m/s")
#             description_label.config(text=current['weather'][0]['description'].title())
#
#             for i in range(7):
#                 day = datetime.now() + timedelta(days=i)
#                 day_labels[i].config(text=day.strftime("%A"))
#                 temp_labels[i].config(
#                     text=f"Day: {json_data['daily'][i]['temp']['day']}°C\nNight: {json_data['daily'][i]['temp']['night']}°C")
#                 icon = json_data['daily'][i]['weather'][0]['icon']
#                 img = Image.open(f"icon/{icon}@2x.png").resize((50, 50))
#                 photo = ImageTk.PhotoImage(img)
#                 image_labels[i].config(image=photo)
#                 image_labels[i].image = photo
#         else:
#             timezone.config(text="Timezone: Not Found")
#             long_lat.config(text="Longitude and latitude Not Found")
#     except Exception as e:
#         messagebox.showerror("Error", f"Failed to get data: {str(e)}")
#
#
# textfield = tk.Entry(root, justify='center', width=15, font=('poppins', 25, 'bold'), bg="#203243", border=0, fg='white')
# textfield.place(x=370, y=135)
# textfield.focus()
#
# search_button = tk.Button(root, text="Search", command=getWeather)
# search_button.place(x=640, y=124)
#
# timezone = tk.Label(root, font=("Helvetica", 20), fg="white", bg="#57adff")
# timezone.place(x=680, y=20)
# long_lat = tk.Label(root, font=("Helvetica", 10), fg="white", bg="#57adff")
# long_lat.place(x=700, y=50)
# clock = tk.Label(root, font=("Helvetica", 30, 'bold'), fg="white", bg="#57adff")
# clock.place(x=30, y=20)
#
# temperature_label = tk.Label(root, font=("Helvetica", 11), fg="white", bg="#203243")
# temperature_label.place(x=135, y=120)
# humidity_label = tk.Label(root, font=("Helvetica", 11), fg="white", bg="#203243")
# humidity_label.place(x=135, y=140)
# pressure_label = tk.Label(root, font=("Helvetica", 11), fg="white", bg="#203243")
# pressure_label.place(x=135, y=160)
# wind_label = tk.Label(root, font=("Helvetica", 11), fg="white", bg="#203243")
# wind_label.place(x=135, y=180)
# description_label = tk.Label(root, font=("Helvetica", 11), fg="white", bg="#203243")
# description_label.place(x=130, y=200)
#
# day_labels = []
# temp_labels = []
# image_labels = []
# for i in range(7):
#     frame = tk.Frame(root, width=70 if i else 230, height=115 if i else 132, bg="#282829")
#     frame.place(x=35 + i * 100, y=315 if i else 325)
#     day_label = tk.Label(frame, bg="#282829", fg="#fff")
#     day_label.place(x=10, y=5)
#     day_labels.append(day_label)
#     image_label = tk.Label(frame, bg="#282829")
#     image_label.place(x=7, y=20)
#     image_labels.append(image_label)
#     temp_label = tk.Label(frame, bg="#282829", fg="#fff", font="arial 10 bold")
#     temp_label.place(x=10, y=70)
#     temp_labels.append(temp_label)
#
# root.mainloop()
#
