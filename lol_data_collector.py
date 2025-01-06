import os
import requests
from dotenv import load_dotenv
from summoner_list import summoner_name_list
import time
import csv
from collections import deque

''' Load the API key from .env file '''
load_dotenv()
API_KEY = os.getenv("RIOT_API_KEY")

BASE_URL = "https://europe.api.riotgames.com" 
MATCHES_PER_PLAYER = 20
MAX_REQUESTS_PER_SECOND = 20  
MAX_REQUESTS_PER_2_MINUTES = 100
MAX_MATCHES = 100000

request_timestamps = deque()

''' Function to retrieve PUUID based on summoner name and tag '''
def get_puuid_by_name_and_tag(name, tag):
    wait_for_rate_limit()  
    url = f"{BASE_URL}/riot/account/v1/accounts/by-riot-id/{name}/{tag}"
    response = requests.get(url, headers={"X-Riot-Token": API_KEY})
    log_request_time()  
    if response.status_code == 200:
        return response.json().get("puuid")
    else:
        print(f"Error getting PUUID for {name}#{tag}: {response.status_code}")
        return None

''' Function to retrieve match IDs '''
def get_match_ids(puuid, count=MATCHES_PER_PLAYER):
    wait_for_rate_limit()
    url = f"{BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
    response = requests.get(url, headers={"X-Riot-Token": API_KEY})
    log_request_time()  
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting match IDs for PUUID {puuid}: {response.status_code}")
        return []

''' Function to retrieve detailed match data '''
def get_match_data(match_id):
    wait_for_rate_limit()  
    url = f"{BASE_URL}/lol/match/v5/matches/{match_id}"
    response = requests.get(url, headers={"X-Riot-Token": API_KEY})
    log_request_time()  
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting match data for {match_id}: {response.status_code}")
        return None

''' Function to retrieve timeline data of a match '''
def get_match_timeline(match_id):
    wait_for_rate_limit()  
    url = f"{BASE_URL}/lol/match/v5/matches/{match_id}/timeline"
    response = requests.get(url, headers={"X-Riot-Token": API_KEY})
    log_request_time() 
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting match timeline for {match_id}: {response.status_code}")
        return None

''' Function to save data to a CSV file '''
def save_to_csv(data, filename="match_data.csv"):
    fieldnames = [
        "match_id", "game_duration", "blue_win", "red_win", 
        "blueGold", "blueMinionsKilled", "blueJungleMinionsKilled", "blueAvgLevel",
        "blueChampKills", "blueHeraldKills", "blueDragonKills", "blueTowersDestroyed",
        "redGold", "redMinionsKilled", "redJungleMinionsKilled", "redAvgLevel",
        "redChampKills", "redHeraldKills", "redDragonKills", "redTowersDestroyed",
        "summoner_name", "team", "champion_name", "kills", "deaths", "assists",
        "totalGold", "xp", "minionsKilled", "totalDamageDone"
    ]
    
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        writer.writerows(data)

''' Function to handle API rate limits '''
def wait_for_rate_limit():
    now = time.time()
    
    ''' Remove requests older than 2 minutes '''
    while request_timestamps and request_timestamps[0] < now - 120:
        request_timestamps.popleft()

    ''' If more than 100 requests in the last 2 minutes, wait '''
    if len(request_timestamps) >= MAX_REQUESTS_PER_2_MINUTES:
        sleep_time = 120 - (now - request_timestamps[0])  
        print(f"Rate limit exceeded (100 requests per 2 minutes). Sleeping for {sleep_time:.2f} seconds.")
        time.sleep(sleep_time)

    ''' If more than 20 requests in the last second, wait '''
    if len(request_timestamps) >= MAX_REQUESTS_PER_SECOND:
        sleep_time = 1 - (now - request_timestamps[-1])  
        if sleep_time > 0:
            print(f"Sleeping for {sleep_time:.2f} seconds to avoid exceeding 20 requests per second.")
            time.sleep(sleep_time)

def log_request_time():
    request_timestamps.append(time.time())

