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
    def __init__(self, strategy, mixed=False):
        self.mixed = mixed
        self.counter = 0
        self.strategy = strategy
        self.history = []
        self.payoffs = []

        self.revenge_counter = 0

    def choose_strategy(self):
        strategies = [
            'tft', '2tft', 'random', 'always_defect', 'always_cooperate',
            'tft2'
        ]
        if self.mixed:
            if self.counter < 8 and self.counter != 0:
                self.counter += 1
            else:
                self.counter = 0
                self.strategy = random.choice(strategies)
        else:
            return

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
                penultimous_step = history_other[-2]
                if last_player_step == penultimous_step == 0:
                    return 0
                else:
                    return 1
            except IndexError:
                return 1
        elif self.strategy == '2tft':
            # replicate last with forgetting
            if step == 0:
                return 1
            last_player_step = history_other[-1]
            try:
                penultimous_step = history_other[-2]
                if last_player_step == penultimous_step == 0:
                    # other betrayed twice
                    # revenge is twice
                    self.revenge_counter = 1
                    return 0
                else:
                    if self.revenge_counter:
                        self.revenge_counter -= 1
                        return 0
                    else:
                        return 1
            except IndexError:
                # second move is also always 1
                return 1
        elif self.strategy == 'always_defect':
            return 1
        elif self.strategy == 'always_cooperate':
            return 0


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


def run_simulation(steps, epochs=1, plot=True):
    playerA = Player('random', True)
    playerB = Player('2tft', True)
    for epoch in range(epochs):
        for i in range(steps):
            if playerA.mixed:
                playerA.choose_strategy()
            if playerB.mixed:
                playerB.choose_strategy()
            moveA = playerA.make_move(i, playerB.history)
            moveB = playerB.make_move(i, playerA.history)
            scoreA, scoreB = evaluate_players(moveA, moveB)
            playerA.history.append(moveA)
            playerB.history.append(moveB)

            playerA.payoffs.append(scoreA)
            playerB.payoffs.append(scoreB)
            # print(np.mean(playerA.payoffs), np.mean(playerB.payoffs), np.std(
            #         playerA.payoffs), np.std(playerB.payoffs))
    text = '\n'.join([
        f'mean payoffA: {np.mean(playerA.payoffs)}',
        f'mean payoffB: {np.mean(playerB.payoffs)}',
        f'std payoffA: {np.std(playerA.payoffs)}',
        f'std payoffA: {np.std(playerB.payoffs)}'
    ])
    print(f"Text {text}")
    # place a text box in upper left in axes coords

    assert len(playerA.history) == len(playerB.history)
    assert len(playerA.payoffs) == len(playerB.payoffs)

    if plot:
        fig, ax = plt.subplots()

        ax.plot(np.cumsum(playerA.payoffs), '.', label='A payoff')
        ax.plot(np.cumsum(playerB.payoffs), '.', label='B payoff')
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

        ax.text(0.95,
                0.01,
                text,
                verticalalignment='bottom',
                horizontalalignment='right',
                transform=ax.transAxes,
                bbox=props,
                fontsize=15)
        ax.legend()
        plt.xlabel("Iteration")
        plt.ylabel("Cumulative payoff")
        plt.title(f"Cumsum of A: {playerA.strategy} B: {playerB.strategy}")
        plt.show()
    return np.mean(playerA.payoffs), np.mean(playerB.payoffs), np.std(
        playerA.payoffs), np.std(playerB.payoffs)


if __name__ == "__main__":
    t_pAmean, t_pBmean, t_pAstd, t_pBstd = 0, 0, 0, 0
    num_runs = 1
    plot = False if num_runs > 1 else True
    for i in range(num_runs):
        pAmean, pBmean, pAstd, pBstd = run_simulation(100, plot=plot)
        t_pAmean += pAmean
        t_pBmean += pBmean
        t_pAstd += pAstd
        t_pBstd += pBstd

    print(f"Player A: {t_pAmean/num_runs}, {t_pAstd/num_runs}")
    print(f"Player B: {t_pBmean/num_runs}, {t_pBstd/num_runs}")
