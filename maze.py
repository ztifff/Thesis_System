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
    """Places 1 Start on Top, and 2-5 spread-out Exits on Left, Right, or Bottom edges."""
    top_candidates = []
    exit_candidates = []
    
    # 1. Scan Top inner row for Start (y = 1)
    for x in range(1, width - 1):
        if maze_grid[1][x] == 0:
            top_candidates.append(x)
            
    # 2. Scan Bottom, Left, and Right inner rows for Exits
    # Bottom Edge
    for x in range(1, width - 1):
        if maze_grid[height - 2][x] == 0:
            exit_candidates.append((x, height - 1))
    # Left Edge
    for y in range(1, height - 1):
        if maze_grid[y][1] == 0:
            exit_candidates.append((0, y))
    # Right Edge
    for y in range(1, height - 1):
        if maze_grid[y][width - 2] == 0:
            exit_candidates.append((width - 1, y))

    # Fallbacks just in case
    if not top_candidates: top_candidates.append(1)
    if not exit_candidates: exit_candidates.append((width - 2, height - 1))

    random.shuffle(top_candidates)
    random.shuffle(exit_candidates)
    
    # 3. OVERWRITE TOP WALL: Place 1 Start (y = 0)
    sx = top_candidates.pop()
    maze_grid[0][sx] = 'S'
    start_pos = (sx, 0) # <--- NEW: Remember where the Start node is
    
    # 4. OVERWRITE SIDES/BOTTOM: Place 2 to 5 Exits
    num_exits = random.randint(2, 5)
    num_exits = min(num_exits, len(exit_candidates))
    
    # Require exits to be at least a quarter of the maze away from each other (and from the start)
    min_dist = max(5, max(width, height) // 4) 
    
    placed_exits = []
    
    # First Pass: Try to place exits that respect all distance constraints
    for ex, ey in exit_candidates:
        if len(placed_exits) >= num_exits:
            break
            
        # ---> NEW: Ensure the exit is far away from the Start node <---
        dist_to_start = abs(ex - start_pos[0]) + abs(ey - start_pos[1])
        if dist_to_start < min_dist:
            continue # Reject this spot! It's too close to the Start.
            
        # Check distance against all currently placed exits
        too_close = False
        for px, py in placed_exits:
            manhattan_dist = abs(ex - px) + abs(ey - py)
            if manhattan_dist < min_dist:
                too_close = True
                break
                
        if not too_close:
            maze_grid[ey][ex] = 'E'
            placed_exits.append((ex, ey))
            
    # Second Pass (Fallback): If the maze is too small and we couldn't place enough exits safely
    if len(placed_exits) < num_exits:
        for ex, ey in exit_candidates:
            if len(placed_exits) >= num_exits:
                break
            if (ex, ey) not in placed_exits:
                # Still enforce an absolute minimum buffer of 3 blocks from the Start
                if abs(ex - start_pos[0]) + abs(ey - start_pos[1]) >= 3:
                    maze_grid[ey][ex] = 'E'
                    placed_exits.append((ex, ey))
                
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

def proximity_exit_blocker(maze_grid, active_heads, active_exits, triggered_exits):
    """
    Checks if an algorithm is within 3 blocks of an exit.
    If so, rolls a 50% chance to permanently block that exit with a Red Box ('B').
    Will NOT block the exit if it is the very last one available!
    """
    blocked_this_turn = []
    
    # ---> NEW: Count exactly how many open exits are currently on the board <---
    open_exits_count = sum(1 for ex, ey in active_exits if maze_grid[ey][ex] == 'E')
    
    for head_x, head_y in active_heads:
        for ex, ey in active_exits:
            # If it's still an open exit and we haven't rolled for it yet
            if (ex, ey) not in triggered_exits and maze_grid[ey][ex] == 'E':
                
                # Check Manhattan distance
                dist = abs(head_x - ex) + abs(head_y - ey)
                
                if dist <= 3: 
                    triggered_exits.add((ex, ey)) # Mark it so we only roll once!
                    
                    # ---> NEW: Only drop the trap if there is more than 1 exit remaining! <---
                    if open_exits_count > 1 and random.random() < 0.50: 
                        maze_grid[ey][ex] = 'B' 
                        blocked_this_turn.append((ex, ey))
                        open_exits_count -= 1 # Lower the count in case multiple traps fire at once
                        
    return maze_grid, blocked_this_turn