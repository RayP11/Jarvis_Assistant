from requests_html import HTMLSession

def weather(location):
    """
    Fetches the current weather for a given location using web scraping.

    Args:
        location (str): The location for which the weather is to be fetched.

    Returns:
        str: A description of the current weather at the given location.
    """
    s = HTMLSession()
    query = location
    url = f'https://www.google.com/search?q=weather+{query}'

    try:
        r = s.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'})
        r.raise_for_status()  # Raise an HTTPError for bad responses

        # Extract weather information
        temp_element = r.html.find('span#wob_tm', first=True)
        desc_element = r.html.find('div.VQF4g', first=True).find('span#wob_dc', first=True)

        if temp_element and desc_element:
            temp = temp_element.text
            desc = desc_element.text
            weather_report = f"In {query} it is currently {temp} degrees, and it is {desc}."
        else:
            weather_report = "Could not retrieve complete weather information."

    except Exception as e:
        print(f"An error occurred while fetching weather data: {e}")
        weather_report = "Sorry, I couldn't fetch the weather information at the moment."

    return weather_report