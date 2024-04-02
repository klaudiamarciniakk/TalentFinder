import csv
import os

import requests
from tqdm import tqdm
from unidecode import unidecode

headers = {
    'authority': 'api.sofascore.com',
    'accept': '*/*',
    'accept-language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'if-none-match': 'W/"7dd2d62cd7"',
    'origin': 'https://www.sofascore.com',
    'referer': 'https://www.sofascore.com/',
    'sec-ch-ua': '"Chromium";v="118", "Opera GX";v="104", "Not=A?Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 OPR/104.0.0.0',
    'If-Modified-Since': 'Sun, 3 Dec 2023 00:00:00 GMT'

}


def get_players(players_ids_src):
    players_list = []
    with open(players_ids_src, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)

        row_count = sum(1 for _ in csv_reader)
        csv_file.seek(0)
        progress_bar = tqdm(total=row_count, desc='Processing first CSV ', unit='row', dynamic_ncols=True)
        processed_rows = 0

        for row in csv_reader:
            processed_rows += 1
            progress_bar.update(1)

            slug = row['slug']
            id_sofascore = row['id_sofascore']
            player_id = {'slug': slug, 'id_sofascore': id_sofascore}
            players_list.append(player_id)
    return players_list


def get_players_details(players_list, players_details_csv_file_path, selected_keys):
    with open(players_details_csv_file_path, "w", newline="") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=selected_keys)
        csv_writer.writeheader()

        row_count = sum(1 for _ in players_list)
        progress_bar = tqdm(total=row_count, desc='Downloading players details ', unit='row', dynamic_ncols=True)
        processed_rows = 0

        for player in players_list:
            if player["id_sofascore"] == 'id_sofascore':
                continue
            processed_rows += 1
            progress_bar.update(1)

            if player["id_sofascore"] == '':
                selected_data = {
                    "id": player["id_sofascore"],
                    "slug": player["slug"],
                    "team": None,
                    "height": None,
                    "preferredFoot": None,
                    "marketValue": None
                }
            else:
                response = requests.get(f'https://api.sofascore.com/api/v1/player/{player["id_sofascore"]}',
                                        headers=headers)
                player_response = response.json()
                player_data = player_response.get("player", {})
                if player["slug"] == player_data.get('slug', ""):
                    marketValue = str(player_data.get("proposedMarketValueRaw", {}).get("value", ""))
                    selected_data = {
                        "id": player_data.get("id", ""),
                        "slug": unidecode(player_data.get("slug", "")),
                        "team": unidecode(player_data.get("team", {}).get("slug", "")),
                        "height": player_data.get("height", ""),
                        "preferredFoot": player_data.get("preferredFoot", ""),
                        "marketValue": marketValue
                    }
                else:
                    selected_data = {
                        "id": player["id_sofascore"],
                        "slug": player["slug"],
                        "team": None,
                        "height": None,
                        "preferredFoot": None,
                        "marketValue": None
                    }
            csv_writer.writerow(selected_data)

    print(f"Dane zostały zapisane do pliku CSV: {players_details_csv_file_path}")


if __name__ == '__main__':
    players_details_csv_file_path = os.path.join('..', '..', 'data', 'sofascore', 'players_details_sofascore.csv')
    players_ids_src = os.path.join('..', '..', 'data', 'players', 'players_ids.csv')
    selected_keys = ["id", "slug", "team", "height", "preferredFoot", "marketValue"]

    players_list = get_players(players_ids_src)
    get_players_details(players_list, players_details_csv_file_path, selected_keys)
