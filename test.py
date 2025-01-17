import pygame
import requests
import re
from bs4 import BeautifulSoup

# Initialize pygame
pygame.init()

# Screen dimensions
screen_width = 600
screen_height = 500
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Steam Game Rater")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)

# Font
font = pygame.font.SysFont(None, 30)

# Points system
points = 0
average_players = 0
positive_review_percent = 0
critic_score = 0

# Function to display text
def display_text(text, x, y, color=BLACK):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

# Function to display progress bars
def display_progress_bar(x, y, width, height, progress, label, color=GREEN):
    pygame.draw.rect(screen, LIGHT_BLUE, (x, y, width, height))  # Background
    pygame.draw.rect(screen, color, (x, y, width * (progress / 100), height))  # Progress bar
    display_text(f"{label}: {progress}%", x + width + 10, y)

# Function to get average players over the last 30 days
def fetch_average_players(app_id):
    url = f"https://steamcharts.com/app/{app_id}#7d"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        average_players_div = soup.find('div', class_='app-stat')
        if average_players_div:
            return average_players_div.find('span', class_='num').text
    return "N/A"

# Function to get user reviews and calculate positive percentage
def fetch_user_reviews(app_id):
    review_url = f'https://store.steampowered.com/appreviews/{app_id}?json=1&language=english&num_per_page=100&filter=recent'
    response = requests.get(review_url)

    if response.status_code == 200:
        data = response.json()
        positive = data['query_summary']['total_positive']
        negative = data['query_summary']['total_negative']
        total_reviews = positive + negative
        if total_reviews > 0:
            percent = (positive / total_reviews) * 100
            return percent
    return 0

# Function to get critic score
def fetch_critic_score(app_id):
    details_endpoint = f"https://store.steampowered.com/api/appdetails?appids={app_id}&json=1"
    response = requests.get(details_endpoint)

    if response.status_code == 200:
        data = response.json()
        if str(app_id) in data and data[str(app_id)]["success"]:
            return data[str(app_id)]["data"].get("metacritic", {}).get("score", 0)
    return 0

# Main game loop
running = True
app_id_input = ""  # Store the inputted App ID
input_active = True

while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if input_active:
                if event.key == pygame.K_RETURN:  # Press Enter to submit the input
                    if app_id_input:
                        # Fetch data based on App ID
                        average_players = fetch_average_players(app_id_input)
                        positive_review_percent = fetch_user_reviews(app_id_input)
                        critic_score = fetch_critic_score(app_id_input)

                        # Award points based on data
                        points = 0
                        if average_players >= "10000":
                            points += 1
                        if positive_review_percent >= 95:
                            points += 1
                        if critic_score >= 65:
                            points += 1
                elif event.key == pygame.K_BACKSPACE:  # Handle backspace
                    app_id_input = app_id_input[:-1]
                else:
                    app_id_input += event.unicode  # Append the typed character

    # Display input field
    display_text("Enter Steam App ID:", 50, 50)
    pygame.draw.rect(screen, BLUE, (50, 90, 200, 30))
    display_text(app_id_input, 60, 95, BLACK)

    # Display results
    display_text(f"Average Players (Last 30 Days): {average_players}", 50, 170)
    display_progress_bar(50, 210, 500, 20, float(average_players)/100000 * 100, "Average Players")

    display_text(f"Positive Review Percentage: {positive_review_percent}%", 50, 250)
    display_progress_bar(50, 290, 500, 20, positive_review_percent, "Review Score")

    display_text(f"Critic Score: {critic_score}", 50, 330)
    display_progress_bar(50, 370, 500, 20, critic_score, "Critic Score")

    display_text(f"Total Points: {points}", 50, 420)

    pygame.display.flip()

pygame.quit()
