import requests
import os
import json
import re
from bs4 import BeautifulSoup
from steam_web_api import Steam
from requests_html import HTMLSession

#NOTE Most inputs will be click based

app_id = input("Please enter the Steam App ID ")

#Game Rater
#points system
points = 0

#Average player counter over 30 days

url = (f"https://steamcharts.com/app/{app_id}#7d") #Steam chart
response = requests.get(url)

if response.status_code == 200:
    print("Successfully fetched the page!")
else:
    print(f"Failed to fetch the page. Status code: {response.status_code}")

from bs4 import BeautifulSoup

soup = BeautifulSoup(response.content, "html.parser")

# Example: Extracting the average players over the last 30 days
# Note: The actual class or ID should be determined by inspecting the page's HTML structure
average_players_div = soup.find('div', class_='app-stat')

if average_players_div:
    average_players = average_players_div.find('span', class_='num').text
    print(f"Average Players (Last 30 Days): {average_players}")
else:
    print("Could not find the average players data.")

if average_players >= "10000":
    prompt = input("Would you like to award this game a point for this catagorey ")
    if prompt == "yes" or prompt == "Yes":
        points += 1
        print (points)
    else:
        print(points)


def get_user_reviews(review_appid, params):

    user_review_url = f'https://store.steampowered.com/appreviews/{review_appid}'
    req_user_review = requests.get(
        user_review_url,
        params=params
    )

    if req_user_review.status_code != 200:
        print(f'Fail to get response. Status code: {req_user_review.status_code}')
        return {"success": 2}
    
    try:
        user_reviews = req_user_review.json()
    except:
        return {"success": 2}

    return user_reviews

review_appid = app_id
params = {
        'json':1,
        'language': 'english',
        'cursor': '*',                                  # set the cursor to retrieve reviews from a specific "page"
        'num_per_page': 100,
        'filter': 'recent'
    }

reviews_response = get_user_reviews(review_appid, params)

positive = reviews_response['query_summary']['total_positive']
negative = reviews_response['query_summary']['total_negative']

total_review = positive + negative
print("Reviews gathered " + str(total_review))
percent = (positive / total_review) * 100
print("Positive review percent is " + str(percent))

#ranking for reviews
if percent >= 95:
    print("Overwhelmingly Positive")
    points += 1
    print(points)
elif percent < 95 and percent >= 85:
    print("Very Positive")
    print(points)
    points += 1
elif percent < 85 and percent >= 80:
    print("Positive")
    points += 1
    print(points)
elif percent < 80 and percent >= 70:
    print("Mostly Positive")
    prompt = input("Would you like to award this game a point for this catagorey ")
    if prompt == "yes" or prompt == "Yes":
        points += 1
        print (points)
    else:
        print(points)
elif percent < 70 and percent >= 40:
    print("Mixed")
    prompt = input("Would you like to award this game a point for this catagorey ")
    if prompt == "yes" or prompt == "Yes":
        points += 1
        print (points)
    else:
        print(points)
elif percent < 40 and percent >= 20:
    print("Mostly Negative")
    print("Score too low, no points have been awarded")
    print(points)
elif percent < 20 and percent >= 15:
    print("Negative")
    print("Score too low, no points have been awarded")
    print(points)
elif percent < 15 and percent >= 10:
    print("Very Negative")
    print("Score too low, no points have been awarded")
    print(points)
elif percent < 10 and percent >= 0:
    print("Overwhelmingly Negative")
    print("Score too low, no points have been awarded")
    print(points)
else:
    print("No reviews have been found")


#Critic scoring
def remove_html_tags(text):
    """
    Removes HTML tags from a given string.
    
    Args:
        text (str): The text from which HTML tags will be removed.
    
    Returns:
        str: The cleaned text without HTML tags.
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
    appid = app_id #app id input
    tax_rate = 13  # Example tax rate in percentage
    result = fetch_and_clean_steam_app_details(appid, target_currency="CAD", tax_rate=tax_rate)
    
print("Critic Score is " + str(result["metacritic"]))
if result["metacritic"] >= 65:
    points += 1
    print(points)
elif result["metacritic"] >= 30 and result["metacritic"] < 65:
    prompt = input("Would you like to award this game a point for this catagorey ")
    if prompt == "yes" or prompt == "Yes":
        points += 1
        print (points)
    else:
        print(points)
else:
    print("Score too low, no points have been awarded")
    print(points)