import os
import requests
from steam_web_api import Steam

#app information, will be click based after UI

app_id = input()

KEY = os.environ.get("6E921FFF29FC14995F1AA43BE67F3D16")
steam = Steam(KEY)

# arguments: app_id
user = steam.apps.get_app_details(app_id)
print(user)