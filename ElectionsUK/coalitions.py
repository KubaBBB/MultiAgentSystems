import numpy as np
import pandas as pd
import itertools as it
from collections import Counter, OrderedDict


def compute_coalitions(filepath):
    df = pd.read_csv(filepath, sep=';')
    party_records = df[['Party', 'Seats']].to_records()
    party_dict = {}
    for indx, party, seats in party_records:
        if seats:
            party_dict[party] = seats
    shapley_value(party_dict)


def shapley_value(party_dict):
    all_parties = list(party_dict.keys())
    total_seats = sum(party_dict.values())
    coalition_dict = {}
    winning_seats = 0.5 * total_seats
    print("Calculating Shapley value")
    combinations = 0
    for group_length in range(1, len(all_parties)+1):
        print(f"Calculating the groups of lengths {group_length}")
        for permutation in it.permutations(all_parties, r=group_length):
            coalition_value = calcualte_permutation_value(
                party_dict, permutation, winning_seats)
            coalition_dict[permutation] = coalition_value
            combinations += 1
    print(f"Possible combinations: {combinations}")
    player_inputs = Counter()
    print("Calculating player's inputs")
    for coalition in coalition_dict:
        # print(f"Value for coalition: {coalition}, {coalition_dict[coalition]}")
        current_coalition_value = coalition_dict[coalition]
        """
        Add contribution for each player in the reduced coalition
        eg.
        P1, P2, P3 = 5
        P1 = 3
        add P1 += 3 
        P1, P2 = 4 
        add P2 += (4 - 3)
        P1, P3, P3
        add P3 += (5 - 4)
        """
        for i in reversed(range(len(coalition))):
            if i == 0:
                player_inputs[coalition[i]] += coalition_dict[(coalition[i],)]
                break
            # we take player i reduced coalition
            reduced_coalition = coalition[:i]
            reduced_coalition_value = coalition_dict[reduced_coalition]
            player_inputs[coalition[i]] += (current_coalition_value - reduced_coalition_value)
            current_coalition_value = reduced_coalition_value
    # get all winning_coalitions
    print(player_inputs)
    winning_coals = [coal for coal, val in coalition_dict.items() if val]
    winning_coals = [
        tuple(coal) for coal in set(map(frozenset, winning_coals))
    ]
    print(f"There are: {len(winning_coals)} winning coalitions")
    for coal in winning_coals:
        print(
            f"\tCoalition: {', '.join(coal)} has " +\
                f"{sum([party_dict[party] for party in coal])} votes.")

    for player in player_inputs:
        shapley_value = player_inputs[player] / len(coalition_dict)
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
        return 1.0
    return 0.0


# filepath = '/Users/jakubmojsiejuk/Documents/agh/game-gym/PrisonersDilemma/ElectionsUK/resources/2015.csv'
filepath = '/Users/jakubmojsiejuk/Documents/agh/game-gym/PrisonersDilemma/ElectionsUK/resources/eu2014.csv'
# filepath = '/Users/jakubmojsiejuk/Documents/agh/game-gym/PrisonersDilemma/ElectionsUK/resources/test.csv'
compute_coalitions(filepath)