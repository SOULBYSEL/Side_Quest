import requests
import os
import json
import re
from bs4 import BeautifulSoup
from steam_web_api import Steam
from requests_html import HTMLSession

def remove_html_tags(text):
    """
    Removes HTML tags from a given string.
    """
    return re.sub(r'<[^>]*>', '', text)

def calculate_tax(price, tax_rate):
    """
    Calculates the tax-inclusive price.
    
    Args:
        price (float): The base price of the product.
        tax_rate (float): The tax rate as a percentage (e.g., 13 for 13% tax).
    
    Returns:
        float: The price including tax.
    """
    return round(price * (1 + tax_rate / 100), 2)

def fetch_and_clean_steam_app_details(appid, country_code="CA", target_currency="CAD", tax_rate=13):
    """
    Fetches and cleans details of a Steam app using its app ID, including tax.
    """
    try:
        details_endpoint = f"https://store.steampowered.com/api/appdetails?appids={appid}&json=1&cc={country_code}"
        response = requests.get(details_endpoint)

        if response.status_code != 200:
            return f"Error: Failed to fetch data. HTTP Status Code: {response.status_code}"

        details = response.json()

        if str(appid) not in details or not details[str(appid)]["success"]:
            return f"Error: No data found for app ID {appid}."

        details = details[str(appid)]["data"]

        # Specify keys to retain
        keys_to_keep = [
            "name", "categories", "controller_support", "developers", "dlc",
            "genres", "is_free", "metacritic", "platforms", "price_overview",
            "publishers", "release_date", "required_age", "steam_appid",
            "supported_languages", "type", "website", "support_info"
        ]
        cleaned_data = {k: details[k] for k in keys_to_keep if k in details}

        # Clean and format specific fields
        if "categories" in cleaned_data:
            cleaned_data["categories"] = [remove_html_tags(x["description"]) for x in cleaned_data["categories"]]
        if "genres" in cleaned_data:
            cleaned_data["genres"] = [remove_html_tags(x["description"]) for x in cleaned_data["genres"]]
        if "metacritic" in cleaned_data:
            cleaned_data["metacritic"] = cleaned_data["metacritic"]["score"]
        else:
            cleaned_data["metacritic"] = "No Metacritic score available"
        if "price_overview" in cleaned_data:
            price_data = cleaned_data["price_overview"]
            base_price = price_data["final"] / 100  # Final price after discounts
            cleaned_data["price_final"] = base_price
            cleaned_data["price_with_tax"] = calculate_tax(base_price, tax_rate)
            cleaned_data["price_currency"] = price_data["currency"]
            del cleaned_data["price_overview"]
        if "support_info" in cleaned_data:
            for k, v in cleaned_data["support_info"].items():
                cleaned_data[f"support_{k}"] = remove_html_tags(v)
            del cleaned_data["support_info"]
        if "release_date" in cleaned_data and isinstance(cleaned_data["release_date"], dict):
            release_date_info = cleaned_data["release_date"]
            cleaned_data["coming_soon"] = release_date_info.get("coming_soon", False)
            cleaned_data["release_date"] = remove_html_tags(release_date_info.get("date", ""))
        if "platforms" in cleaned_data:
            cleaned_data["platforms"] = [k for k, v in cleaned_data["platforms"].items() if v]
        if "supported_languages" in cleaned_data:
            cleaned_data["supported_languages"] = remove_html_tags(cleaned_data["supported_languages"])

        # Ensure the price is in CAD, if it's in another currency, apply conversion
        if cleaned_data["price_currency"] != target_currency:
            if cleaned_data["price_currency"] == "USD":
                cleaned_data["price_final"] = round(cleaned_data["price_final"] * 1.36, 2)  # Convert USD to CAD (approx rate)
                cleaned_data["price_with_tax"] = round(cleaned_data["price_with_tax"] * 1.36, 2)
                cleaned_data["price_currency"] = target_currency

        return cleaned_data

    except requests.exceptions.RequestException as e:
        return f"Error: Request failed with exception {str(e)}"
    except KeyError as e:
        return f"Error: Unexpected response structure. Missing key {str(e)}"
    except Exception as e:
        return f"Error: An unexpected error occurred: {str(e)}"

# Test with Slay the Spire app ID 646570
if __name__ == "__main__":
    appid = input("Enter Steam App Id: ") #app id input
    tax_rate = 13  # Example tax rate in percentage
    result = fetch_and_clean_steam_app_details(appid, target_currency="CAD", tax_rate=tax_rate)
    
    if isinstance(result, dict):
        print("Cleaned App Details:")
        for key, value in result.items():
            print(f"{key}: {value}")
    else:
        print(result)
