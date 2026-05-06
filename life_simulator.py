import numpy as np
import matplotlib.pyplot as plt
import time

def initialize_grid(size, initial_density=0.2):
    """Initializes the grid with random 'alive' cells."""
    grid = np.zeros((size, size), dtype=int)
    # Set initial cells randomly to 1 (alive)
    grid[np.random.rand(size, size) < initial_density] = 1
    return grid

def update_grid(current_grid):
    """
    Applies a simple cellular automaton rule set to mimic life (like Conway's Game of Life).
    This simulates growth, shrinking, and replication/destruction.
    """
    size = current_grid.shape[0]
    new_grid = np.copy(current_grid)
    
    for i in range(1, size - 1):
        for j in range(1, size - 1):
            # Count live neighbors
            live_neighbors = 0
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    live_neighbors += current_grid[i + di, j + dj]
            
            cell = current_grid[i, j]
            
            if cell == 1:  # Cell is alive
                if live_neighbors < 2 or live_neighbors > 3:
                    new_grid[i, j] = 0  # Dies (underpopulation or overpopulation)
            else:  # Cell is dead
                if live_neighbors == 3:
                    new_grid[i, j] = 1  # Becomes alive (reproduction)
                    
    return new_grid

def animate_life(size=100, generations=200):
    """
    Animates the cellular automaton simulation.
    """
    print("Starting Life Simulation...")
    grid = initialize_grid(size)
    
    fig, ax = plt.subplots()
    # Use a binary colormap for clear life/death representation
    im = ax.imshow(grid, cmap='binary', interpolation='nearest') 
    ax.set_title("Life Simulation (Cellular Automaton)")
    ax.set_xticks([])
    ax.set_yticks([])

    for gen in range(generations):
        # Update the grid state
        grid = update_grid(grid)
        
        # Update the plot data
        im.set_data(grid)
        
        # Redraw the canvas
        plt.pause(0.1) # Pause for 0.1 seconds to create animation effect
        
    print("Simulation finished.")
    plt.show() # Keep the final frame displayed

if __name__ == "__main__":
    # Configuration: Adjust these values to change the simulation behavior
    GRID_SIZE = 300  # Size of the grid (N x N)
    GENERATIONS = 3000 # How many steps to simulate
    
    # Note: This script requires numpy and matplotlib. 
    # If you encounter errors, please ensure 'pip install numpy matplotlib' has been run.
    animate_life(size=GRID_SIZE, generations=GENERATIONS)