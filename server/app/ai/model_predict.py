from myapp.app.ai.model_loader import *
import pandas as pd
import numpy as np


import requests
from datetime import datetime

API_KEY = "a849bef4a9975e9f2d3f01f0ac2136c2"

# Function to get weather data
def get_weather(city_name, api_key):
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"

    # Constructing the full URL
    final_url = BASE_URL + "q=" + city_name + "&appid=" + api_key

    # Sending GET request
    response = requests.get(final_url)
    data = response.json()

    # Check HTTP status code
    if response.status_code == 200:
        # Extract and return the main weather data
        return data
    else:
        print("Error:", data['message'])
        return None


def get_weather_forecast(city_name, api_key, target_datetime):
    BASE_URL = "http://api.openweathermap.org/data/2.5/forecast?"
    final_url = BASE_URL + "q=" + city_name + "&appid=" + api_key
    response = requests.get(final_url)
    data = response.json()

    # Check HTTP status code
    if response.status_code != 200:
        print("Error:", data['message'])
        return None

    # Convert target_datetime to timestamp
    target_timestamp = int(target_datetime.timestamp())

    # Find the closest forecast to the target datetime
    closest_forecast = None
    for forecast in data['list']:
        if abs(forecast['dt'] - target_timestamp) < 1800:  # 1800 seconds = 30 minutes
            closest_forecast = forecast
            break

    return closest_forecast




def define_part_of_day(hour, df):
    if (hour >= 5) and (hour < 12):
      df['part_of_day'] = ['morning']
    if (hour >= 12) and (hour < 17):
      df['part_of_day'] = ['afternoon']
    if (hour >= 17) and (hour < 21):
      df['part_of_day'] = ['evening']
    if (hour >= 21) or (hour < 5):
      df['part_of_day'] = ['night']



# Manhattan and Euclidean (Havesine) distances
def distance(df, method="manhattan"):
    earthR = 6378137.0
    pi180 = np.pi/180

    dlat = (df.dropoff_latitude - df.pickup_latitude) * pi180
    dlng = (df.dropoff_longitude - df.pickup_longitude) * pi180

    if method == "manhattan":
        ay = np.sin(np.abs(dlat)/2)**2
        cy = 2*np.arctan2(np.sqrt(ay), np.sqrt(1-ay))
        dy = earthR * cy

        ax = np.sin(np.abs(dlng)/2)**2
        cx = 2*np.arctan2(np.sqrt(ax), np.sqrt(1-ax))
        dx = earthR * cx

        distance = (np.abs(dx) + np.abs(dy)) /1000

    elif method == "euclidean":
        a = (np.sin(dlat/2)**2 + np.cos(df.pickup_latitude*pi180) * np.cos(df.dropoff_latitude*pi180) * np.sin(dlng/2)**2)
        c = 2*np.arctan2(np.sqrt(a), np.sqrt(1-a))

        distance = (earthR * c) /1000

    else:
        distance = 0

    return distance

##########################################################

holidays2023 = {
    "New Years Day": datetime(2023,1,2).date(),
    "Martin Luther King Jr. Birthday": datetime(2023,1,16).date(),
    "Lincoln's Birthday": datetime(2023,2,13).date(),
    "Washington's Birthday": datetime(2023,2,20).date(),
    "Memorial Day": datetime(2023,5,29).date(),
    "Flag Day": datetime(2023,6,11).date(),
    "Juneteenth": datetime(2023,6,19).date(),
    "Independence Day": datetime(2023,7,4).date(),
    "Independence Post-day": datetime(2023,7,5).date(),
    "Labor Day": datetime(2023,9,4).date(),
    "Columbus Day": datetime(2023,10,9).date(),
    "Election Day": datetime(2023,11,7).date(),
    "Veterans Day": datetime(2023,11,11).date(),
    "Thanksgiving Day": datetime(2023,11,23).date(),
    "Thanksgiving Post-day": datetime(2023,11,24).date(),
    "Thanksgiving Post-post-day": datetime(2023,11,25).date(),
    "Christmas Eve": datetime(2023,12,24).date(),
    "Christmas Day": datetime(2023,12,25).date(),
    "Christmas Post-day": datetime(2023,12,26).date(),
    "New Years Eve": datetime(2023,12,31).date(),
}

##########################################################