''' Function to filter timeline data '''
def extract_data_from_timeline(timeline_data, match_data):
    frames = timeline_data.get("info", {}).get("frames", [])
    last_timestamp = frames[-1].get("timestamp") if frames else None

    if len(frames) < 15:
        print("Skipping game due to insufficient frames.")
        return {}, {}, {}, 0, 0

    frame_15_min = frames[14]
    timestamp_15_min = frame_15_min.get("timestamp", 0)
    participant_frames = frame_15_min.get("participantFrames", {})
    stats_15_min = {}

    blue_stats = {
        "blue_win": False,
        "blueGold": 0,
        "blueMinionsKilled": 0,
        "blueJungleMinionsKilled": 0,
        "blueAvgLevel": 0.0,
        "blueChampKills": 0,
        "blueHeraldKills": 0,
        "blueDragonKills": 0,
        "blueTowersDestroyed": 0
    }

    red_stats = {
        "red_win": False,
        "redGold": 0,
        "redMinionsKilled": 0,
        "redJungleMinionsKilled": 0,
        "redAvgLevel": 0.0,
        "redChampKills": 0,
        "redHeraldKills": 0,
        "redDragonKills": 0,
        "redTowersDestroyed": 0
    }

    for participant_id in range(1, 11):
        stats_15_min[participant_id] = {
            "kills": 0,
            "deaths": 0,
            "assists": 0,
            "totalGold": 0,
            "xp": 0,
            "totalDamageDone": 0,
            "minionsKilled": 0,
            "championName": "Unknown"
        }

    # Players statistics
    for participant_id, participant_data in participant_frames.items():

        # Statistics for individual players
        stats_15_min[int(participant_id)] = {
            "totalGold": participant_data.get("totalGold", 0),
            "xp": participant_data.get("xp", 0),
            "totalDamageDone": participant_data.get("damageStats", {}).get("totalDamageDone", 0),
            "minionsKilled": participant_data.get("minionsKilled", 0),
            "championName": participant_data.get("championName", "Unknown"),
            "kills": participant_data.get("stats", {}).get("kills", 0),
            "deaths": participant_data.get("stats", {}).get("deaths", 0),
            "assists": participant_data.get("stats", {}).get("assists", 0)
        }

        # Team statistics
        team_id = int(participant_id) <= 5 and 100 or 200

        if team_id == 100:
            blue_stats["blueGold"] += participant_data.get("totalGold", 0)
            blue_stats["blueMinionsKilled"] += participant_data.get("minionsKilled", 0)
            blue_stats["blueJungleMinionsKilled"] += participant_data.get("jungleMinionsKilled", 0)
            blue_stats["blueAvgLevel"] += participant_data.get("level", 0)
        elif team_id == 200:
            red_stats["redGold"] += participant_data.get("totalGold", 0)
            red_stats["redMinionsKilled"] += participant_data.get("minionsKilled", 0)
            red_stats["redJungleMinionsKilled"] += participant_data.get("jungleMinionsKilled", 0)
            red_stats["redAvgLevel"] += participant_data.get("level", 0)

    blue_levels = []
    red_levels = []

    for frame in frames:
        for participant_id, participant_data in frame["participantFrames"].items():
            if participant_data["participantId"] in range(1, 6):
                blue_levels.append(participant_data["level"])
            elif participant_data["participantId"] in range(6, 11):
                red_levels.append(participant_data["level"])

    if blue_levels:
        blue_stats["blueAvgLevel"] = round(sum(blue_levels) / len(blue_levels), 1)
    if red_levels:
        red_stats["redAvgLevel"] = round(sum(red_levels) / len(red_levels), 1)

    # Counting team results
    for team in match_data["info"]["teams"]:
        if team["teamId"] == 100:
            blue_stats["blue_win"] = team["win"]
        elif team["teamId"] == 200:
            red_stats["red_win"] = team["win"]

    for frame in frames:
        if frame["timestamp"] > 900000:
            break

        events = frame.get("events", [])
        for event in events:
            if event["type"] == "CHAMPION_KILL":
                killer_id = event["killerId"]
                victim_id = event["victimId"]
                assister_ids = event.get("assistingParticipantIds", [])

                if killer_id in stats_15_min:
                    stats_15_min[killer_id]["kills"] += 1

                if victim_id in stats_15_min:
                    stats_15_min[victim_id]["deaths"] += 1

                for assister_id in assister_ids:
                    if assister_id in stats_15_min:
                        stats_15_min[assister_id]["assists"] += 1

                if killer_id in range(1, 6):
                    blue_stats["blueChampKills"] += 1
                elif killer_id in range(6, 11):
                    red_stats["redChampKills"] += 1

            elif event["type"] == "ELITE_MONSTER_KILL":
                if event["monsterType"] == "RIFTHERALD":
                    if event["killerId"] in range(1, 6):
                        blue_stats["blueHeraldKills"] += 1
                    elif event["killerId"] in range(6, 11):
                        red_stats["redHeraldKills"] += 1
                elif event["monsterType"] == "DRAGON":
                    if event["killerId"] in range(1, 6):
                        blue_stats["blueDragonKills"] += 1
                    elif event["killerId"] in range(6, 11):
                        red_stats["redDragonKills"] += 1

            elif event["type"] == "BUILDING_KILL":
                if event["buildingType"] == "TOWER_BUILDING":
                    if event["teamId"] == 200:
                        blue_stats["blueTowersDestroyed"] += 1
                    elif event["teamId"] == 100:
                        red_stats["redTowersDestroyed"] += 1

    return stats_15_min, blue_stats, red_stats, timestamp_15_min, last_timestamp

