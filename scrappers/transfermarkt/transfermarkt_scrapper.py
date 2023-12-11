# This is a sample Python script.
import requests
from bs4 import BeautifulSoup
import json
import csv
from unidecode import unidecode
import traceback
import pandas as pd
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

headers = {
  'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
}

seasons_dictionary = {
    "2011": "2011/2012",
    "2012": "2012/2013",
    "2013": "2013/2014",
    "2014": "2014/2015",
    "2015": "2015/2016",
    "2016": "2016/2017",
    "2017": "2017/2018",
    "2018": "2018/2019",
    "2019": "2019/2020",
    "2020": "2020/2021",
    "2021": "2021/2022",
    "2022": "2022/2023",
    "2023": "2023/2024"
}

months_dictionary = {
    " sty ": ".01.",
    " lut ": ".02.",
    " mar ": ".03.",
    " kwi ": ".04.",
    " maj ": ".05.",
    " cze ": ".06.",
    " lip ": ".07.",
    " sie ": ".08.",
    " wrz ": ".09.",
    " paz ": ".10.",
    " lis ": ".11.",
    " gru ": ".12."
}

def csv_error(func, year,url,error):
    selected_keys = ["func", "year", "url", "error"]
    with open('errors',"a", newline="") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=selected_keys)
        selected_data = {
                "func": func,
                "year": unidecode(year),
                "url": unidecode(url),
                "error": unidecode(error)
            }
        csv_writer.writerow(selected_data)
def scrape_player(uri,year):
    # Use a breakpoint in the code line below to debug your script.
    url = "https://www.transfermarkt.pl"+uri
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    id = url.split("spieler/")[1]
    slug = url.split("transfermarkt.pl/")[1].split("/profil/")[0]
    header = soup.find_all('ul', {'class': 'data-header__items'})
    birth = header[0].find_all('li', {'class': 'data-header__label'})
    date = ""
    place_of_birth = ""
    nationality = ""
    height = ""
    position = ""
    manager = ""
    table_information = soup.find("div", {"class": "info-table info-table--right-space"})
    if "Nazwisko w kraju pochodzenia:" in table_information.find("span", {"class": "info-table__content info-table__content--regular"}).get_text():
        name = table_information.find("span", {"class": "info-table__content info-table__content--bold"}).get_text()
    else:
        name = ""

    for data in birth:
        if data.find("span")["itemprop"] == "birthDate":
            brith_date = data.get_text().split("Urodz./Wiek:")[1].split("(")[0].lstrip().strip()
            for element in months_dictionary:
                if element in brith_date:
                    date = brith_date.replace(element, months_dictionary[element])
                    break
                else:
                    date = ""
                    continue
        elif data.find("span")["itemprop"] == "birthPlace":
            place_of_birth = data.get_text().split("Miejsce urodzenia:")[1].lstrip().strip()
        elif data.find("span")["itemprop"] == "nationality":
            nationality = data.get_text().split("Narodowość:")[1].lstrip().strip()
    pos_height = header[1].find_all('li', {'class': 'data-header__label'})
    for data in pos_height:
        if "Wzrost" in data.get_text():
            height = data.get_text().split("Wzrost:")[1].lstrip().strip()
        elif "Pozycja" in data.get_text():
            position = data.get_text().split("Pozycja:")[1].lstrip().strip()
        elif "Menadżer" in data.get_text():
            manager = data.get_text().split("Menadżer:")[1].lstrip().strip()
    if date !="":
        age = int(year) - int(date.split(".")[2])
        if age > 23:
            return False
    selected_keys = ['id', 'slug', 'name', 'place_of_birth', 'brith_date', 'nationality', 'height', 'position', 'manager']
    with open('players', "a", newline="") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=selected_keys)
        selected_data = {
            "id": id,
            "slug": unidecode(slug),
            "name": unidecode(name),
            "place_of_birth": unidecode(place_of_birth),
            "brith_date": unidecode(date),
            "nationality": unidecode(nationality),
            "height": unidecode(height),
            "position": unidecode(position),
            "manager": unidecode(manager)
        }
        csv_writer.writerow(selected_data)
    transfery(id)
    market_value_scrape(id)
    return position



