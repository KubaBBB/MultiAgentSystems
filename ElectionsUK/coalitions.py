import numpy as np
import pandas as pd
import itertools as it
from collections import Counter


def compute_coalitions(filepath):
    df = pd.read_csv(filepath, sep=';')
    party_records = df[['Party', 'Seats']].to_records()
    party_dict = {}
    for indx, party, seats in party_records:
        if seats:
            party_dict[party] = seats
    shapley_value(party_dict)
    # print(party_dict)


def shapley_value(party_dict):
    all_parties = list(party_dict.keys())
    total_seats = sum(party_dict.values())
    coalition_dict = {}
    winning_seats = 0.5 * total_seats
    print("Calculating Shapley value")
    combinations = 0
    for group_length in range(1, len(all_parties)):
        print(f"Calculating the groups of lengths {group_length}")
        for permutation in it.permutations(all_parties, r=group_length):
            coalition_value = calcualte_permutation_value(
                party_dict, permutation, winning_seats)
            coalition_dict[permutation] = coalition_value
            combinations += 1
    print(f"Possible combinations: {combinations}")
    # print(coalition_dict)
    player_inputs = Counter()
    player_participations = Counter()
    print("Calculating player's inputs")
    for coalition in coalition_dict:
        for i, player in enumerate(coalition):
            playerless_coalition = coalition[:i]
            if len(playerless_coalition) != 0:
                playerless_value = coalition_dict[playerless_coalition]
            else:
                playerless_value = 0
            player_inputs[player] += (party_dict[player] - playerless_value)
            player_participations[player] += 1

    for player in player_inputs:
        shapley_value = player_inputs[player] / player_participations[player]
        print(
            f"Player {player}: " + \
                f"coalition input {shapley_value}"
        )


def calcualte_permutation_value(party_dict, permutation, winning_seats):
    # calculate_permutation value
    seats = 0
    for coalition_member in permutation:
        seats += party_dict[coalition_member]
        if seats > winning_seats:
            return 1
        else:
            return 0


filepath = '/Users/jakubmojsiejuk/Documents/agh/game-gym/PrisonersDilemma/ElectionsUK/resources/2017.csv'
filepath = '/Users/jakubmojsiejuk/Documents/agh/game-gym/PrisonersDilemma/ElectionsUK/resources/eu2014.csv'
compute_coalitions(filepath)