import numpy as np
import pandas as pd
import itertools as it
from collections import Counter, OrderedDict
import seaborn as sns
import matplotlib.pyplot as plt


def compute_coalitions(filepath):
    """
    Reads the csv for elections and
    computes the coalitions
    """
    df = pd.read_csv(filepath, sep=';')
    party_records = df[['Party', 'Seats']].to_records()
    party_dict = {}
    for indx, party, seats in party_records:
        if seats:
            party_dict[party] = seats
    shapley_value(party_dict, df, filepath)


def shapley_value(party_dict: dict, org_df=None, filepath=None):
    """
    Calculates the player contributions aka Shapley
    values.
    :param party_dict
        dictionary of parties and ther seits
    :returns (produces)
        dictionary of player combinations and 
        values for each combination aka 
        each coalition and value 
        d = {(P1, P2, P3): 2, (P1): 1, ....}
    """
    all_parties = list(party_dict.keys())
    total_seats = sum(party_dict.values())
    coalition_dict = {}
    winning_seats = 0.5 * total_seats + 1
    print(f"Calculating Shapley value, winning seats: {winning_seats}")
    combinations = 0
    for group_length in range(1, len(all_parties) + 1):
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
                # just a single player in the coalition, so just add him
                player_inputs[coalition[i]] += coalition_dict[(coalition[i], )]
                break
            # we take player i reduced coalition
            reduced_coalition = coalition[:
                                          i]  # if i == 1, then is a single player
            reduced_coalition_value = coalition_dict[reduced_coalition]
            player_inputs[coalition[i]] += (current_coalition_value -
                                            reduced_coalition_value)
            current_coalition_value = reduced_coalition_value
    # get all winning_coalitions
    print(player_inputs)
    winning_coals = [coal for coal, val in coalition_dict.items() if val]
    winning_coals = [
        tuple(coal) for coal in set(map(frozenset, winning_coals))
    ]

    # count player coalitions
    player_coalitions = Counter()
    for coalition in coalition_dict:
        for player in player_inputs:
            if player in coalition:
                player_coalitions[player] += 1

    print(f"There are: {len(winning_coals)} winning coalitions")
    data = {'Coalition': [], 'Seats': []}
    for coal in winning_coals:
        coalition_seats = sum([party_dict[party] for party in coal])
        coal_name = ', '.join(coal)
        data['Coalition'].append(coal_name)
        data['Seats'].append(coalition_seats)
        print(
            f"\tCoalition: {coal_name} has " +\
                f"{coalition_seats} seats.")

    org_df['Shapley'] = 0.0
    for player in player_inputs:
        shapley_value = player_inputs[player] / player_coalitions[player]
        print(
            f"Player {player}: " + \
                f"coalition input {shapley_value}"
        )
        org_df.loc[org_df['Party'] == player, 'Shapley'] = shapley_value
    df = pd.DataFrame.from_dict(data=data)
    df.to_csv('coalition_output.csv', index=False)
    savename = filepath.replace('.csv', '')
    org_df.to_csv(f'{savename}_shapley_modified.csv', index=False)


def calcualte_permutation_value(party_dict: dict, permutation, winning_seats):
    """
    Calculates the winning condition for each coalition
    :param party_dict
        dictionary of parties and their seats
    :param permutation 
        a given permutation of players
    :param winning seats
        number of seats that ensures the win
    """
    # calculate_permutation value
    seats = 0
    for coalition_member in permutation:
        seats += party_dict[coalition_member]
    if seats > winning_seats:
        return 1.0
    return 0.0


def statitstics_shapley(filenames):
    df = pd.DataFrame()
    for filename in filenames:
        tmp = pd.read_csv(filename)
        tmp['year'] = filename.replace('pl', '').replace('.csv', '')
        df = pd.concat([df, tmp], sort=True)

    # histogram
    mean = np.mean(df['Shapley'])
    std = np.std(df['Shapley'])
    ax = sns.distplot(df['Shapley'],
                    #   bins=25,
                      rug=True,
                      rug_kws={"color": "b"},
                      kde_kws={
                          "color": "r",
                          "lw": 3,
                          "linestyle": '--',
                          "label": "Predicted distribution"
                      },
                      hist_kws={
                          "histtype": "step",
                          "linewidth": 3,
                          "alpha": 1,
                          "color": "b"
                      })
    ax.axvline(x=mean, label=f'Mean at = {np.around(mean,2)}', c='c', ls='--')
    ax.axvline(x=mean + std,
               label=f'Mean + std at {np.around(mean+std,2)}',
               c='m',
               ls='-.')
    ax.axvline(x=mean - std,
               label=f'Mean - std at {np.around(mean-std,2)}',
               c='m',
               ls='-.')
    ax.set_xlim([0.0, 0.9])
    ax.legend()
    ax.set_ylabel("Count of values")
    ax.set_title("Polish elections 2007-2011- distribution of Shapley values")
    plt.savefig("Polish.png")
    plt.show()


filepath = './Elections/resources/eu2019.csv'
filepath = './Elections/resources/eu2014.csv'
filepath = './Elections/resources/eu2009.csv'
filepath = './Elections/resources/pl2007.csv'
# filepath = './Elections/resources/pl2011.csv'


# filepath = './Elections/resources/test.csv'
# compute_coalitions(filepath)
filenames = [
    './Elections/resources/eu2009_shapley_modified.csv',
    './Elections/resources/eu2014_shapley_modified.csv',
    './Elections/resources/eu2019_shapley_modified.csv'
]

filenames = [
    './Elections/resources/pl2007_shapley_modified.csv',
    './Elections/resources/pl2011_shapley_modified.csv'
]
statitstics_shapley(filenames)