def transfery(id):
    url = f"https://www.transfermarkt.pl/ceapi/transferHistory/list/{id}"
    response = requests.get(url, headers=headers)
    json_result = json.loads(response.content)
    selected_keys = ['id','season','date', 'marketValue', 'fee', 'clubName1', 'clubName2']
    with open('transfers',"a", newline="") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=selected_keys)
        for transfer in json_result.get('transfers', {}):
            selected_data = {
              "id": id,
              "season": unidecode(transfer.get("season", "")),
              "date": unidecode(transfer.get("date", "")),
              "marketValue": unidecode(transfer.get("marketValue", "")),
              "fee": unidecode(transfer.get("fee", {})),
              "clubName1": unidecode(transfer.get("from", {}).get("clubName", {})),
              "clubName2": unidecode(transfer.get("to", {}).get("clubName", {})),
            }
            csv_writer.writerow(selected_data)

def market_value_scrape(id):
    url = f"https://www.transfermarkt.pl/ceapi/marketValueDevelopment/graph/{id}"
    response = requests.get(url, headers=headers)
    json_result = json.loads(response.content)
    selected_keys = ['id','value','date', 'club', 'age']
    with open('player_value',"a", newline="") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=selected_keys)
        for element in json_result.get('list',{}):
            selected_data = {
                "id": id,
                "value": unidecode(element.get("mw", "")),
                "date": unidecode(element.get("datum_mw", "")),
                "club": unidecode(element.get("verein", "")),
                "age": unidecode(element.get("age", {})),
            }
            csv_writer.writerow(selected_data)

def club_scrape(url,year):
    url="https://www.transfermarkt.pl"+url #/centralna-liga-juniorow/startseite/wettbewerb/PLZJ/plus/?saison_id=2018"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    clubs_list = soup.find_all('td', {'class': 'zentriert no-border-rechts'})
    for club in clubs_list:
        club_href = club.find("a")['href']#.replace("saison_id/2018","saison_id/2016")
        club_players_scrape(club_href,year)
def club_players_scrape(uri,year):
    url = "https://www.transfermarkt.pl"+uri
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    players_list = soup.find_all('td', {'class': 'hauptlink'})
    for player in players_list:
        if "rechts" in player['class']:
            continue
        if player.find("a"):
            player_href = player.find("a")['href']
            if "spieler" in player_href:
                try:
                    position = scrape_player(player_href,year)

                    if position == False:
                        continue
                    if position != "Bramkarz":
                        try:
                            get_seasons(player_href,get_season)
                        except Exception as e:
                            csv_error("get_seasons/get_season", year, player_href,str(traceback.format_exc()))
                    else:
                        try:
                            get_seasons(player_href,get_season_goalkeeper)
                        except Exception as e:
                            csv_error("get_seasons/get_season_goalkeeper", year, player_href,str(traceback.format_exc()))
                except Exception as e:
                    csv_error("scrape_player", year, player_href, str(traceback.format_exc()))

def get_seasons(url, func):
    url = "https://www.transfermarkt.pl" + url.replace("/profil/", "/leistungsdaten/")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    seasons = soup.find("select", {"class": "chzn-select"})
    for season in seasons.find_all("option")[1:]:
        year= season["value"]
        func(url,year)

