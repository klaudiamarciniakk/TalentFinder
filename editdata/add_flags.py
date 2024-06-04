from sqlalchemy import create_engine
import pandas as pd
import os
import pyodbc
import json

server = 'mssql-2017.labs.wmi.amu.edu.pl'
database = 'db_football_players'
username = 'db_football_players'
password = 'Lh4M466Ww7'

connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(connection_string)
def load_data():

 query_player_seasons = """
 SELECT * FROM [db_football_players].[dbo].[player_seasons]
 """
 df_player_seasons = pd.read_sql(query_player_seasons, engine)

 query_player_values = """
 SELECT * FROM [db_football_players].[dbo].[player_value]
 """
 df_player_values = pd.read_sql(query_player_values, engine)
 return df_player_seasons, df_player_values

def count_cards(card_string):
    if pd.isna(card_string):
        return 0
    else:
        return 1
def count_two_cards(card_string):
    if pd.isna(card_string):
        return 0
    else:
        return 2

def assign_season(date):
    if date.month < 8:
        return f"{date.year-1}/{date.year}"
    else:
        return f"{date.year}/{date.year+1}"


def generate_value_flag(df_player_values, df_player_seasons):
    df_player_seasons = generate_total_teams(df_player_seasons)
    df_player_values['date'] = pd.to_datetime(df_player_values['date'], format='%d.%m.%Y', errors='coerce')
    df_player_values['season'] = df_player_values['date'].apply(assign_season)
    df_player_values = df_player_values.sort_values(by=['id', 'date'])
    df_player_values['value_change'] = df_player_values.groupby('id')['value'].diff()
    df_player_values['club_changed'] = df_player_values.groupby('id')['club'].shift() != df_player_values['club']
    df_player_values['VALUE_FLAG'] = df_player_values.apply(lambda row: '' if not row['club_changed'] else (
        'SAME_VALUE' if row['value_change'] == 0 else (
            'MORE_VALUEABLE' if row['value_change'] > 0 else 'LESS_VALUEABLE')), axis=1)
    df_player_seasons = df_player_seasons.merge(df_player_values[['id', 'season', 'VALUE_FLAG']], on=['id', 'season'],
                                                how='left')
    return df_player_seasons
def generate_total_teams(df_player_seasons):
    home_games = df_player_seasons.groupby(['id', 'season', 'league', 'home_team']).size().reset_index(
        name='home_count')
    away_games = df_player_seasons.groupby(['id', 'season', 'league', 'away_team']).size().reset_index(
        name='away_count')
    sorted_home_games = home_games.sort_values(by=['id', 'season', 'league', 'home_count'], ascending=False)
    sorted_away_games = away_games.sort_values(by=['id', 'season', 'league', 'away_count'], ascending=False)
    sorted_home_games = sorted_home_games.groupby(['id', 'season', 'league']).agg({
        'home_count': 'first',
        'home_team': 'first'
    }).reset_index()
    sorted_away_games = sorted_away_games.groupby(['id', 'season', 'league']).agg({
        'away_count': 'first',
        'away_team': 'first'
    }).reset_index()
    total_games = pd.merge(sorted_home_games, sorted_away_games, left_on=['id', 'season', 'league'], right_on=['id', 'season', 'league'],
                           how='outer', suffixes=('_home', '_away'))
    total_games.fillna({'home_count': 0, 'away_count': 0}, inplace=True)
    total_games['total_games'] = total_games['home_count'] + total_games['away_count']
    total_games['team'] = total_games.apply(
        lambda x: x['home_team'] if x['home_count'] >= x['away_count'] else x['away_team'], axis=1)
    temp = total_games.sort_values(by=['id', 'season', 'league', 'total_games'], ascending=False)
    player_team = temp.groupby(['id', 'season', 'league']).agg({
        'total_games': 'first',
        'team': 'first'
    }).reset_index()
    df_player_seasons = df_player_seasons.merge(player_team[['id', 'season', 'team']], on=['id', 'season'])
    return df_player_seasons
def generate_red_card_player_flag(df_player_seasons):
    df_player_seasons = generate_total_teams(df_player_seasons)
    df_player_seasons['red_cards_count'] = df_player_seasons['red_card'].apply(count_cards)
    average_red_cards = df_player_seasons.groupby(['season', 'team'])['red_cards_count'].mean().reset_index()
    df_player_seasons = df_player_seasons.merge(average_red_cards, on=['season', 'team'], suffixes=('', '_avg'))
    average_cards_per_player = df_player_seasons.groupby(['id', 'season', 'team']).agg(
        average_red_cards_per_player=('red_cards_count', 'mean')
    ).reset_index()
    df_player_seasons = df_player_seasons.merge(average_cards_per_player, on=['id', 'season', 'team'])
    df_player_seasons['RED_CARD_PLAYER'] = df_player_seasons.apply(
        lambda x: 'RED_CARD_PLAYER' if x['average_red_cards_per_player'] > x['red_cards_count_avg'] else '', axis=1)
    return df_player_seasons
