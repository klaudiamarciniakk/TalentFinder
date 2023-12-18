import csv
from datetime import datetime
from tqdm import tqdm
import requests
import os

headers = {
    'authority': 'api.sofascore.com',
    'accept': '*/*',
    'accept-language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'if-none-match': 'W/"f810540cc3"',
    'origin': 'https://www.sofascore.com',
    'referer': 'https://www.sofascore.com/',
    'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Opera GX";v="102"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 OPR/102.0.0.0',
    'If-Modified-Since': 'Sun, 19 Nov 2023 00:00:00 GMT'
}


def timestamp_to_date(timestamp):
    try:
        dt_object = datetime.utcfromtimestamp(timestamp)
        formatted_date = dt_object.strftime('%Y-%m-%d')
        return formatted_date
    except TypeError:
        print(f"Invalid timestamp: {timestamp}")
        return None
    except OSError:
        print(f"Invalid timestamp: {timestamp}")
        return None

def format_date(input_date):
    try:
        parsed_date = datetime.strptime(input_date, '%d.%m.%Y')
        formatted_date = parsed_date.strftime('%Y-%m-%d')
        return formatted_date
    except ValueError:
        return None


def get_players_list(players_id_file_src):
    with open(players_id_file_src, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        next(csv_reader)
        rest = list(csv_reader)
        row_count = sum(1 for _ in rest)
        csv_file.seek(0)
        progress_bar = tqdm(total=row_count, desc='Processing CSV', unit='row', dynamic_ncols=True)
        processed_rows = 0
        players_list = []
        for row in rest:
            processed_rows += 1
            progress_bar.update(1)
            slug = row['slug']
            id_transfermarkt = row['id']

            player = requests.get(f'https://api.sofascore.com/api/v1/search/{slug}', headers=headers).json()
            players_details = player.get("results", [])
            correct_player_flag = False
            if len(players_details) != 0:
                for player_data in players_details:
                    if player_data.get('type', "") == "player":
                        player = player_data.get("entity", {})
                        player_details = requests.get(f'https://api.sofascore.com/api/v1/player/{player.get("id", "")}',
                                                      headers=headers).json()
                        details = player_details.get("player", {})
                        date_of_birth_timestamp = details.get("dateOfBirthTimestamp", "")
                        if format_date(row['birth_date']) == timestamp_to_date(date_of_birth_timestamp):
                            player_ids = {'slug': slug, 'id_transfermarkt': id_transfermarkt,
                                          'id_sofascore': player.get("id", "")}
                            correct_player_flag = True
                            break
                if not correct_player_flag:
                    player_ids = {'slug': slug, 'id_transfermarkt': id_transfermarkt, 'id_sofascore': None}
            else:
                player_ids = {'slug': slug, 'id_transfermarkt': id_transfermarkt, 'id_sofascore': None}
            players_list.append(player_ids)
    return players_list


def save_players_list_to_csv(output_filename, players_list):
    with open(output_filename, 'w', newline='') as output_csv_file:
        fieldnames = ['slug', 'id_transfermarkt', 'id_sofascore']
        csv_writer = csv.DictWriter(output_csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(players_list)


if __name__ == '__main__':
    players_id_file_src = os.path.join('..', '..', 'data', 'transfermarkt', 'players.csv')
    output_filename = os.path.join('..', '..', 'data', 'players', 'players_ids.csv')
    players_list = get_players_list(players_id_file_src)
    save_players_list_to_csv(output_filename, players_list)