def get_season_goalkeeper(url, year):
    url = url + "/saison/" + year + "/plus/1"  # /filip-szymczak/leistungsdaten/spieler/554972/saison/2022/plus/1"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    leagues_divs = soup.find_all('div', {'class': 'table-header img-vat'})
    leagues = []
    for league in leagues_divs:
        if league.find('img') != None:
            leagues.append(league.find('img')['title'])
        else:
            leagues.append(league.find('a').get_text().lstrip().strip())
    tables = soup.find_all('tbody')[1:]
    id = url.split("spieler/")[1].split("/")[0]
    selected_keys_minutes = ["id", "season", "title", "matches", "goals", "own_goal", "from_bench",
                             "changes",
                             "yellow_card", "two_yellow_card ", "red_card", "lose_goals", "clean_sheet",
                             "minutes", ]
    selected_keys_seasons = ["id", "season", "league", "round", "date", "home_team", "away_team", "result", "position",
                             "goals", "assists", "own_goals", "yellow_card", "two_yellow_card", "red_card",
                             "from_bench",
                             "changes", "minutes", "out", "out_reason"]
    empty = soup.find("span", {"class": "empty"})
    if empty != None:
        add_idx = 1
    else:
        add_idx = 0
    for idx, table in enumerate(tables):
        trs = table.find_all("tr")
        for idx_tr, tr in enumerate(trs):
            tds = tr.find_all('td')
            if idx + add_idx == 0:
                with open('player_goalkeeper_club_minutes', "a", newline="") as csv_file:
                    csv_writer = csv.DictWriter(csv_file, fieldnames=selected_keys_minutes)

                    for idx_td, td in enumerate(tds[1:]):
                        if idx_td == 0:
                            title = td.get_text()
                        elif idx_td == 1:
                            matches = td.get_text()
                        elif idx_td == 2:
                            goals = td.get_text()
                        elif idx_td == 3:
                            own_goal = td.get_text()
                        elif idx_td == 4:
                            from_bench = td.get_text().replace("'", "")
                        elif idx_td == 5:
                            changes = td.get_text()
                        elif idx_td == 6:
                            yellow_card = td.get_text()
                        elif idx_td == 7:
                            two_yellow_card = td.get_text()
                        elif idx_td == 8:
                            red_card = td.get_text()
                        elif idx_td == 9:
                            lose_goals = td.get_text()
                        elif idx_td == 10:
                            clean_sheet = td.get_text().replace("'", "")
                        elif idx_td == 11:
                            minutes = td.get_text().replace("'", "")
                    selected_data = {
                        "id": id,
                        "season": seasons_dictionary[year],
                        "title": unidecode(title),
                        "matches": unidecode(matches),
                        "goals": unidecode(goals),
                        "own_goal": unidecode(own_goal),
                        "from_bench": unidecode(from_bench),
                        "changes": unidecode(changes),
                        "yellow_card": unidecode(yellow_card),
                        "two_yellow_card ": unidecode(two_yellow_card),
                        "red_card": unidecode(red_card),
                        "lose_goals": unidecode(lose_goals),
                        "clean_sheet": unidecode(clean_sheet),
                        "minutes": unidecode(minutes),
                    }
                    csv_writer.writerow(selected_data)
            else:
                with open('player_seasons', "a", newline="") as csv_file:
                    csv_writer = csv.DictWriter(csv_file, fieldnames=selected_keys_seasons)
                    new_tds = list(filter(check_if_image_in_tag, tds))
                    for idx_td, td in enumerate(new_tds):
                        if idx_td == 0:
                            round = td.get_text().lstrip().strip()
                        elif idx_td == 1:
                            for element in months_dictionary:
                                if element in td.get_text():
                                    date = td.get_text().replace(element, months_dictionary[element])
                                    break
                                else:
                                    date = ""
                                    continue
                        elif idx_td == 2:
                            if "(" in td.get_text():
                                home_team = td.get_text().split("(")[0].replace(u'\xa0', '')
                            else:
                                home_team = td.get_text()
                        elif idx_td == 3:
                            if "(" in td.get_text():
                                away_team = td.get_text().split("(")[0].replace(u'\xa0', '')
                            else:
                                away_team = td.get_text()
                        elif idx_td == 4:
                            result = td.get_text()
                        elif td.has_attr('colspan') == True and idx_td == 5:
                            position = goals = assists = own_goals = yellow_card = two_yellow_card = red_card = from_bench = changes = minutes = ""
                            out_reason = td.get_text()
                            out = True
                        elif idx_td == 5:
                            position = td.get_text()
                        elif idx_td == 6:
                            goals = td.get_text()
                        elif idx_td == 7:
                            assists = td.get_text()
                        elif idx_td == 8:
                            own_goals = td.get_text()
                        elif idx_td == 9:
                            yellow_card = td.get_text()
                        elif idx_td == 10:
                            two_yellow_card = td.get_text()
                        elif idx_td == 11:
                            red_card = td.get_text()
                        elif idx_td == 12:
                            from_bench = td.get_text().replace("'", "")
                        elif idx_td == 13:
                            changes = td.get_text()
                        elif idx_td == 14:
                            minutes = td.get_text().replace("'", "")
                            out_reason = ""
                            out = False
                    selected_data = {
                        "id": id,
                        "season": seasons_dictionary[year],
                        "league": unidecode(leagues[0]),
                        "round": unidecode(round),
                        "date": unidecode(date),
                        "home_team": unidecode(home_team),
                        "away_team": unidecode(away_team),
                        "result": unidecode(result),
                        "position": unidecode(position),
                        "goals": unidecode(goals),
                        "assists": unidecode(assists),
                        "own_goals": unidecode(own_goals),
                        "yellow_card": unidecode(yellow_card),
                        "two_yellow_card": unidecode(two_yellow_card),
                        "red_card": unidecode(red_card),
                        "from_bench": unidecode(from_bench),
                        "changes": unidecode(changes),
                        "minutes": unidecode(minutes),
                        "out": out,
                        "out_reason": unidecode(out_reason),
                    }
                    csv_writer.writerow(selected_data)
        if idx != 0:
            leagues.pop(0)
