import numpy as np
import pandas as pd
import itertools as it
from collections import Counter

def compute_coalitions(filepath):
    df = pd.read_csv(filepath, sep=';')
    print(df.columns)
    party_records = df[['Party', 'Seats ']].to_records()
    party_dict = {}
    for indx, party, seats in party_records:
        party_dict[party] = seats
    shapley_value(party_dict)

def shapley_value(party_dict):
    all_parties = list(party_dict.keys())
    total_seats = sum(party_dict.values())
    coalition_dict = {}
    for group_length in range(len(all_parties)):
        for permutation in it.permutations(all_parties, r=group_length):
            coalition_value = calcualte_permutation_value(
                party_dict, permutation, total_seats)
            coalition_dict[permutation] = coalition_value
    player_inputs = Counter()
    player_participations = Counter()
    for coalition in coalition_dict:
        if len(coalition) == 1:
            pass
        elif len(coalition) == 2:
            pass
        elif len(coalition) == 3:
            pass
        for i, player in enumerate(coalition):
            if i == 0:
                playerless_coalition = coalition[:i]
                playerless_value = 0
                if len(playerless_coalition) != 0:
                    playerless_coalition = coalition_dict[playerless_coalition]
                player_inputs[player] += (playerless_coalition -
                                          party_dict[player])
                player_participations[player] += 1

    for player in player_inputs:
        shapley_value = player_inputs[player] / player_participations[player]
        print(
            f"Player {player}" + \
                f"coalition input {shapley_value}"
        )


def calcualte_permutation_value(party_dict, permutation, total_seats):
    # calculate_permutation value
    seats = 0
    for coalition_member in permutation:
        seats += party_dict[coalition_member]
    if seats > 0.5 * total_seats:
        return 1
    else:
        return 0


filepath = '/Users/jakubmojsiejuk/Documents/agh/game-gym/PrisonersDilemma/ElectionsUK/resources/2015.csv'
compute_coalitions(filepath)