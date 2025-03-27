from dotenv import dotenv_values
import os
import pandas as pd
import requests
import json
import time
import logging
import logging.config
import yaml


# Load environment variables from .env file
config = dotenv_values(".env")

# Configure logging using YAML config file
with open(config["LOGGING_CONFIG"], "r") as file:
    config_logging = yaml.safe_load(file)
    logging.config.dictConfig(config_logging)

logger = logging.getLogger(__name__)


def get_cities_list(config_file_path: str, spot_type: str) -> list:
    """
    Prepare a list of cities for a given type of spot.
    Args:
        config_file_path: str - path to the configuration file
        type_of_spot: str - type of spot (e.g. restaurants in..., hotels in...)
    """
    try:
        with open(config_file_path, "r", encoding="utf-8") as f:
            cities_list = json.load(f)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return []

    cities_list = cities_list["City"]
    cities_list = [city for sublist in cities_list for city in sublist]
    cities_list = [spot_type + city for city in cities_list]

    return cities_list


def get_places(api_key: str, url: str, query: str, page_token: str = None) -> dict:
    """
    Get places from Google Places API.

    Args:
        api_key: str - Google Places API key
        url: str - Google Places API URL
        query: str - name of the city

    Returns:
        dict: JSON response from the API or empty dict in case of an error
    """

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "nextPageToken,places.id,places.name,places.displayName,places.formattedAddress,places.priceLevel,places.attributions,places.location,places.priceLevel,places.rating,places.userRatingCount,places.servesBreakfast,places.servesBrunch,places.servesCoffee,places.servesDessert,places.servesDinner,places.servesLunch,places.servesVegetarianFood,places.goodForChildren,places.allowsDogs,places.googleMapsLinks",
    }

    data = {"textQuery": query}

    if page_token:
        data["pageToken"] = page_token
        logger.debug(f"Fetching places with token: {page_token}")

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        logger.debug("Response status code: {response.status_code}")
        logger.debug(f"Used URL: {response.url}")
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.info(f"Request error: {e}")
        return {}

    except Exception as e:
        logger.info(f"Unexpected error occurred: {e}")
        return {}


def get_all_city_places(
    api_key: str, url: str, query: str, max_results: int, page_token: str = None
) -> list:
    """
    Get all places for a given query.
    Args:
        api_key: str - Google Places API key
        url: str - Google Places API URL
        query: str - name of the city
        max_results: int - maximum number of results
    Returns:
        list: list of places
    """
    results = []

    while len(results) < max_results:
        logger.debug(f"get_all_city_places funtion - page_token: {page_token}")
        data = get_places(api_key, url, query, page_token)

        places = data.get("places", [])
        results.extend(places)

        if "nextPageToken" in data and len(results) < max_results:
            page_token = data["nextPageToken"]
            time.sleep(2)
        else:
            break

    return results


def get_all(api_key: str, url: str, query: list, max_results: int = 40) -> list:
    """
    Get places from all the cities in the list.
    Args:
        api_key: str - Google Places API key
        url: str - Google Places API URL
        query: list - list of cities
    Returns:
        list: List of all retrived places accross all cities.

    """
    all_results = []
    for city in query:
        try:
            city_results = get_all_city_places(api_key, url, city, max_results)
            all_results.extend(city_results)
            logger.info(f"City: {city} - Number of places: {len(city_results)}")
        except Exception as e:
            logger.info(f"Error occurred: {e}")

    return all_results


if __name__ == "__main__":
    list_of_spots = get_cities_list(
        config_file_path=config["LIST_OF_CITIES"], spot_type=config["SPOT_TYPE"]
    )

    places_data = get_all(
        api_key=config["API_KEY"],
        url=config["URL_GOOGLE_APIS_PLACE"],
        query=list_of_spots,
        max_results=40,
    )
    with open(config["DATA_LOCATION"], "w") as f:
        json.dump(places_data, f)
