from urllib.request import urlopen
from bs4 import BeautifulSoup
import json

def write_to_json(filename, obj):
    with open(f"{filename}.json", "w") as outfile:
        json.dump(obj, outfile)

soup = BeautifulSoup(urlopen(f"https://www.basketball-reference.com/leagues/NBA_2021_advanced.html"), 'html.parser')

table = soup.find(id="advanced_stats")

data = []

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

    mpg = float(row_info["mp"]) / float(row_info["g"])

    if mpg > 30:
        data.append((name, float(row_info["bpm"])))

write_to_json("bpm_list_2021", data)