def generate_yellow_card_player_flag(df_player_seasons):
    df_player_seasons = generate_total_teams(df_player_seasons)
    df_player_seasons['yellow_cards_count'] = df_player_seasons['yellow_card'].apply(count_cards) + df_player_seasons[
        'two_yellow_card'].apply(count_two_cards)
    average_yellow_cards = df_player_seasons.groupby(['season', 'team'])['yellow_cards_count'].mean().reset_index()
    df_player_seasons = df_player_seasons.merge(average_yellow_cards, on=['season', 'team'], suffixes=('', '_avg'))
    average_cards_per_player = df_player_seasons.groupby(['id', 'season', 'team']).agg(
        average_yellow_cards_per_player=('yellow_cards_count', 'mean'),
    ).reset_index()

    df_player_seasons = df_player_seasons.merge(average_cards_per_player, on=['id', 'season', 'team'])
    df_player_seasons['YELLOW_CARD_PLAYER'] = df_player_seasons.apply(
        lambda x: 'YELLOW_CARD_PLAYER' if x['average_yellow_cards_per_player'] > x['yellow_cards_count_avg'] else '',
        axis=1)
    return df_player_seasons
def merge_flags(df_player_seasons, final_data):
    df_player_seasons = df_player_seasons.merge(final_data, on=['id', 'season', 'team'], how='left')
    return df_player_seasons
def generate_flags(flag_list, df_player_seasons, df_player_values):
    final_data = generate_total_teams(df_player_seasons)[['id', 'season', 'team']]
    if 'red_card_player' in flag_list:
        df_player_seasons_rcp=generate_red_card_player_flag(df_player_seasons)
        df_player_seasons_rcp = df_player_seasons_rcp.reindex(columns=['id', 'season', 'team', 'RED_CARD_PLAYER'])
        final_data_rcp = df_player_seasons_rcp[['id', 'season', 'team', 'RED_CARD_PLAYER']]
        final_data_rcp = final_data_rcp.drop_duplicates(subset=['id', 'season', 'team'])
        final_data=merge_flags(final_data, final_data_rcp)
    if 'yellow_card_player' in flag_list:
        df_player_seasons_ycp=generate_yellow_card_player_flag(df_player_seasons)
        df_player_seasons_ycp = df_player_seasons_ycp.reindex(columns=['id', 'season', 'team', 'YELLOW_CARD_PLAYER'])
        final_data_ycp = df_player_seasons_ycp[['id', 'season', 'team', 'YELLOW_CARD_PLAYER']]
        final_data_ycp = final_data_ycp.drop_duplicates(subset=['id', 'season', 'team'])
        final_data=merge_flags(final_data, final_data_ycp)
    if 'value_flag' in flag_list:
        df_player_seasons_vf=generate_value_flag(df_player_values, df_player_seasons)
        df_player_seasons_vf = df_player_seasons_vf.reindex(columns=['id', 'season', 'team', 'VALUE_FLAG'])
        final_data_vf = df_player_seasons_vf[['id', 'season', 'team','VALUE_FLAG']]
        final_data_vf = final_data_vf.drop_duplicates(subset=['id', 'season', 'team'])
        final_data=merge_flags(final_data, final_data_vf)

    print("Zakończono generowanie flag.")

    if final_data is not None:
        if os.path.exists('flags_result.json'):
            print("Ładowanie danych z pliku 'flags_result.json'...")
            with open('flags_result.json', 'r') as f:
                data = json.load(f)
                df_player_seasons = pd.read_json(data, orient='records')
            result = merge_flags(df_player_seasons, final_data)
            result = result.drop_duplicates(subset=['id', 'season', 'team'])
            result = result.to_json(orient='records')
        else:
            result = final_data.drop_duplicates(subset=['id', 'season', 'team'])
            result = result.to_json(orient='records')
        with open('flags_result.json', 'w') as f:
            json.dump(result, f)

def delete_flags(flag_list, df_player_seasons, df_player_values):
    if os.path.exists('flags_result.json'):
        print("Ładowanie danych z pliku 'flags_result.json'...")
        with open('flags_result.json', 'r') as f:
            data = json.load(f)
            df_player_seasons = pd.read_json(data, orient='records')
        if 'red_card_player' in flag_list:
            df_player_seasons = df_player_seasons.drop(['RED_CARD_PLAYER'], axis=1)
        if 'yellow_card_player' in flag_list:
            df_player_seasons = df_player_seasons.drop(['YELLOW_CARD_PLAYER'], axis=1)
        if 'value_flag' in flag_list:
            df_player_seasons = df_player_seasons.drop(['VALUE_FLAG'], axis=1)
        result = df_player_seasons.to_json(orient='records')
        with open('flags_result.json', 'w') as f:
            json.dump(result, f)

def main():
    df_player_seasons, df_player_values = load_data()
    action = input("Chcesz wygenerować czy usunąć flagi? (wygenerować/usunąć): ")
    if action.lower() == 'wygenerować':
        print("Jakie flagi chcesz wygenerować?")
        print("1. Red Card Player\n2. Yellow Card Player\n3. Value Flag")
        selected_flags = input("Podaj numery flag, które chcesz wygenerować (np. 1, 3): ")
        flag_map = {'1': 'red_card_player', '2': 'yellow_card_player', '3': 'value_flag'}
        flag_list = [flag_map[num.strip()] for num in selected_flags.split(',') if num.strip() in flag_map]
        generate_flags(flag_list, df_player_seasons, df_player_values)
    elif action.lower() == 'usunąć':
        print("Usuwanie flag...")
        selected_flags = input("Podaj numery flag, które chcesz usunać (np. 1, 3): ")
        flag_map = {'1': 'red_card_player', '2': 'yellow_card_player', '3': 'value_flag'}
        flag_list = [flag_map[num.strip()] for num in selected_flags.split(',') if num.strip() in flag_map]
        delete_flags(flag_list, df_player_seasons, df_player_values)
if __name__ == "__main__":
    main()
