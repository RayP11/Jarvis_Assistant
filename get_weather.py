from requests_html import HTMLSession
import requests


#NEW METHOD FOR WEATHER
#From National Weather Service


import requests

def get_weather():
    # Coordinates for Sykesville, MD
    lat = 39.3535
    lng = -76.9739

    # Initialize an empty string to store the weather details
    weather_report = ""

    # Get gridpoints using the latitude and longitude
    grid_url = f'https://api.weather.gov/points/{lat},{lng}'
    response = requests.get(grid_url)

    if response.status_code == 200:
        data = response.json()
        grid_x = data['properties']['gridX']
        grid_y = data['properties']['gridY']

        # Now get the forecast using the gridpoints
        forecast_url = f'https://api.weather.gov/gridpoints/{data["properties"]["gridId"]}/{grid_x},{grid_y}/forecast'
        forecast_response = requests.get(forecast_url)

        if forecast_response.status_code == 200:
            forecast_data = forecast_response.json()
            periods = forecast_data['properties']['periods']

            # Add a header to the report
            weather_report += "Weather forecast for Sykesville, MD:\n"

            # Add weather details for each period to the string
            for period in periods:
                name = period['name']
                temperature = period['temperature']
                temperature_unit = period['temperatureUnit']
                detailed_forecast = period['detailedForecast']
                weather_report += f"{name}: {temperature}{temperature_unit}\n"
                weather_report += f"  {detailed_forecast}\n"
        
        else:
            weather_report += "Error fetching forecast data from NWS.\n"
    else:
        weather_report += "Error: Could not find gridpoints for Sykesville, MD.\n"
    
    # Return the weather report string
    return weather_report









#OUTDATED Web-scraping for weather

# def weather(location):
#     """
#     Fetches the current weather for a given location using web scraping.

#     Args:
#         location (str): The location for which the weather is to be fetched.

#     Returns:
#         str: A description of the current weather at the given location.
#     """
#     s = HTMLSession()
#     query = location
#     url = f'https://www.google.com/search?q=weather+{query}'

#     try:
#         r = s.get(url, headers={
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
#         })
#         r.raise_for_status()  # Raise an HTTPError for bad responses

#         # Extract weather information
#         temp_element = r.html.find('span#wob_tm', first=True)
#         desc_element = r.html.find('div.VQF4g span#wob_dc', first=True)

#         if temp_element and desc_element:
#             temp = temp_element.text
#             desc = desc_element.text
#             weather_report = f"In {query}, it is currently {temp} degrees and it is {desc}."
#         else:
#             # Log which element is missing
#             print(f"Debug: temp_element={temp_element}, desc_element={desc_element}")
#             weather_report = "Could not retrieve complete weather information."

#     except Exception as e:
#         # Log the specific error and URL for debugging
#         print(f"An error occurred while fetching weather data: {e}")
#         print(f"Failed URL: {url}")
#         weather_report = "Sorry, I couldn't fetch the weather information at the moment."

#     return weather_report
