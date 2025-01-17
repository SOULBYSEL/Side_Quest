import requests
import re
from bs4 import BeautifulSoup

def fetch_game_data(app_id):
    points = 0
    result_text = ""

    # Average player counter over 30 days
    url = f"https://steamcharts.com/app/{app_id}#7d"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        average_players_div = soup.find('div', class_='app-stat')
        if average_players_div:
            average_players = average_players_div.find('span', class_='num').text
            if int(average_players.replace(",", "")) >= 10000:
                points += 1
            result_text += f"Average Players (Last 30 Days): {average_players}\n"
        else:
            result_text += "Could not find the average players data.\n"
    else:
        result_text += f"Failed to fetch the page. Status code: {response.status_code}\n"

    # User reviews
    def get_user_reviews(review_appid, params):
        user_review_url = f'https://store.steampowered.com/appreviews/{review_appid}'
        req_user_review = requests.get(user_review_url, params=params)
        if req_user_review.status_code != 200:
            return {"success": 2}
        try:
            user_reviews = req_user_review.json()
        except:
            return {"success": 2}
        return user_reviews

    params = {
        'json': 1,
        'language': 'english',
        'cursor': '*',
        'num_per_page': 100,
        'filter': 'recent'
    }
    reviews_response = get_user_reviews(app_id, params)
    if reviews_response["success"] == 1:
        positive = reviews_response['query_summary']['total_positive']
        negative = reviews_response['query_summary']['total_negative']
        total_review = positive + negative
        percent = (positive / total_review) * 100
        result_text += f"Reviews gathered: {total_review}\n"
        result_text += f"Positive review percent is: {percent:.2f}%\n"
        if percent >= 95:
            points += 1
            result_text += "Overwhelmingly Positive\n"
        elif percent >= 85:
            points += 1
            result_text += "Very Positive\n"
        elif percent >= 80:
            points += 1
            result_text += "Positive\n"
        elif percent >= 70:
            result_text += "Mostly Positive\n"
        elif percent >= 40:
            result_text += "Mixed\n"
        elif percent >= 20:
            result_text += "Mostly Negative\n"
        elif percent >= 15:
            result_text += "Negative\n"
        elif percent >= 10:
            result_text += "Very Negative\n"
        else:
            result_text += "Overwhelmingly Negative\n"
    else:
        result_text += "Failed to fetch user reviews.\n"

    # Critic scoring
    def remove_html_tags(text):
        return re.sub(r'<[^>]*>', '', text)

    def calculate_tax(price, tax_rate):
        return round(price * (1 + tax_rate / 100), 2)

    def fetch_and_clean_steam_app_details(appid, country_code="CA", target_currency="CAD", tax_rate=13):
        try:
            details_endpoint = f"https://store.steampowered.com/api/appdetails?appids={appid}&json=1&cc={country_code}"
            response = requests.get(details_endpoint)
            if response.status_code != 200:
                return f"Error: Failed to fetch data. HTTP Status Code: {response.status_code}"
            details = response.json()
            if str(appid) not in details or not details[str(appid)]["success"]:
                return f"Error: No data found for app ID {appid}."
            details = details[str(appid)]["data"]
            if "metacritic" in details:
                return details["metacritic"]["score"]
            else:
                return "No Metacritic score available"
        except requests.exceptions.RequestException as e:
            return f"Error: Request failed with exception {str(e)}"
        except KeyError as e:
            return f"Error: Unexpected response structure. Missing key {str(e)}"
        except Exception as e:
            return f"Error: An unexpected error occurred: {str(e)}"

    critic_score = fetch_and_clean_steam_app_details(app_id)
    result_text += f"Critic Score: {critic_score}\n"
    if isinstance(critic_score, int) and critic_score >= 65:
        points += 1
    elif isinstance(critic_score, int) and critic_score >= 30:
        result_text += "Critic score is between 30 and 65.\n"
    else:
        result_text += "Score too low, no points have been awarded.\n"

    result_text += f"Total Points: {points}\n"
    
    # Replace underscores with spaces
    result_text = result_text.replace("_", " ")
    
    return result_text
