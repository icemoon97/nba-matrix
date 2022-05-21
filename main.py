import json
import csv
import numpy as np

# takes a filename for a json with a ranking matrix and player list
# returns ranked list of players based on largest eigenvector ranking
def rank_from_json(filename, max_iter=100, tol=1e-10):
    with open(f"{filename}.json", "r") as openfile:
        data = json.load(openfile)

        matchup_matrix = data["matrix"]
        players = data["player_list"]

    #print(players)

    m = np.array(matchup_matrix)

    # power method to get largest eigenvector
    x_prev = np.ones(m.shape[0])
    for i in range(max_iter):
        x_new = m @ x_prev
        x_new = x_new / np.linalg.norm(x_new)
        
        l = np.transpose(x_new) @ (m @ x_new)  # lambda
        error = np.linalg.norm(m @ x_new - l * x_new)
        x_prev = x_new

        # exits loop if desired accuracy has been reached
        if error < tol:
            print(i)
            break

    # sorting based on eigenvector to get ranking
    r = x_prev.tolist()
    r = sorted(zip(r, range(len(r))), key=lambda x: x[0], reverse=True)

    player_ranking = list(map(lambda x: players[x[1]], r))
    return player_ranking

# making comparisons between multiple ranking matrices
with open("data/bpm_list_2021.json", "r") as openfile:
    data = json.load(openfile)

    top_20 = sorted(data, key=lambda x: x[1], reverse=True)[:25]
    #print(top_20)

comparison = {}
for i,player in enumerate(top_20):
    comparison[player[0]] = [i]

# file names of matrices to compare
to_compare = ["gmsc_30mpg_matrix", "gmsc_30mpg_matrix_adj", "gmsc_30mpg_matrix2", "gmsc_30mpg_matrix_adj2"]

for file in to_compare:
    ranking = rank_from_json("data/" + file)
    for i,name in enumerate(ranking):
        if name in comparison:
            comparison[name].append(i)

comparison_file_name = "gmsc_comp"

# saving results of comparison as csv
with open(f"comparisons/{comparison_file_name}.csv", "w", encoding="UTF8", newline="") as openfile:
    writer = csv.writer(openfile)

    writer.writerow(["Player", "BPM", "GameScore", "GameScore adj", "GameScore/wins", "GameScore/wins adj"])
    
    for name,arr in comparison.items():
        row = [name]
        row.extend([x + 1 for x in arr])
        writer.writerow(row)