''' Main function '''
def main():
    all_data = []
    puuid_list = []
    unique_match_ids = set()
    seen_players = set()

    ''' Fetching PUUID for each player from the list'''
    for player in summoner_name_list:
        name = player["name"]
        tag = player["tag"]
        print(f"Fetching PUUID for {name}#{tag}...")
        puuid = get_puuid_by_name_and_tag(name, tag)
        if puuid:
            print(f"PUUID for {name}#{tag}: {puuid}")
            puuid_list.append(puuid)
        time.sleep(1.2)  

    ''' Fetching match data based on PUUID '''
    for puuid in puuid_list:
        print(f"Processing matches for PUUID: {puuid}")
        match_ids = get_match_ids(puuid)
        print(f"Found {len(match_ids)} matches for PUUID {puuid}")

        for match_id in match_ids:
            if match_id in unique_match_ids:
                continue
            unique_match_ids.add(match_id)

            if len(unique_match_ids) > MAX_MATCHES:
                print("Reached maximum unique matches. Stopping data collection")
                break

            match_data = get_match_data(match_id)
            if not match_data:
                print(f"Failed to fetch match data for {match_id}")
                continue

            timeline_data = get_match_timeline(match_id)
            if not timeline_data:
                print(f"Failed to fetch timeline data for {match_id}")
                continue

            stats_15_min, blue_stats, red_stats, timestamp_15_min, last_timestamp = extract_data_from_timeline(timeline_data, match_data)

            if not blue_stats or not red_stats:
                print(f"Skipping match {match_id} due to insufficient data.")
                continue

            game_info = match_data.get("info", {})
            participants = game_info.get("participants", [])

            ''' Collecting player and team results '''
            match_result = {
                "match_id": match_id,
                "game_duration": round(last_timestamp / 1000),
                "blue_win": blue_stats["blue_win"],
                "red_win": red_stats["red_win"],
                "blueGold": blue_stats["blueGold"],
                "blueMinionsKilled": blue_stats["blueMinionsKilled"],
                "blueJungleMinionsKilled": blue_stats["blueJungleMinionsKilled"],
                "blueAvgLevel": blue_stats["blueAvgLevel"],
                "blueChampKills": blue_stats["blueChampKills"],
                "blueHeraldKills": blue_stats["blueHeraldKills"],
                "blueDragonKills": blue_stats["blueDragonKills"],
                "blueTowersDestroyed": blue_stats["blueTowersDestroyed"],
                "redGold": red_stats["redGold"],
                "redMinionsKilled": red_stats["redMinionsKilled"],
                "redJungleMinionsKilled": red_stats["redJungleMinionsKilled"],
                "redAvgLevel": red_stats["redAvgLevel"],
                "redChampKills": red_stats["redChampKills"],
                "redHeraldKills": red_stats["redHeraldKills"],
                "redDragonKills": red_stats["redDragonKills"],
                "redTowersDestroyed": red_stats["redTowersDestroyed"]
            }

            ''' Player information'''
            for participant_id, participant_data in stats_15_min.items():
                participant_info = next((p for p in participants if p["participantId"] == int(participant_id)), None)

                if not participant_info:
                    print(f"Participant data not found for id: {participant_id}, skipping.")
                    continue

                summoner_name = participant_info.get("summonerName", "Unknown")
                team = participant_info.get("teamId", 0)
                champion_name = participant_info.get("championName", "Unknown")

                totalGold = participant_data.get("totalGold", 0)
                xp = participant_data.get("xp", 0)
                totalDamageDone = participant_data.get("totalDamageDone", 0)
                minionsKilled = participant_data.get("minionsKilled", 0)

                player_key = (summoner_name, match_id)
                if player_key in seen_players:
                    continue

                seen_players.add(player_key)

                player_stats = {
                    "summoner_name": summoner_name,
                    "team": "blue" if team == 100 else "red",
                    "champion_name": champion_name,
                    "kills": participant_data.get("kills", 0),
                    "deaths": participant_data.get("deaths", 0),
                    "assists": participant_data.get("assists", 0),
                    "totalGold": totalGold,
                    "xp": xp,
                    "totalDamageDone": totalDamageDone,
                    "minionsKilled": minionsKilled
                }

                match_entry = {**match_result, **player_stats}
                if match_entry not in all_data:
                    all_data.append(match_entry)

            if len(all_data) >= MAX_MATCHES:
                print("Reached the maximum limit of match data. Stopping.")
                break

        if len(all_data) >= MAX_MATCHES:
            break

        time.sleep(1)

    ''' Saving data to a CSV file '''
    if all_data:
        print(f"Saving {len(all_data)} entries to match_data.csv...")
        save_to_csv(all_data)
        print("Data saved to match_data.csv")
    else:
        print("No data to save.")

if __name__ == "__main__":
    main()

