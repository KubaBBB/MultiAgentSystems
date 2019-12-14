# Python code to implement Conway's Game Of Life 
import argparse 
import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib.animation as animation 
import os
from time import sleep

filename='input1.txt'

# setting up the values for the grid 
ON = 255
OFF = 0
vals = [ON, OFF] 

def fill_from_file(i, j, grid, filename):
	with open(os.path.join(os.path.dirname(__file__), 'resources', filename)) as f:
		content = f.readlines()
	# you may also want to remove whitespace characters like `\n` at the end of each line
	content = [x.strip() for x in content]
	for index in range(content.__len__()):
		sep = content[index].index(',')
		values = [content[index][0:sep], content[index][sep+1:content[index].__len__()]]
		grid[int(values[0])+i, int(values[1])+i] = 255

def read_pattern(pattern):
	with open(os.path.join(os.path.dirname(__file__), 'resources', 'patterns', f'{pattern}.txt')) as f:
		content = f.readlines()
	values = []
	max_width, max_height = 0, 0
	content = [x.strip() for x in content]
	for index in range(content.__len__()):
		sep = content[index].index(',')
		x = int(content[index][0:sep])
		y = int(content[index][sep+1:content[index].__len__()])
		if x > max_width:
			max_width = x
		if y > max_height:
			max_height = y
		values.append([x,y])
	pattern = np.zeros(shape=(max_width+2, max_height+2), dtype=int)
	for coord in values:
		pattern[coord[0], coord[1]] = 255
	return pattern

def count_pattern_on_grid(grid, pattern):
	t = 0

def random_grid(N):

	"""returns a grid of NxN random values"""
	return np.random.choice(vals, N*N, p=[0.2, 0.8]).reshape(N, N) 

def add_glider(i, j, grid):

	"""adds a glider with top left cell at (i, j)"""
	glider = np.array([[0, 0, 255], 
					[255, 0, 255], 
					[0, 255, 255]]) 
	grid[i:i+3, j:j+3] = glider 

def add_gosper_glider_gun(i, j, grid):

	"""adds a Gosper Glider Gun with top left 
	cell at (i, j)"""

	gun = np.zeros(11*38).reshape(11, 38)

	gun[5][1] = gun[5][2] = 255
	gun[6][1] = gun[6][2] = 255

	gun[3][13] = gun[3][14] = 255
	gun[4][12] = gun[4][16] = 255
	gun[5][11] = gun[5][17] = 255
	gun[6][11] = gun[6][15] = gun[6][17] = gun[6][18] = 255
	gun[7][11] = gun[7][17] = 255
	gun[8][12] = gun[8][16] = 255
	gun[9][13] = gun[9][14] = 255

	gun[1][25] = 255
	gun[2][23] = gun[2][25] = 255
	gun[3][21] = gun[3][22] = 255
	gun[4][21] = gun[4][22] = 255
	gun[5][21] = gun[5][22] = 255
	gun[6][23] = gun[6][25] = 255
	gun[7][25] = 255

	gun[3][35] = gun[3][36] = 255
	gun[4][35] = gun[4][36] = 255

	grid[i:i+11, j:j+38] = gun 

def update(frameNum, img, grid, N): 

	# copy grid since we require 8 neighbors 
	# for calculation and we go line by line 
	newGrid = grid.copy()
	#sleep(2)
	for i in range(N): 
		for j in range(N): 

			# compute 8-neghbor sum 
			# using toroidal boundary conditions - x and y wrap around 
			# so that the simulaton takes place on a toroidal surface. 
			total = int((grid[i, (j-1)%N] + grid[i, (j+1)%N] +
						grid[(i-1)%N, j] + grid[(i+1)%N, j] +
						grid[(i-1)%N, (j-1)%N] + grid[(i-1)%N, (j+1)%N] +
						grid[(i+1)%N, (j-1)%N] + grid[(i+1)%N, (j+1)%N])/255) 

			# apply Conway's rules 
			if grid[i, j] == ON: 
				if (total < 2) or (total > 3): 
					newGrid[i, j] = OFF 
			else: 
				if total == 3: 
					newGrid[i, j] = ON 

	# update data 
	img.set_data(newGrid) 
	grid[:] = newGrid[:] 
	return img, 

# main() function 
def main(): 

	# Command line args are in sys.argv[1], sys.argv[2] .. 
	# sys.argv[0] is the script name itself and can be ignored 
	# parse arguments 
	parser = argparse.ArgumentParser(description="Runs Conway's Game of Life simulation.") 

	# add arguments 
	parser.add_argument('--grid-size', dest='N', required=False) 
	parser.add_argument('--mov-file', dest='movfile', required=False) 
	parser.add_argument('--interval', dest='interval', required=False) 
	parser.add_argument('--glider', action='store_true', required=False) 
	parser.add_argument('--gosper', action='store_true', required=False)
	parser.add_argument('--file', action='store_true', required=False)

	args = parser.parse_args() 
	patterns = ['block', 'tub', 'blinker_1', 'blinker_2']
	patternsGrid = []
	for pattern in patterns:
		patternsGrid.append(read_pattern(pattern))
	# set grid size 
	N = 100
	if args.N and int(args.N) > 8: 
		N = int(args.N) 
		
	# set animation update interval 
	updateInterval = 50
	if args.interval: 
		updateInterval = int(args.interval) 

	# declare grid 
	grid = np.array([]) 

	# check if "glider" demo flag is specified 
	if args.glider: 
		grid = np.zeros(N*N).reshape(N, N) 
		add_glider(1, 1, grid)
	elif args.gosper: 
		grid = np.zeros(N*N).reshape(N, N) 
		add_gosper_glider_gun(10, 10, grid)
	elif args.file:
		grid = np.zeros(N*N).reshape(N,N)
		fill_from_file(10, 10, grid, filename)
	else: # populate grid with random on/off - 
			# more off than on 
		grid = random_grid(N)

	# set up animation 
	fig, ax = plt.subplots() 
	img = ax.imshow(grid, interpolation='nearest') 
	ani = animation.FuncAnimation(fig, update, fargs=(img, grid, N, ), 
								frames = 10, 
								interval=updateInterval, 
								save_count=50) 

	# # of frames? 
	# set output file 
	if args.movfile: 
		ani.save(args.movfile, fps=30, extra_args=['-vcodec', 'libx264']) 

	plt.show() 

# call main 
if __name__ == '__main__': 
	main() 