def get_season(url, year):
    url = url+"/saison/"+year+"/plus/1"#/filip-szymczak/leistungsdaten/spieler/554972/saison/2022/plus/1"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    leagues_divs = soup.find_all('div', {'class': 'table-header img-vat'})
    leagues = []
    for league in leagues_divs:
        if league.find('img') != None:
            leagues.append(league.find('img')['title'])
        else:
            leagues.append(league.find('a').get_text().lstrip().strip())
    tables = soup.find_all('tbody')[1:]
    id = url.split("spieler/")[1].split("/")[0]
    selected_keys_minutes = ["id", "season", "title", "matches", "goals", "assists", "own_goal", "from_bench", "changes",
                        "yellow_card", "two_yellow_card ", "red_card", "penalty_goal", "minutes_per_goal", "minutes",]
    selected_keys_seasons = ["id", "season", "league", "round", "date", "home_team", "away_team", "result", "position",
                             "goals", "assists", "own_goals", "yellow_card", "two_yellow_card", "red_card", "from_bench",
                        "changes", "minutes", "out", "out_reason"]
    empty = soup.find("span", {"class": "empty"})
    if empty != None:
        add_idx = 1
    else:
        add_idx = 0
    for idx, table in enumerate(tables):
        trs=table.find_all("tr")
        for idx_tr, tr in enumerate(trs):
            tds=tr.find_all('td')
            if idx + add_idx == 0:
                with open('player_club_minutes', "a", newline="") as csv_file:
                    csv_writer = csv.DictWriter(csv_file, fieldnames=selected_keys_minutes)

                    for idx_td, td in enumerate(tds[1:]):
                        if idx_td == 0:
                            title = td.get_text()
                        elif idx_td == 1:
                            matches = td.get_text()
                        elif idx_td == 2:
                            goals = td.get_text()
                        elif idx_td == 3:
                            assists = td.get_text()
                        elif idx_td == 4:
                            own_goal = td.get_text()
                        elif idx_td == 5:
                            from_bench = td.get_text().replace("'","")
                        elif idx_td == 6:
                            changes = td.get_text()
                        elif idx_td == 7:
                            yellow_card = td.get_text()
                        elif idx_td == 8:
                            two_yellow_card = td.get_text()
                        elif idx_td == 9:
                            red_card = td.get_text()
                        elif idx_td == 10:
                            penalty_goal = td.get_text()
                        elif idx_td == 11:
                            minutes_per_goal = td.get_text().replace("'","")
                        elif idx_td == 12:
                            minutes = td.get_text().replace("'","")
                    selected_data = {
                        "id": id,
                        "season": seasons_dictionary[year],
                        "title": unidecode(title),
                        "matches": unidecode(matches),
                        "goals": unidecode(goals),
                        "assists": unidecode(assists),
                        "own_goal": unidecode(own_goal),
                        "from_bench": unidecode(from_bench),
                        "changes": unidecode(changes),
                        "yellow_card": unidecode(yellow_card),
                        "two_yellow_card ": unidecode(two_yellow_card),
                        "red_card": unidecode(red_card),
                        "penalty_goal": unidecode(penalty_goal),
                        "minutes_per_goal": unidecode(minutes_per_goal),
                        "minutes": unidecode(minutes),
                    }
                    csv_writer.writerow(selected_data)
            else:
                with open('player_seasons', "a", newline="") as csv_file:
                    csv_writer = csv.DictWriter(csv_file, fieldnames=selected_keys_seasons)
                    new_tds = list(filter(check_if_image_in_tag, tds))
                    for idx_td, td in enumerate(new_tds):
                        if idx_td == 0:
                            round = td.get_text().lstrip().strip()
                        elif idx_td == 1:
                            for element in months_dictionary:
                                if element in td.get_text():
                                    date = td.get_text().replace(element,months_dictionary[element])
                                    break
                                else:
                                    date = ""
                                    continue
                        elif idx_td == 2:
                            if "(" in td.get_text():
                                home_team = td.get_text().split("(")[0].replace(u'\xa0', '')
                            else:
                                home_team = td.get_text()
                        elif idx_td == 3:
                            if "(" in td.get_text():
                                away_team = td.get_text().split("(")[0].replace(u'\xa0', '')
                            else:
                                away_team = td.get_text()
                        elif idx_td == 4:
                            result = td.get_text()
                        elif td.has_attr('colspan') == True and idx_td == 5:
                            position = goals = assists = own_goals = yellow_card = two_yellow_card = red_card = from_bench = changes = minutes = ""
                            out_reason = td.get_text()
                            out = True
                        elif idx_td == 5:
                            position = td.get_text()
                        elif idx_td == 6:
                            goals = td.get_text()
                        elif idx_td == 7:
                            assists = td.get_text()
                        elif idx_td == 8:
                            own_goals = td.get_text()
                        elif idx_td == 9:
                            yellow_card = td.get_text()
                        elif idx_td == 10:
                            two_yellow_card = td.get_text()
                        elif idx_td == 11:
                            red_card = td.get_text()
                        elif idx_td == 12:
                            from_bench = td.get_text().replace("'","")
                        elif idx_td == 13:
                            changes = td.get_text()
                        elif idx_td == 14:
                            minutes = td.get_text().replace("'","")
                            out_reason = ""
                            out = False
                    selected_data = {
                            "id": id,
                            "season": seasons_dictionary[year],
                            "league": unidecode(leagues[0]),
                            "round": unidecode(round),
                            "date": unidecode(date),
                            "home_team": unidecode(home_team),
                            "away_team": unidecode(away_team),
                            "result": unidecode(result),
                            "position": unidecode(position),
                            "goals": unidecode(goals),
                            "assists": unidecode(assists),
                            "own_goals": unidecode(own_goals),
                            "yellow_card": unidecode(yellow_card),
                            "two_yellow_card": unidecode(two_yellow_card),
                            "red_card": unidecode(red_card),
                            "from_bench": unidecode(from_bench),
                            "changes": unidecode(changes),
                            "minutes": unidecode(minutes),
                            "out": out,
                            "out_reason": unidecode(out_reason),
                        }
                    csv_writer.writerow(selected_data)
        if idx != 0:
            leagues.pop(0)


