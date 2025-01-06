## Project Description
**League of Legends Data Collector** is a Python tool that leverages the Riot Games Developer API to collect and perform preliminary analysis of match data for players on a predefined list. League of Legends (LoL) is a popular online multiplayer battle arena (MOBA) game where players form teams of five and compete to destroy the enemy's Nexus. The game emphasizes teamwork, strategic thinking, and individual skill, with players selecting champions to battle, grow in power, and work towards victory.

The project facilitates the gathering of detailed match statistics and saves them to a CSV file, making it easier to perform further analysis.

---

## Functionalities
- **Player PUUID Collection**: Automatically fetch unique player identifiers based on their names and tags.
- **Match Data Collection**: Retrieve match IDs and detailed match data.
- **Timeline Analysis**: Extract statistics from the first 15 minutes of each match.
- **Query Limit Management**: The tool adheres to rate limits imposed by the Riot API.
- **Data Export**: Saves collected data in CSV format, ready for use in analytical tools

---

## Data Collected
The data collected from each match includes:

- **match_id**: A unique identifier for each match.
- **game_duration**: The length of the match in seconds.
- **blue_win**: Boolean indicating whether the blue team won.
- **red_win**: Boolean indicating whether the red team won.
- **blueGold**: Gold accumulated by the blue team.
- **blueMinionsKilled**: Minions killed by the blue team.
- **blueJungleMinionsKilled**: Jungle minions killed by the blue team.
- **blueAvgLevel**: Average level of the blue team champions.
- **blueChampKills**: Champion kills by the blue team.
- **blueHeraldKills**: Rift Herald kills by the blue team.
- **blueDragonKills**: Dragon kills by the blue team.
- **blueTowersDestroyed**: Towers destroyed by the blue team.
- **redGold**: Gold accumulated by the red team.
- **redMinionsKilled**: Minions killed by the red team.
- **redJungleMinionsKilled**: Jungle minions killed by the red team.
- **redAvgLevel**: Average level of the red team champions.
- **redChampKills**: Champion kills by the red team.
- **redHeraldKills**: Rift Herald kills by the red team.
- **redDragonKills**: Dragon kills by the red team.
- **redTowersDestroyed**: Towers destroyed by the red team.
- **summoner_name**: The player's in-game name.
- **team**: Indicates which team (blue or red) the player belongs to.
- **champion_name**: The name of the champion the player played.
- **kills**: Number of kills the player secured.
- **deaths**: Number of times the player died.
- **assists**: Number of assists the player contributed.
- **totalGold**: The total gold the player earned.
- **xp**: Experience points gained by the player.
- **minionsKilled**: Number of minions killed by the player.
- **totalDamageDone**: The total damage dealt by the player.
  
Each of these metrics provides insights into the performance of players and teams in League of Legends matches, which can be valuable for player analysis, strategy development, and gameplay improvement.

---

## Requirements
- **Python 3.8+**
- Required Python Libraries:
  - `os`
  - `requests`
  - `dotenv`
  - `time`
  - `csv`
  - `collections` (deque)
- **Riot Games API Key:**
  Obtain your API key from the [Riot Developer Portal](https://developer.riotgames.com/).
- **Create a `.env` file:**
   Add your Riot API key in the `.env` file located in the main project directory:
   ```env
   RIOT_API_KEY=your-api-key
   ```
---

## Usage
1. **Run the main script:**
   - The script will create or update the `match_data.csv` file in the main directory.
3. **Results:**
   - The CSV file will contain detailed match data, including player and team statistics.

---

## Main Functions
- **`get_puuid_by_name_and_tag(name, tag)`**
  - Fetches the PUUID (Platform Unique ID) for the specified player name and tag.
- **`get_match_ids(puuid, count)`**
  - Retrieves match IDs for a given player.
- **`get_match_data(match_id)`**
  - Fetches detailed match data for a specific match ID.
- **`get_match_timeline(match_id)`**
  - Retrieves the timeline of events for the match.
- **`extract_data_from_timeline(timeline_data, match_data)`**
  - Analyzes timeline data, extracting key statistics from the early game phase.
- **`save_to_csv(data, filename)`**
  - Saves the collected data to a CSV file.

---

## Query Limits
To adhere to Riot API rate limits:
- **Maximum 20 requests per second**
- **Maximum 100 requests per 2 minutes**
- The script will automatically wait if these limits are exceeded.

---

## License
This project is licensed under the MIT License. More details can be found in the `LICENSE` file.

---

## Acknowledgements
- Thanks to Riot Games for providing the API and data.
