# some code was taken from andr3w321's espn_scraper @ https://github.com/andr3w321/espn_scraper

import json
import pytz
from dateutil import parser
from dateutil.relativedelta import relativedelta
import datetime
import os.path
import requests
import json
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
def get_leagues():
    """ Return a list of supported leagues """
    return get_week_leagues()

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
def get_league_from_url(url):
    return url.split('.com/')[1].split('/')[0]
def get_date_from_scoreboard_url(url):
    league = get_league_from_url(url)
    if "nfl":
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


def get_league_from_url(url):
    return url.split('.com/')[1].split('/')[0]

def get_date_from_scoreboard_url(url):
    league = get_league_from_url(url)
    if league == "nhl":
        return url.split("?date=")[1].split("&")[0]
    else:
        return url.split('/')[-1].split('?')[0]
def get_data_type_from_url(url):
    """ Guess and return the data_type based on the url """
    data_type = None
    valid_data_types = ["scoreboard", "summary", "recap", "boxscore", "playbyplay", "conversation", "gamecast"]
    for valid_data_type in valid_data_types:
        if valid_data_type in url:
            data_type = valid_data_type
            break
    if data_type == None:
        raise ValueError("Unknown data_type for url. Url must contain one of {}".format(valid_data_types))
    return data_type

def get_filename_ext(filename):
    if filename.endswith(".json"):
        return "json"
    elif filename.endswith(".html"):
        return "html"
    else:
        raise ValueError("Uknown filename extension for {}".format(filename))

def get_teams(league):
        """ Returns a list of teams with ids and names """
        url = BASE_URL + "/" + league + "/teams"
        print(url)
        soup = get_soup(retry_request(url))
        if league == "wnba":
            selector = "b a"
        else:
            selector = "a.bi"
        team_links = soup.select(selector)
        teams = []
        for team_link in team_links:
            teams.append({'id': team_link['href'].split('/')[-2], 'name': team_link.text})
        return teams
def get_standings(league, season_year, college_division=None):
    standings = {"conferences": {}}
    if league in ["nhl"]:
        url = "{}/{}/standings/_/year/{}".format(BASE_URL, league, season_year)
        print(url)
        soup = get_soup(retry_request(url))
        standings = {"conferences": {}}
        # espn has malformed html where they forgot to include closing </table> tags so have to parse by table rows instead of by tables
        trs = soup.find_all("tr", class_=["stathead","colhead","oddrow","evenrow"])
        for tr in trs:
            if "stathead" in tr["class"]:
                conference_name = tr.text
                standings["conferences"][conference_name] = {"divisions": {}}
            elif "colhead" in tr["class"]:
                division = tr.find("td").text
                standings["conferences"][conference_name]["divisions"][division] = {"teams": []}
            elif "oddrow" in tr["class"] or "evenrow" in tr["class"]:
                team = {}
                team_a_tag = tr.find("td").find("a")
                if team_a_tag is None:
                    # some teams are now defunct with no espn links
                    team["name"] = tr.find("td").text.split(" - ")[1].strip()
                    team["abbr"] = ""
                else:
                    team["name"] = team_a_tag.text
                    team["abbr"] = team_a_tag["href"].split("name/")[1].split("/")[0].upper()
                standings["conferences"][conference_name]["divisions"][division]["teams"].append(team)
    elif league in ["ncb","ncw"]:
        url = "{}/{}/standings/_/year/{}".format(BASE_URL, league, season_year)
        print(url)
        soup = get_soup(retry_request(url))
        standings = {"conferences": {}}
        conference_name = "i"
        standings["conferences"][conference_name] = {"divisions": {}}
        divs = soup.find_all("div", class_="mod-table")
        for div in divs:
            division = div.find("div", class_="mod-header").find("h4").text.split("Standings")[0]
            standings["conferences"][conference_name]["divisions"][division] = {"teams": []}
            trs = div.find("div", class_="mod-content").find("table", class_="tablehead").find_all("tr", class_=["oddrow","evenrow"])
            for tr in trs:
                for c in tr["class"]:
                    if "team" in c:
                        team_a_tag = tr.find("td").find("a")
                        team = {}
                        team["name"] = team_a_tag.text
                        team["id"] = int(c.split("-")[2])
                        standings["conferences"][conference_name]["divisions"][division]["teams"].append(team)
    elif league in ["nfl","ncf","nba","mlb","wnba"]:
        if college_division:
            valid_college_divisions = ["fbs", "fcs", "d2", "d3"]
            if college_division in valid_college_divisions:
                url = "{}/{}/standings/_/view/{}/season/{}/group/division".format(BASE_URL, league, college_division, season_year)
            else:
                raise ValueError("College division must be none or {}".format(",".join(valid_college_divisions)))
        elif league in ["wnba"]:
            url = "{}/{}/standings/_/season/{}/group/conference".format(BASE_URL, league, season_year)
        else:
            url = "{}/{}/standings/_/season/{}/group/division".format(BASE_URL, league, season_year)
        print(url)
        soup = get_soup(retry_request(url))
        conference_names = [x.text for x in soup.find_all("span", class_="long-caption")]
        tables = soup.find_all("table", class_="standings")
        for i in range(0, len(tables)):
            standings["conferences"][conference_names[i]] = {"divisions": {}}
            theads = tables[i].find_all("thead", class_="standings-categories")
            for thead in theads:
                division = thead.find("th").text
                standings["conferences"][conference_names[i]]["divisions"][division] = {"teams": []}
                nextSib = thead.nextSibling
                while(nextSib and nextSib.name == "tr"):
                    link = nextSib.find("abbr")
                    team = {}
                    team["name"] = link["title"]
                    team["abbr"] = link.text
                    standings["conferences"][conference_names[i]]["divisions"][division]["teams"].append(team)
                    nextSib = nextSib.nextSibling
print(get_week_scoreboard_url("nfl","2018", input(),"group=None"))



