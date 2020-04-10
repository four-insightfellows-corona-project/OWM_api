#!/usr/bin/env python3

'''
Captures the current weather conditions from OpenWeatherMap API.

Note: In order for this to work you need to install the
develop branch of pyowm, this can be done using:

    pip install git+https://github.com/csparpa/pyowm.git@develop

'''

import os
import pyowm
import pandas as pd

from auth import (
    OWM_api_key)


def data_file_path(folder, datafile):
    ''' give folder and file,
        returns file path
    '''
    return os.path.join(os.path.dirname(os.getcwd()), folder, datafile)


OWM_forcast_cols = ['park_name', 'reception_time', 'reference_time',
                    'sunset_time', 'sunrise_time', 'clouds', 'rain_1h',
                    'snow_1h', 'wind_speed', 'wind_deg', 'humidity', 'press',
                    'temp', 'temp_feels', 'temp_max', 'temp_min', 'status',
                    'detailed_status']

owm = pyowm.OWM(OWM_api_key)

park_loc = pd.DataFrame({
    'name': ['Prospect Park', 'Wooster Square'],
    'lat': [40.662551, 41.304745],
    'long': [-73.969256, -72.917757],
    'tz_correct': [-14400, -14400]})

park_name = 'Prospect Park'
park_lat = park_loc.loc[park_loc.name == park_name, 'lat'].iloc[0]
park_long = park_loc.loc[park_loc.name == park_name, 'long'].iloc[0]
tz_correct = park_loc.loc[park_loc.name == park_name, 'tz_correct'].iloc[0]

obs = owm.weather_at_coords(float(park_lat), float(park_long))
wethr = obs.get_weather()

wethr_rain = 0
if wethr.get_rain():
    wethr_rain = wethr.get_rain()['1h']

wethr_snow = 0
if wethr.get_snow():
    wethr_snow = wethr.get_snow()['1h']

to_add_dict = {
    'park_name': [park_name],
    'reception_time': [obs.get_reception_time('unix') + int(tz_correct)],
    'reference_time': [wethr.get_reference_time() + int(tz_correct)],
    'sunrise_time': [wethr.get_sunrise_time()],
    'sunset_time': [wethr.get_sunset_time()],
    'clouds': [wethr.get_clouds()],
    'rain_1h': [wethr_rain],
    'snow_1h': [wethr_snow],
    'wind_speed': [wethr.get_wind(unit='meters_sec')['speed']],
    'wind_deg': [wethr.get_wind(unit='meters_sec')['deg']],
    'humidity': [wethr.get_humidity()],
    'press': [wethr.get_pressure()['press']],
    'temp': [wethr.get_temperature(unit='fahrenheit')['temp']],
    'temp_feels': [wethr.get_temperature(unit='fahrenheit')['feels_like']],
    'temp_max': [wethr.get_temperature(unit='fahrenheit')['temp_max']],
    'temp_min': [wethr.get_temperature(unit='fahrenheit')['temp_min']],
    'status': [wethr.get_status()],
    'detailed_status': [wethr.get_detailed_status()]}

current_wethr_df = pd.DataFrame(to_add_dict)

log_path = data_file_path('weather_data', 'current_log.csv')

if os.path.exists(log_path):
    current_log = pd.read_csv(log_path, index_col=0)
else:
    current_log = pd.read_csv(
        data_file_path('weather_data', 'example_current_df.csv'), index_col=0)

current_log = current_log.append(current_wethr_df, ignore_index=True)

current_log.to_csv(log_path)
