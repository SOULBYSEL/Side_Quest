import pygame
import os
import sys
import requests
from steam_web_api import Steam
from Appinfo import fetch_and_clean_steam_app_details  # Import Appinfo.py functions
import json  # Ensure json is imported
from rate_game import fetch_game_data  # Import the new function

# Initialize Pygame
pygame.init()

# Setup the environment
os.environ['SDL_VIDEO_CENTERED'] = '1'
info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h
screen = pygame.display.set_mode((screen_width - 10, screen_height - 50), pygame.RESIZABLE)
pygame.display.set_caption('Side Quest')

# Load images and colors
background = pygame.image.load(r"C:\\Users\\slend\\Downloads\\background.jpg").convert()
start_img = pygame.image.load(r"C:\\Users\\slend\\Downloads\\Start.png").convert_alpha()
quit_img = pygame.image.load(r"C:\\Users\\slend\\Downloads\\Exit.png").convert_alpha()
logo = pygame.image.load(r"C:\\Users\\slend\\Downloads\\logo.png").convert_alpha()
l_width = logo.get_rect().width
l_height = logo.get_rect().height
logo = pygame.transform.scale(logo, (int(l_width * 0.25), int(l_height * 0.25)))

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)  # Highlight color

# Button class
class Button():
    def __init__(self, x, y, image=None, scale=1.0, width=0, height=0, text=""):
        if image:
            b_width = image.get_width()
            b_height = image.get_height()
            self.image = pygame.transform.scale(image, (int(b_width * scale), int(b_height * 0.5)))
            self.rect = self.image.get_rect()
        else:
            self.image = None
            self.rect = pygame.Rect(x, y, width, height)
        self.rect.topleft = (x, y)
        self.clicked = False
        self.text = text
        self.font = pygame.font.Font(None, 32)

    def draw(self):
        if self.image:
            screen.blit(self.image, (self.rect.x, self.rect.y))
        else:
            pygame.draw.rect(screen, WHITE, self.rect, 2)
            text_surface = self.font.render(self.text, True, WHITE)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

