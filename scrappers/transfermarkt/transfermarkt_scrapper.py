# This is a sample Python script.
import os

import requests
from bs4 import BeautifulSoup
import json
import csv
from unidecode import unidecode
import pandas as pd
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

headers = {
  'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
}
def scrape_player(uri):
    # Use a breakpoint in the code line below to debug your script.
    url = "https://www.transfermarkt.pl"+uri
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    id = url.split("spieler/")[1]
    name = url.split("transfermarkt.pl/")[1].split("/profil/")[0].replace("-", " ")
    header = soup.find_all('ul', {'class': 'data-header__items'})
    birth = header[0].find_all('li', {'class': 'data-header__label'})
    brith_date = ""
    place_of_birth = ""
    nationality = ""
    height = ""
    position = ""
    for data in birth:
        if data.find("span")["itemprop"] == "birthDate":
            brith_date = data.get_text().split("Urodz./Wiek:")[1].lstrip().strip()
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

    selected_keys = ['id', 'name', 'place_of_birth', 'brith_date', 'nationality', 'height', 'position']
    players_file_src = os.path.join('..', '..', 'data', 'transfermarkt', 'players.csv')
    with open(players_file_src, "a", newline="") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=selected_keys)
        selected_data = {
            "id": id,
            "name": unidecode(name),
            "place_of_birth": unidecode(place_of_birth),
            "brith_date": brith_date,
            "nationality": unidecode(nationality),
            "height": height,
            "position": unidecode(position),
        }
        print(selected_data)
        csv_writer.writerow(selected_data)
    transfery(id)
    market_value_scrape(id)



def transfery(id):
    url = f"https://www.transfermarkt.pl/ceapi/transferHistory/list/{id}"
    response = requests.get(url, headers=headers)
    json_result = json.loads(response.content)
    selected_keys = ['id','season','date', 'marketValue', 'fee', 'clubName1', 'clubName2']
    transfer_file_src = os.path.join('..', '..', 'data', 'transfermarkt', 'transfers.csv')
    with open(transfer_file_src, "a", newline="") as csv_file:
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
    player_value_file_src = os.path.join('..', '..', 'data', 'transfermarkt', 'player_value.csv')
    with open(player_value_file_src, "a", newline="") as csv_file:
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

def club_scrape():
    url="https://www.transfermarkt.pl/centralna-liga-juniorow/startseite/wettbewerb/PLZJ/plus/?saison_id=2018"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    clubs_list = soup.find_all('td', {'class': 'zentriert no-border-rechts'})
    for club in clubs_list:
        club_href = club.find("a")['href'].replace("saison_id/2018","saison_id/2016")
        club_players_scrape(club_href)
def club_players_scrape(uri):
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
                scrape_player(player_href)
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    transfer_file_src = os.path.join('..', '..', 'data', 'transfermarkt', 'transfers.csv')
    player_value_file_src = os.path.join('..', '..', 'data', 'transfermarkt', 'player_value.csv')
    players_file_src = os.path.join('..', '..', 'data', 'transfermarkt', 'players.csv')
    selected_keys = ['id','season','date', 'marketValue', 'fee', 'clubName1', 'clubName2']
    with open(transfer_file_src,"a", newline="") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=selected_keys)
        csv_writer.writeheader()
    selected_keys = ['id','value','date', 'club', 'age']
    with open(player_value_file_src,"a", newline="") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=selected_keys)
        csv_writer.writeheader()
    selected_keys = ['id', 'name', 'place_of_birth', 'brith_date', 'nationality', 'height', 'position']
    with open(players_file_src, "a", newline="") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=selected_keys)
        csv_writer.writeheader()
    club_scrape()




# See PyCharm help at https://www.jetbrains.com/help/pycharm/
