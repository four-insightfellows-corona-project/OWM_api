#!/bin/bash

'''
Note: In order for this to work you need to install the
develop branch of pyowm, this can be done using:

    pip install git+https://github.com/csparpa/pyowm.git@develop

'''

import os
import pyowm
import pandas as pd
import numpy as np
import json
import requests
from pyowm.weatherapi25.parsers import forecastparser

from auth import (
    OWM_api_key)

OWM_forcast_cols = ['park_name', 'reception_time', 'reference_time',
                    'sunset_time', 'sunrise_time', 'clouds', 'rain', 'snow',
                    'wind_speed', 'wind_deg', 'humidity', 'press', 'press_sea',
                    'temp', 'temp_feels', 'temp_max', 'temp_min', 'status',
                    'detailed_status']

def forcast_to_df(park_forcast, t_sunrise, t_sunset, tz_correct):
    ''' Takes a forcast object and sunrise/sunset time,
        Returns datafram of relevant info
    '''
    # Neet to adjust sunrise/set times, should only go
    # into columns of the same day (or just use last day in window?)

    forcast_df = pd.DataFrame(columns=OWM_forcast_cols)

    for x in park_forcast.get_weathers():
        if (t_sunrise == 0) or (t_sunset == 0):
            x_sunrise = np.nan
            x_sunset = np.nan
        else:
            x_sunrise = t_sunrise + tz_correct
            x_sunset = t_sunset + tz_correct

        x_rain = 0
        if x.get_rain():
            x_rain = x.get_rain()['3h']

        x_snow = 0
        if x.get_snow():
            x_snow = x.get_snow()['3h']

        to_add_dict = {
            'park_name': [park_name],
            'reception_time': [park_forcast.get_reception_time('unix') + tz_correct],
            'reference_time': [x.get_reference_time() + tz_correct],
            'sunrise_time': [x_sunrise],
            'sunset_time': [x_sunset],
            'clouds': [x.get_clouds()],
            'rain': [x_rain],
            'snow': [x_snow],
            'wind_speed': [x.get_wind(unit='meters_sec')['speed']],
            'wind_deg': [x.get_wind(unit='meters_sec')['deg']],
            'humidity': [x.get_humidity()],
            'press': [x.get_pressure()['press']],
            'press_sea': [x.get_pressure()['sea_level']],
            'temp': [x.get_temperature(unit='fahrenheit')['temp']],
            'temp_feels': [x.get_temperature(unit='fahrenheit')['feels_like']],
            'temp_max': [x.get_temperature(unit='fahrenheit')['temp_max']],
            'temp_min': [x.get_temperature(unit='fahrenheit')['temp_min']],
            'status': [x.get_status()],
            'detailed_status': [x.get_detailed_status()]}

        to_add = pd.DataFrame(to_add_dict)
        forcast_df = forcast_df.append(to_add, ignore_index=True)
    return forcast_df


owm = pyowm.OWM(OWM_api_key)

park_loc = pd.DataFrame({
    'name': ['Prospect Park', 'Wooster Square'],
    'lat': [40.662551, 41.304745],
    'long': [-73.969256, -72.917757]})

park_name = 'Prospect Park'
park_lat = park_loc.loc[park_loc.name == park_name, 'lat'].iloc[0]
park_long = park_loc.loc[park_loc.name == park_name, 'long'].iloc[0]

api_url = 'http://api.openweathermap.org/data/2.5/forecast'
payload = {
    'lat': park_lat,
    'lon': park_long,
    'appid': OWM_api_key}

owm_req = requests.get(api_url, params=payload)

owm_json = json.loads(owm_req.text)

sunrise_time = owm_json['city']['sunrise']
sunset_time = owm_json['city']['sunset']
tz_correct = owm_json['city']['timezone']

weather_df = forcast_to_df(
    forecastparser.ForecastParser().parse_JSON(owm_req.text),
    sunrise_time, sunset_time, tz_correct)

if os.path.exists('./weather_data/weather_log.csv'):
    weather_log = pd.read_csv(
        './weather_data/weather_log.csv', index_col=0)
else:
    weather_log = pd.read_csv(
        './weather_data/example_weather_df.csv', index_col=0)

weather_log = weather_log.append(weather_df, ignore_index=True)

weather_log.to_csv('./weather_data/weather_log.csv')
