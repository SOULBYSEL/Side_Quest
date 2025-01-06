import os
import requests
from steam_web_api import Steam

#seach engine

search = input()

KEY = os.environ.get("6E921FFF29FC14995F1AA43BE67F3D16")


steam = Steam(KEY)

# arguments: search
user = steam.apps.search_games(search)
print(user)