weather_dict = {
                'overcast clouds': 0,
                'mist': 0,  # This could be similar to haze
                'broken clouds': 0,  # This might be considered partly cloudy
                'few clouds': 0,  # This is also partly cloudy
                'scattered clouds': 0,

                'clear sky': 2,

                'moderate rain': 3,
                'light rain': 3,
                'heavy intensity rain': 3,
                'very heavy rain': 3,
                'extreme rain': 3,
                'freezing rain': 3,
                'light intensity drizzle': 3,
                'drizzle': 3,
                'heavy intensity drizzle': 3,

                'light snow': 4,
                'snow': 4,
                'heavy snow': 4,
                'sleet': 4,
                'light shower sleet': 4,
                'shower sleet': 4,
                'light rain and snow': 4,
                'rain and snow': 4,
                'light shower snow': 4,
                'shower snow': 4,
                'heavy shower snow': 4,

                # Add more descriptions as needed.
}


wind_dir_dict = {'E' : 0,
                 'ENE' : 0,
                 'ESE' : 0,

                 'W' : 1,
                 'WSW' : 1,
                 'WNW' : 1,

                 'S' : 2,
                 'SSE' : 2,
                 'SSW' : 2,

                 'N' : 3,
                 'NNE' : 3,
                 'NNW' : 3,

                 'Variable' : 4,
                 'Calm' : 5,
                 'SW' : 6,
                 'NW' : 7,
                 'NE' : 8,
                 'SE' : 9,
                 'Unknown' : 10
                }


def degrees_to_cardinal(d):
    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    ix = int((d + 11.25)/22.5)
    return dirs[ix % 16]


def test_model(pickup_longitude,  dropoff_longitude, pickup_latitude, dropoff_latitude, _datetime, weather_att=False, forecast= False):

    df = pd.DataFrame()
    hour = _datetime.hour
    df['month'] = [_datetime.month]
    df["dayofmonth"] = [_datetime.day]
    df[	"dayofweek"] = [_datetime.weekday()]



    # Creating `part_of_day` feature

    define_part_of_day(hour, df)

    # Creating `distance` column using manhattan,  euclidean

    df["pickup_longitude"] = [pickup_longitude]
    df["dropoff_longitude"] = [dropoff_longitude]
    df["pickup_latitude"] = [pickup_latitude]
    df["dropoff_latitude"] = [dropoff_latitude]

    df['manhattan_distance'] = distance(df)
    df['euclidean_distance'] = distance(df, "euclidean")
    df.drop(['pickup_longitude', 'dropoff_longitude', 'pickup_latitude', 'dropoff_latitude'], axis=1, inplace=True)


    # Creating `holiday` feature

    if _datetime.date() in holidays2023.values():
       df["holiday"] = [1]
    else:
       df["holiday"] = [0]


    # Creating 'weather' feature

    if weather_att:
      if forecast:
          weather_data = get_weather_forecast("New York", API_KEY, _datetime)
      else:
          weather_data = get_weather("New York", API_KEY)
      if weather_data:
          main_data = weather_data['main']
          wind_data = weather_data.get('wind', {})
          weather_conditions = weather_data.get('weather', [{}])[0]

          df["Temp."] = main_data.get('temp', 273.15) - 273.15
          df["Humidity"] =  main_data.get('humidity', 0.0)
          df["Pressure"] = main_data.get('pressure', 0.0)
          df["Dew Point"] = main_data.get('temp_min', 273.15) - 273.15
          df["Visibility"] =  weather_data.get('visibility', 0.0) / 1000
          df["Wind Dir"] = wind_data.get('deg', 0.0)
          df["Wind Speed"] = wind_data.get('speed', 0.0)
          df["Gust Speed"] =  wind_data.get('gust', 0.0)
          df["Precip"] = weather_data.get('rain', {}).get('1h', 0.0)
          df["Conditions"] = weather_conditions.get('description', 'Unknown')

          df["Conditions"] = df["Conditions"].apply(lambda x: weather_dict.get(x, 1))

          df["Wind Dir"] = degrees_to_cardinal(df["Wind Dir"])
          df["Wind Dir"] = df["Wind Dir"].apply(lambda x: wind_dir_dict.get(x,10))


    # Model pipeline
    if weather_att:
      model_weather_xgb = model_xgb_with_weather
    else:
      model_xgb = model_xgb_without_weather

    pipe = model_xgb



    pred = pipe.predict(df)

    return pred
