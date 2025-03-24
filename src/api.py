from dotenv import dotenv_values
import os
import pandas
import requests
import json
import types

config = dotenv_values(".env")


def get_places(api_key: str, url: str, query: str, max_requests=50):
    """
    Get places from Google Places API.

    Args:
        api_key: str - Google Places API key
        url: str - Google Places API URL
        query: str - name of the city
    """

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "nextPageToken,places.id,places.name,places.displayName,places.formattedAddress,places.priceLevel,places.attributions,places.location,places.priceLevel,places.rating,places.userRatingCount,places.servesBreakfast,places.servesBrunch,places.servesCoffee,places.servesDessert,places.servesDinner,places.servesLunch,places.servesVegetarianFood,places.goodForChildren,places.allowsDogs,places.googleMapsLinks",
    }

    data = {"textQuery": query}

    try:
        respone = requests.post(url, headers=headers, json=data, timeout=10)
        respone.raise_for_status()
        return respone.json()

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return None

    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return None


data = get_places(
    config["API_KEY"], config["URL_GOOGLE_APIS_PLACE"], query="restaurants in Poznań"
)
print(data)
