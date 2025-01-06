import os
import requests
from steam_web_api import Steam

#NOTE Most inputs will be click based

app_id = input()

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
    prompt = input("Would you like to award this game a point for this catagorey")
    if prompt == "yes" or prompt == "Yes":
        points += 1
    elif prompt == "no" or prompt == "No":
        points = 0
print (points)



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
print(reviews_response)