def check_if_image_in_tag(tag):
    if tag.find('img') == None:
        return True

    return False
def league_scrape(url, year):
    # /centralna-liga-juniorow/startseite/wettbewerb/PLZJ/plus/?saison_id=2018"
    #url = "https://www.transfermarkt.pl/wettbewerbe/europa/wettbewerbe?plus=1"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    leagues_type = soup.find_all("td", {"class": "extrarow bg_blau_20 hauptlink"})
    youth_league = False
    for league in leagues_type:
        if "Liga młodzieżowa" in league.get_text():
            youth_league = True

    leagues = soup.find("tbody").find_all("table")
    if youth_league:
        for league in leagues:
            league_url = league.find("td").find("a")['href']
            club_scrape(league_url+"/plus/?saison_id="+year,year)
    link = soup.find("link", {"rel": "next"})
    league_scrape(link['href'],year)
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #get_seasons("/jakub-kaminski/profil/spieler/407098")
   # season('a') #https://www.transfermarkt.pl/jan-andrzejewski/leistungsdaten/spieler/289163/saison/2014/plus/1
    #scrape_player("/michal-macuk/profil/spieler/387262")
    seasons_lis = ["2018", "2019", "2020", "2021", "2022", "2023"]
    for seasons in seasons_lis:
        league_scrape("https://www.transfermarkt.pl/wettbewerbe/europa/wettbewerbe?plus=1&page=12", seasons)



    #get_season("https://www.transfermarkt.pl/jan-andrzejewski/leistungsdaten/spieler/289163","2014") #view-source:https://www.transfermarkt.pl/jan-andrzejewski/leistungsdaten/spieler/289163/saison/2014/plus/1
'''
    selected_keys = ['id','season','date', 'marketValue', 'fee', 'clubName1', 'clubName2']
    with open('transfers',"a", newline="") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=selected_keys)
        csv_writer.writeheader()
    selected_keys = ['id','value','date', 'club', 'age']
    with open('player_value',"a", newline="") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=selected_keys)
        csv_writer.writeheader()
    selected_keys = ['id', 'name', 'place_of_birth', 'brith_date', 'nationality', 'height', 'position']
    with open('players',"a", newline="") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=selected_keys)
        csv_writer.writeheader()
    club_scrape()
    '''




# See PyCharm help at https://www.jetbrains.com/help/pycharm/
