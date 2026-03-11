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

    # Add safe loops
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

    # Return the clean grid. We place S and E in a separate function now!
    return maze_grid, maze_width, maze_height

def place_random_start_exits(maze_grid, width, height):
    """Places 1 Start and 2-5 Exits in the absolute outer perimeter walls (y=0 and y=height-1)."""
    top_edge_candidates = []
    bottom_edge_candidates = []
    
    # 1. Scan the first inner row (y=1) to find valid open paths
    for x in range(1, width - 1):
        if maze_grid[1][x] == 0:
            top_edge_candidates.append(x) # Save the x-coordinate
            
    # 2. Scan the last inner row (y=height-2) to find valid open paths
    for x in range(1, width - 1):
        if maze_grid[height - 2][x] == 0:
            bottom_edge_candidates.append(x)

    # Fallback just in case
    if not top_edge_candidates: top_edge_candidates.append(1)
    if not bottom_edge_candidates: bottom_edge_candidates.append(width - 2)

    random.shuffle(top_edge_candidates)
    random.shuffle(bottom_edge_candidates)
    
    # 3. OVERWRITE THE TOP WALL: Place 1 Start on the absolute top boundary (y = 0)
    sx = top_edge_candidates.pop()
    maze_grid[0][sx] = 'S' 
    
    # 4. OVERWRITE THE BOTTOM WALL: Place 2 to 5 Exits on the absolute bottom boundary (y = height - 1)
    num_exits = random.randint(2, 5)
    num_exits = min(num_exits, len(bottom_edge_candidates)) 
    
    exits_placed = 0
    while exits_placed < num_exits and bottom_edge_candidates:
        ex = bottom_edge_candidates.pop()
        maze_grid[height - 1][ex] = 'E' 
        exits_placed += 1
        
    return maze_grid

def update_maze_dynamically(maze_grid, width, height):
    """Safely alters one wall without breaking the grid."""
    for _ in range(50):
        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)
        
        # NEW: Dynamically scan for targets to prevent boxing them in
        is_near_target = False
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if 0 <= y+dy < height and 0 <= x+dx < width:
                    if maze_grid[y+dy][x+dx] in ['S', 'E']:
                        is_near_target = True
                        break
            if is_near_target: break
            
        if is_near_target: 
            continue # Skip altering walls immediately adjacent to targets
            
        if maze_grid[y][x] not in ['S', 'E']:
            up_down = maze_grid[y-1][x] in [0, 'S', 'E'] and maze_grid[y+1][x] in [0, 'S', 'E']
            left_right = maze_grid[y][x-1] in [0, 'S', 'E'] and maze_grid[y][x+1] in [0, 'S', 'E']
            
            if maze_grid[y][x] == 1:
                if up_down != left_right:
                    maze_grid[y][x] = 0
                    return maze_grid, x, y, 0
            else:
                if up_down != left_right and random.random() < 0.2: 
                    maze_grid[y][x] = 1
                    return maze_grid, x, y, 1
    return maze_grid, -1, -1, -1