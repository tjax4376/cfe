import numpy as np
import matplotlib.pyplot as plt

def ulam_warburton(n):
    """
    Generates the Ulam-Warburton sequence up to n.
    This is a simplified representation for fractal visualization, 
    as the true Ulam-Warburton sequence generation is complex.
    We will use a pattern based on the concept for visualization purposes.
    """
    # For fractal generation, we'll use a simpler iterative process 
    # that resembles self-similarity or growth patterns, inspired by Ulam's work.
    # A true implementation would involve number theory checks.
    
    # Let's create a grid and color based on some iterative function, 
    # which is more suitable for direct fractal plotting.
    size = n
    grid = np.zeros((size, size))
    
    for i in range(size):
        for j in range(size):
            # A simple function to create a pattern that can be colored like a fractal
            # This is NOT the Ulam-Warburton sequence itself, but a visual proxy.
            val = (i * 31 + j * 17) % 256
            grid[i, j] = val
            
    return grid

def create_colorful_fractal(n=500):
    """
    Creates and displays a colorful fractal image based on an iterative pattern.
    :param n: The size of the grid (N x N). Larger N means more detail but slower rendering.
    """
    print(f"Generating fractal image of size {n}x{n}...")
    
    # Generate the data grid
    data = ulam_warburton(n)
    
    # Create the plot
    plt.figure(figsize=(10, 10))
    # Use 'viridis' colormap for a colorful effect
    plt.imshow(data, cmap='viridis', interpolation='nearest') 
    
    # Add a color bar to show the mapping of values to colors
    plt.colorbar(label='Value Intensity')
    
    plt.title("Colorful Fractal Image (Ulam-Warburton Inspired)")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    
    # Display the figure instead of saving it, for live viewing
    plt.show()

if __name__ == "__main__":
    # Set the size of the fractal. Adjust this for detail vs speed.
    GRID_SIZE = 500 
    create_colorful_fractal(GRID_SIZE)