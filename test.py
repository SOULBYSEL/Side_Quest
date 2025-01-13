import requests
import os
import json
import re
from bs4 import BeautifulSoup
from steam_web_api import Steam
from requests_html import HTMLSession
from PIL import Image

im = Image.open (r"C:\Users\slend\Downloads\logo.png")

im.show()