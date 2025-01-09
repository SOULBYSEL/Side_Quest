import requests
import os
from bs4 import BeautifulSoup
from steam_web_api import Steam
import json
from requests_html import HTMLSession

session = HTMLSession()
r = session.get("https://store.steampowered.com/app/945710/DreadOut_2/?curator_clanid=25278687&curator_listid=37980")
application_config = r.html.find('#application_config', first=True)
data = json.loads(application_config.attrs["data-curatorlistdata"])

data[0]["multi_detail_lists"][0]["apps"]["recommended_app"]
data = [x for l in data for x in l["multi_detail_lists"]]
data = [x for l in data for x in l["apps"]]
data = sorted(data, key=lambda x: x["sort_order"])
data = [x["recommended_app"] for x in data]
data = [x["appid"] for x in data]

print(data)