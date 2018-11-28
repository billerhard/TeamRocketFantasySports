# some code was taken from andr3w321's espn_scraper @ https://github.com/andr3w321/espn_scraper

import json
import pytz
from dateutil import parser
from dateutil.relativedelta import relativedelta
import datetime
import os.path
import requests
from bs4 import BeautifulSoup
BASE_URL = "http://www.espn.com"

def retry_request(url, headers={}):
    """Get a url and return the request, try it up to 3 times if it fails initially"""
    session = requests.Session()
    session.mount("http://", requests.adapters.HTTPAdapter(max_retries=3))
    res = session.get(url=url, allow_redirects=False, headers=headers)
    session.close()
    return res

def get_soup(res):
    return BeautifulSoup(res.text, "lxml")

def get_new_json(url, headers={}):
    print(url)
    res = retry_request(url, headers)
    if res.status_code == 200:
        return res.json()
    else:
        print("ERROR:", res.status_code)
        return {"error_code": res.status_code, "error_msg": "URL Error"}

def get_new_html_soup(url, headers={}):
    print(url)
    res = retry_request(url, headers)
    if res.status_code == 200:
        return get_soup(res)
    else:
        print("ERROR: ESPN", res.status_code)
        return {"error_code": res.status_code, "error_msg": "ESPN Error"}

def get_week_leagues():
    return ["nfl"]

def get_sport(league):
    if league in ["nfl"]:
        return "football"