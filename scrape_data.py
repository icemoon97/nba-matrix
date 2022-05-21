from urllib.request import urlopen
from bs4 import BeautifulSoup
import json

#useful = "https://en.wikipedia.org/wiki/Wikipedia:WikiProject_National_Basketball_Association/National_Basketball_Association_team_abbreviations"

YEAR = 2021

def write_to_json(filename, obj):
    with open(f"data/{filename}.json", "w") as outfile:
        json.dump(obj, outfile)

# returns array of (date, team, opp_team, pts) for each game in player's gamelog
def get_player_data(url):
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find(id="pgl_basic")

    data = []

    # looping through each row
    for trb in table.tbody.find_all("tr"):
        row_info = {}

        # looping through data elements within row
        for td in trb.find_all('td'):
            stat = td['data-stat']
            row_info[stat] = td.get_text()

        if "game_score" in row_info:
            data.append((row_info["date_game"], row_info["team_id"], row_info["opp_id"], float(row_info["game_score"]), row_info["game_result"]))

    return data

#print(get_player_data("https://www.basketball-reference.com/players/j/jamesle01/gamelog/2021"))

playerlist_soup = BeautifulSoup(urlopen(f"https://www.basketball-reference.com/leagues/NBA_{YEAR}_per_game.html"), 'html.parser')

players = []
player_index = {}
player_link = {}
player_extra_info = {} # games played, might add more later

table = playerlist_soup.find(id="per_game_stats")

for trb in table.tbody.find_all("tr"):
    if trb["class"][0] != "full_table": # skip partial rows
        continue

    name = ""
    link = ""
    row_info = {}

    for td in trb.find_all('td'):
        stat = td["data-stat"]

        if stat == "player":
            name = td.find("a").get_text()
            link = td.find("a")["href"][:-5]

        row_info[stat] = td.get_text()

    # only reads gamelog of players above certain cutoff
    if float(row_info["mp_per_g"]) >= 30:
        players.append(name)
        player_link[name] = link
        player_extra_info[name] = int(row_info["g"])

for i,p in enumerate(players):
    player_index[p] = i

player_gamelog = {}
game_lookup = {} # dates to dict{ team -> [(player,points)...] }

for i,name in enumerate(players):
    print(f"reading {name}, player {i+1}/{len(players)}")
    player_gamelog[name] = get_player_data(f"https://www.basketball-reference.com{player_link[name]}/gamelog/{YEAR}")

    for date, team_id, _, pts, _ in player_gamelog[name]:
        if date not in game_lookup:
            game_lookup[date] = {}

        if team_id not in game_lookup[date]:
            game_lookup[date][team_id] = {}

        if name not in game_lookup[date][team_id]:
            game_lookup[date][team_id][name] = pts


matchup_matrix = [[0 for _ in range(len(players))] for _ in range(len(players))]

# adjustment based on games played and game result
def adjustment(stat, gp, won, gp_adj=True, result_adj=True):
    if gp_adj:
        stat *= 72 / gp
    
    if result_adj:
        if won:
            stat *= 1.50
        else:
            stat *= 0.50

    return stat

# loop through each player's gamelog, find their matchups from game_lookup dict, and write entry to matchup_matrix
for name in players:
    i = player_index[name]
    gamelog = player_gamelog[name]

    for date, _, opp_id, pts, game_result in gamelog:
        if date in game_lookup and opp_id in game_lookup[date]:
            matchup = game_lookup[date][opp_id]

            for opp, opp_pts in matchup.items():
                j = player_index[opp]

                matchup_matrix[i][j] += adjustment(pts, player_extra_info[name], "W" in game_result, gp_adj=False)
                matchup_matrix[j][i] += adjustment(opp_pts, player_extra_info[opp], "L" in game_result, gp_adj=False)

# write results to json
to_write = {"matrix": matchup_matrix, "player_list": players}
write_to_json("gmsc_30mpg_matrix2", to_write)