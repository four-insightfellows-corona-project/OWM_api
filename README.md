# OWM_api

Code for working with the Open Weather Map API.

---

## Folders in this repo
### notebooks
Contains jupyter notebooks that were produced during development & for EDA.

### social_parks_weather
Contains the scripts that are run periodically to gather a running log of
weather data.

### weather_data
Contains example data.

---

## Open Weather Map API access
In order to pull data from the OWM API, add a file called *auth.py* to the
*notebooks* & *social_parks_weather* folders with the following:

**auth.py**
```
# Open Weather Map API key
OWM_api_key = 'YOUR_API_KEY'
```
