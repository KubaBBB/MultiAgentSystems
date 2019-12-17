import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
import re
import cv2
from collections import Counter, defaultdict
import pandas as pd 
import seaborn as sns 

ON = 255
OFF = 0
vals = [ON, OFF]
cumulative_statistics = Counter()
running_statistics = defaultdict(list)

horizontal_stencil = np.array([[0, 0, 0], [255, 255, 255], [0, 0, 0]])
vertical_stencil = horizontal_stencil.T
block = np.array([[255, 255], [255, 255]])
tub = np.array([[0, 255, 0], [255, 0, 255], [0, 255, 0]])
beehive1 = np.array([
    [0, 255, 255, 0],
    [255, 0, 0, 255],
    [0, 255, 255, 0]
])
beehive2 = beehive1.T
beacon1 = np.array([[255, 255, 0, 0], [255, 0, 0, 0], [0, 0, 0, 255],
                    [0, 0, 255, 255]])
beacon2 = np.array([[255, 255, 0, 0], [255, 255, 0, 0], [0, 0, 255, 255],
                    [0, 0, 255, 255]])
toad1 = np.array([[0, 255, 255, 255], [255, 255, 255, 0]])
toad2 = np.array([[0, 0, 255, 0], [255, 0, 0, 255], [255, 0, 0, 255],
                  [0, 255, 0, 0]])


patterns_list = [('blinker', horizontal_stencil), ('blinker', vertical_stencil),
                    ('beehive', beehive1), ('beehive', beehive2),
                    ('tub', tub), ('block', block), ('beacon', beacon1),
                    ('beacon', beacon2), ('toad', toad1), ('toad', toad2)]
patterns_list = [(name, np.pad(pat, 1)) for name, pat in patterns_list]

def count_pattern_on_grid(grid, pattern):
    M = cv2.matchTemplate(grid.astype('uint8'), pattern.astype('uint8'),
                          cv2.TM_SQDIFF)
    R, C = np.where(M == 0)
    return R, C


def update(frameNum, img, grid, N, patterns_grid):
    # print('--- NEW ITERATION ---')
    turn_statistics = Counter()
    for pname, pattern in patterns_grid:
        R, C = count_pattern_on_grid(grid, pattern)
        if len(R) > 0 and (len(R) == len(C)):
            cumulative_statistics[pname] += len(R)
            turn_statistics[pname] += len(R)
        else:
            turn_statistics[pname] += 0    
    # print(cumulative_statistics)
    for turn_pattern in turn_statistics:
        running_statistics[turn_pattern].append(turn_statistics[turn_pattern])
    # copy grid since we require 8 neighbors
    # for calculation and we go line by line
    newGrid = grid.copy()
    for i in range(N):
        for j in range(N):
            # compute 8-neghbor sum
            # using toroidal boundary conditions - x and y wrap around
            # so that the simulaton takes place on a toroidal surface.
            total = int(
                (grid[i,
                      (j - 1) % N] + grid[i,
                                          (j + 1) % N] + grid[(i - 1) % N, j] +
                 grid[(i + 1) % N, j] + grid[(i - 1) % N,
                                             (j - 1) % N] + grid[(i - 1) % N,
                                                                 (j + 1) % N] +
                 grid[(i + 1) % N, (j - 1) % N] + grid[(i + 1) % N,
                                                       (j + 1) % N]) / 255)

            # apply Conway's rules
            if grid[i, j] == ON:
                if (total < 2) or (total > 3):
                    newGrid[i, j] = OFF
            else:
                if total == 3:
                    newGrid[i, j] = ON

    # update data
    if img is not None:
        img.set_data(newGrid)
    grid[:] = newGrid[:]
    return img,


def run_game():
    N = 500
    p1 = 0.8
    grid = np.random.choice(vals, N * N, p=[p1, 1.0-p1]).reshape(N, N)

    fig, ax = plt.subplots()

    update_interval = 50
    its = 50
    animate = False 
    if animate:
        img = ax.imshow(grid, interpolation='nearest')
        ani = animation.FuncAnimation(fig,
                                    update,
                                    fargs=(img, grid, N, patterns_list),
                                    frames=its,
                                    repeat=False,
                                    interval=update_interval)
        plt.show()
    else:
        M = 1
        for random_inits in range(M):
            grid = np.random.choice(vals, N * N, p=[p1, 1.0-p1]).reshape(N, N)
            for i in range(its):
                update(i, None, grid, N, patterns_list)
        for pat in cumulative_statistics:
            print(pat, cumulative_statistics[pat]/M)

    df = pd.DataFrame.from_dict(running_statistics)
    df.to_csv(f'GOL-statistics-{its}_N_{N}_p_{p1}_acc.csv')
    plot_statistics(f'GOL-statistics-{its}_N_{N}_p_{p1}_acc.csv')


def plot_statistics(filename, draw_barplot=False):
    df = pd.read_csv(filename,  index_col=0)
    window = 10
    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()

    barplot_vals, bmenas, bstds, barplot_ticks = [], [], [], []
    for pattern in df.columns:
        barplot_vals.append(df[pattern].sum())
        barplot_ticks.append(pattern)
        bmenas.append(np.mean(df[pattern]))
        bstds.append(np.std(df[pattern]))
        print(len(df[pattern]), pattern)
        data_mean = df[pattern].rolling(window=window).mean()
        data_std = df[pattern].rolling(window=window).std()

        ax1.plot(data_mean, label=pattern)
        ax2.plot(data_std, label=pattern)

    ax1.set_title(f"Running mean window: {window}")
    ax1.set_xlabel("Iteration")
    ax1.set_ylabel("Pattern occurences")
    plt.legend()
    plt.grid()
    svn = filename.replace('.csv', '')
    fig1.savefig(f'./GOF/{svn}_mean_{window}.png')

    ax2.set_title(f"Running std window: {window}")
    ax2.set_xlabel("Iteration")
    ax2.set_ylabel("Pattern occurences")
    plt.legend()
    plt.grid()
    svn = filename.replace('.csv', '')
    fig2.savefig(f'./GOF/{svn}_std_{window}.png')

    if draw_barplot:
        fig3, ax3 = plt.subplots()
        x = np.arange(len(barplot_ticks))
        ax3.bar(x, barplot_vals, yerr=bstds)
        ax3.set_title("Cumulative sum of patterns")
        plt.xticks(x, barplot_ticks)
        fig3.savefig(f'./GOF/{svn}_barplot.png')

    plt.show()
run_game()

# plot_statistics(df)