# Text input box class
class InputBox():
    def __init__(self, x, y, w, h, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = WHITE
        self.text = ''
        self.font = font
        self.txt_surface = font.render(self.text, True, WHITE)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.txt_surface = self.font.render(self.text, True, WHITE)

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

# Set up Steam API
KEY = "6E921FFF29FC14995F1AA43BE67F3D16"  # Replace with your API key
steam = Steam(KEY)

# Additional state variables
viewing_details = False
app_details = None  # Store fetched app details
rating_result = ""  # Store the rating result text

# Create buttons and input box
start_button = Button(550, 690, start_img, 0.3)  # Adjusted position
quit_button = Button(850, 700, quit_img, 0.5)   # Adjusted position
main_menu_button = Button((screen_width - 200) // 2, screen_height - 150, width=200, height=50, text="Main Menu")
return_to_search_button = Button(screen_width - 210, 10, width=200, height=50, text="Return to Search")
font = pygame.font.Font(None, 32)
input_box = InputBox((screen_width - 400) // 2, ((screen_height - 40) // 2) - 200, 400, 40, font)

# Add Rate Game button
rate_game_button = Button(screen_width - 210, 90, width=200, height=50, text="Rate Game")

running = True
search_mode = False  # Initially set to False
search_results = []
highlight_index = -1  # Index of the currently highlighted result
show_return_to_search = False  # State for the Return to Search button

# Fetch Steam app details with fallback
cached_app_details = {}
def get_app_details(appid):
    if appid in cached_app_details:
        return cached_app_details[appid]
    details = fetch_and_clean_steam_app_details(appid)
    cached_app_details[appid] = details
    return details

def wrap_text(text, font, max_width):
    """Wrap text to fit within a specified width."""
    words = text.split(' ')
    lines = []
    current_line = []
    current_width = 0

    for word in words:
        word_width, _ = font.size(word + ' ')
        if current_width + word_width <= max_width:
            current_line.append(word)
            current_width += word_width
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width

    if current_line:
        lines.append(' '.join(current_line))

    return lines

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if search_mode:
            # Handle input box events
            input_box.handle_event(event)
            if event.type == pygame.KEYDOWN and input_box.active:
                search_query = input_box.text.strip()
                if search_query:
                    print(f"Searching for games with query: {search_query}")  # Debug log
                    try:
                        response = steam.apps.search_games(search_query)
                        search_results = response.get('apps', [])  # Extract search results
                    except Exception as e:
                        print(f"Error searching games: {e}")  # Error log
                        search_results = []
                    highlight_index = -1

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if main menu button is clicked
                if main_menu_button.rect.collidepoint(event.pos):
                    print("Returning to main menu from search.")  # Debug log
                    search_mode = False  # Reset to main menu state
                    search_results = []  # Clear search results
                    input_box.text = ""  # Reset input box text
                    show_return_to_search = False

                # Check if any search result was clicked
                y_offset = input_box.rect.y + input_box.rect.height + 20
                for index, result in enumerate(search_results[:10]):
                    result_rect = pygame.Rect(
                        (screen_width // 2) - 200, y_offset - 15, 400, 30
                    )
                    if result_rect.collidepoint(event.pos):
                        appid = result.get('id', None)
                        if isinstance(appid, list):
                            appid = appid[0]  # Updated handling for appid list

                        print(f"Clicked result: {result}")  # Debug log
                        if appid:
                            print(f"Fetching details for appid: {appid}")  # Debug log
                            app_details = get_app_details(appid)
                            print(f"Fetched App Details: {app_details}")  # Debug log
                            viewing_details = True
                            search_mode = False
                            show_return_to_search = True
                        else:
                            print("Error: appid is None.")  # Debug log
                        break
                    y_offset += 30

            if event.type == pygame.MOUSEMOTION:
                # Highlight the result under the cursor
                y_offset = input_box.rect.y + input_box.rect.height + 20
                highlight_index = -1
                for index, result in enumerate(search_results[:10]):
                    result_rect = pygame.Rect(
                        (screen_width // 2) - 200, y_offset - 15, 400, 30
                    )
                    if result_rect.collidepoint(event.pos):
                        highlight_index = index
                        break
                    y_offset += 30

        elif viewing_details:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if main_menu_button.rect.collidepoint(event.pos):
                    print("Returning to main menu from app details.")  # Debug log
                    viewing_details = False
                    app_details = None
                    show_return_to_search = False
                elif return_to_search_button.rect.collidepoint(event.pos):
                    print("Returning to search from app details.")  # Debug log
                    search_mode = True
                    viewing_details = False
                elif rate_game_button.rect.collidepoint(event.pos):
                    print("Opening rate game interface.")  # Debug log
                    # Add rating logic
                    if app_details:
                        appid = app_details.get('steam_appid', None)
                        if appid:
                            rating_result = fetch_game_data(appid)

        else:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if start_button.rect.collidepoint(mouse_pos):
                    print("Starting search mode.")  # Debug log
                    search_mode = True
                elif quit_button.rect.collidepoint(mouse_pos):
                    print("Exiting application.")  # Debug log
                    sys.exit()

    # Draw background
    screen.blit(background, (0, 0))

    if search_mode:
        # Draw instruction text
        instruction_text = font.render("Please enter the name of the Game you wish to rate!", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(screen_width // 2, input_box.rect.y - 40))
        screen.blit(instruction_text, instruction_rect)

        # Draw input box and search results
        input_box.draw()
        y_offset = input_box.rect.y + input_box.rect.height + 20
        for index, result in enumerate(search_results[:10]):  # Limit to 10 results
            game_name = result.get('name', 'Unknown Game')
            color = RED if index == highlight_index else WHITE
            text_surface = font.render(game_name, True, color)
            text_rect = text_surface.get_rect(center=(screen_width // 2, y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += 30

        # Draw main menu button
        main_menu_button.draw()

    elif viewing_details:
        if isinstance(app_details, dict):
            y_offset = 100
            max_lines = (screen_height - 150) // 30  # Number of lines that fit on the screen
            line_count = 0  # Track displayed lines

            for key, value in app_details.items():
                if isinstance(value, list):
                    value = ", ".join(map(str, value[:5])) + ("..." if len(value) > 5 else "")
                elif isinstance(value, dict):
                    value = json.dumps(value, indent=2)

                wrapped_lines = wrap_text(f"{key}: {value}", font, screen_width - 100)
                for line in wrapped_lines:
                    text_surface = font.render(line, True, WHITE)
                    screen.blit(text_surface, (50, y_offset))
                    y_offset += 30
                    line_count += 1

                    if line_count >= max_lines:
                        break

                if line_count >= max_lines:
                    break

        else:
            error_text = font.render("Error: Unable to fetch details.", True, WHITE)
            screen.blit(error_text, (50, 100))

        # Draw main menu button
        main_menu_button.draw()
        if show_return_to_search:
            return_to_search_button.draw()
        # Draw Rate Game button
        rate_game_button.draw()

        # Draw rating result
        if rating_result:
            y_offset += 30
            for line in wrap_text(rating_result, font, screen_width - 100):
                text_surface = font.render(line, True, WHITE)
                screen.blit(text_surface, (50, y_offset))
                y_offset += 30

    else:
        screen.blit(logo, (screen_width // 2 - logo.get_width() // 2, 100))
        start_button.draw()
        quit_button.draw()

    pygame.display.flip()

pygame.quit()
