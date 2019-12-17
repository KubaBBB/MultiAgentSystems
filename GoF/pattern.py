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
    print('--- NEW ITERATION ---')
    turn_statistics = Counter()
    for pname, pattern in patterns_grid:
        R, C = count_pattern_on_grid(grid, pattern)
        if len(R) > 0 and (len(R) == len(C)):
            cumulative_statistics[pname] += len(R)
            turn_statistics[pname] += len(R)
        else:
            turn_statistics[pname] += 0    
    print(cumulative_statistics)
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
    grid = np.random.choice(vals, N * N, p=[0.2, 0.8]).reshape(N, N)

    fig, ax = plt.subplots()
    img = ax.imshow(grid, interpolation='nearest')

    update_interval = 50
    its = 50
    animate = False 
    if animate:
        ani = animation.FuncAnimation(fig,
                                    update,
                                    fargs=(img, grid, N, patterns_list),
                                    frames=its,
                                    repeat=False,
                                    interval=update_interval)
        plt.show()
    else:
        for i in range(its):
            update(i, None, grid, N, patterns_list)


    df = pd.DataFrame.from_dict(running_statistics)

    df.to_csv(f'GOL-statistics-{its}_N_{N}.csv')


# run_game()
def plot_statistics(filename):
    df = pd.read_csv(filename,  index_col=0)
    fig, ax = plt.subplots()


    window = 10
    
    barplot_vals, barplot_ticks = [], []
    for pattern in df.columns:
        barplot_vals.append(df[pattern].sum())
        barplot_ticks.append(pattern)
        print(len(df[pattern]), pattern)
        data = df[pattern].rolling(window=window).std()
        ax.plot(data, label=pattern)

    ax.set_title("Running statistics of patters over the iterations")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Pattern occurences")
    plt.legend()
    plt.grid()
    # plt.show()
    svn = filename.replace('.csv', '')
    plt.savefig(f'./GOF/{svn}_std_{window}.png')
    
    print(barplot_ticks)
    fig2, ax2 = plt.subplots()
    x = np.arange(len(barplot_ticks))
    ax2.bar(x, barplot_vals)
    ax2.set_xticks(x, barplot_ticks)
    plt.show()
        
plot_statistics('GOL-statistics-50_N_500.csv')