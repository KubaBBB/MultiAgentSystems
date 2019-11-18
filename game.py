import random
import numpy as np 
import matplotlib.pyplot as plt
"""
1 - silent
0 - betray 

GAME MATRIX
both betray -- both -2
both silent -- both -1
one betrays, one silent = 0/ -3


"""


class Player:
    def __init__(self, strategy):
        self.strategy = strategy
        self.history = []
        self.payoffs = []

    def make_move(self, step, history_other):
        if self.strategy == 'random':
            return int(random.random() > 0.5)
        elif self.strategy == 'tft':
            # replicate last
            if step == 0:
                return 1
            else:
                last_player_step = history_other[-1]
                return last_player_step

        elif self.strategy == 'tft2':
            # replicate last with forgetting
            if step == 0:
                return 1
            last_player_step = history_other[-1]
            try:
                penultimous_step = history_other[-1]
                if history_other[-1] == penultimous_step == 0:
                    return 0
                else:
                    return 1
            except IndexError:
                return last_player_step


def evaluate_players(player_a_move, player_b_move):
    if not (player_a_move + player_b_move):
        # both betray
        return -2, -2
    if (player_a_move + player_b_move) == 2:
        # both silient
        return -1, -1
    if player_a_move and not player_b_move:
        # player a goes silent
        return -3, 0
    else:
        return 0, -3


def run_simulation(steps):
    playerA = Player('random')
    playerB = Player('tft2')
    for i in range(steps):
        moveA = playerA.make_move(i, playerB.history)
        moveB = playerB.make_move(i, playerA.history)
        scoreA, scoreB = evaluate_players(moveA, moveB)
        playerA.history.append(moveA)
        playerB.history.append(moveB)

        playerA.payoffs.append(scoreA)
        playerB.payoffs.append(scoreB)

    assert len(playerA.history) == len(playerB.history)
    assert len(playerA.payoffs) == len(playerB.payoffs)

    plt.plot(np.cumsum(playerA.payoffs), '.', label='A payoff')
    plt.plot(np.cumsum(playerB.payoffs), '.', label='B payoff')
    plt.legend()
    plt.xlabel("Iteration")
    plt.ylabel("Cumulative payoff")
    plt.title(f"Cumsum of A: {playerA.strategy} B: {playerB.strategy}")
    plt.show()


if __name__ == "__main__":
    run_simulation(100)