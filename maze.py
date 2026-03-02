import random
import sys

sys.setrecursionlimit(10000)

def generate_maze(width=31, height=31):
    maze_width = width if width % 2 != 0 else width + 1
    maze_height = height if height % 2 != 0 else height + 1
    
    maze_grid = [[1 for _ in range(maze_width)] for _ in range(maze_height)]

    def carve(cx, cy):
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 1 <= nx < maze_width - 1 and 1 <= ny < maze_height - 1 and maze_grid[ny][nx] == 1:
                maze_grid[cy + dy // 2][cx + dx // 2] = 0
                maze_grid[ny][nx] = 0
                carve(nx, ny)

    maze_grid[1][1] = 0
    carve(1, 1)

    # Make it tight: Add exactly 5 safe loops instead of randomly blasting walls
    loops_added = 0
    attempts = 0
    while loops_added < 5 and attempts < 200:
        attempts += 1
        x = random.randint(1, maze_width - 2)
        y = random.randint(1, maze_height - 2)
        if maze_grid[y][x] == 1:
            up_down = maze_grid[y-1][x] == 0 and maze_grid[y+1][x] == 0
            left_right = maze_grid[y][x-1] == 0 and maze_grid[y][x+1] == 0
            if up_down != left_right: 
                maze_grid[y][x] = 0
                loops_added += 1

    maze_grid[1][1] = 'S'

    num_exits = random.randint(2, 5)
    exits_placed = 0
    while exits_placed < num_exits:
        ex_x = random.choice(range(1, maze_width-1, 2))
        ex_y = maze_height - 2
        if maze_grid[ex_y][ex_x] == 0:
            maze_grid[maze_height-1][ex_x] = 'E'
            maze_grid[maze_height-2][ex_x] = 0 # Guarantee path above exit
            exits_placed += 1

    return maze_grid, maze_width, maze_height

def update_maze_dynamically(maze_grid, width, height):
    """Safely alters one wall without breaking the grid."""
    for _ in range(50):
        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)
        
        # Protect Start and Exits
        if (x <= 2 and y <= 2) or y >= height - 3: continue 
            
        if maze_grid[y][x] not in ['S', 'E']:
            up_down = maze_grid[y-1][x] in [0, 'S', 'E'] and maze_grid[y+1][x] in [0, 'S', 'E']
            left_right = maze_grid[y][x-1] in [0, 'S', 'E'] and maze_grid[y][x+1] in [0, 'S', 'E']
            
            if maze_grid[y][x] == 1:
                if up_down != left_right:
                    maze_grid[y][x] = 0
                    return maze_grid, x, y, 0
            else:
                if up_down != left_right and random.random() < 0.2: # Low chance to block path
                    maze_grid[y][x] = 1
                    return maze_grid, x, y, 1
    return maze_grid, -1, -1, -1