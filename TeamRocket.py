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
def get_calendar(league, date_or_season_year):
    """ Return a calendar for a league and season_year"""
    if league in get_week_leagues():
        url = get_week_scoreboard_url(league, date_or_season_year, 2, 1)
    # TODO use cached replies for older urls
    return get_url(url)['content']['calendar']
def get_all_scoreboard_urls(league, season_year):
    """ Return a list of all scoreboard urls for a given league and season year """
    urls = []

    if league in get_week_leagues():
        calendar = get_calendar(league, season_year)
        for season_type in calendar:
            if 'entries' in season_type:
                for entry in season_type['entries']:
                    if league == "ncf":
                        for group in get_ncf_groups():
                            urls.append(get_week_scoreboard_url(league, season_year, season_type['value'], entry['value'], group))
                    else:
                        urls.append(get_week_scoreboard_url(league, season_year, season_type['value'], entry['value']))
        return urls
    else:
        raise ValueError("Unknown league for get_all_scoreboard_urls")
def get_league_from_url(url):
    return url.split('.com/')[1].split('/')[0]
def get_date_from_scoreboard_url(url):
    league = get_league_from_url(url)
    if league == "nhl":
        return url.split("?date=")[1].split("&")[0]
    else:
        return url.split('/')[-1].split('?')[0]

def get_sportscenter_api_url(sport, league, dates):
    return "http://sportscenter.api.espn.com/apis/v1/events?sport={}&league={}&dates={}".format(sport, league, dates)
def get_week_scoreboard_url(league, season_year, season_type, week, group=None):
    """ Return a scoreboard url for a league that uses weeks (football)"""
    if league in get_week_leagues():
        if group == None:
            return "{}/{}/scoreboard/_/year/{}/seasontype/{}/week/{}?xhr=1".format(BASE_URL, league, season_year, season_type, week)
        else:
            return "{}/{}/scoreboard/_/group/{}/year/{}/seasontype/{}/week/{}?xhr=1".format(BASE_URL, league, group, season_year, season_type, week)
    else:
        raise ValueError("League must be {} to get week scoreboard url".format(get_week_leagues()))
print(get_week_scoreboard_url("nfl","2018", "13","group=None"))



