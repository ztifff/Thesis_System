from collections import deque
import time
import sys

def run_bfs_generator(grid, start, exits):
    rows = len(grid)
    cols = len(grid[0])
    queue = deque([(start, [start])]) 
    
    # FIX: Store the exact path taken to reach every visited node
    visited_paths = {start: [start]} 
    
    nodes_expanded = 0
    max_q_len = 1
    total_time_ms = 0.0
    last_curr = start
    last_path = [start]

    while True:
        if not queue:
            # WAITING LOGIC
            found_opening = False
            for vx, vy in list(visited_paths.keys()):
                for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                    nx, ny = vx + dx, vy + dy
                    if 0 <= ny < rows and 0 <= nx < cols:
                        if grid[ny][nx] in [0, 'E'] and (nx, ny) not in visited_paths:
                            # Resume using the correct historical path
                            new_path = visited_paths[(vx, vy)] + [(nx, ny)]
                            visited_paths[(nx, ny)] = new_path
                            queue.append(((nx, ny), new_path))
                            found_opening = True
            
            if not found_opening:
                yield last_curr, last_path, False, {"nodes": nodes_expanded, "time_ms": total_time_ms, "mem_kb": (max_q_len * sys.getsizeof(start)) / 1024.0}
                continue 

        t_start = time.perf_counter()
        current, path = queue.popleft()
        x, y = current
        
        if grid[y][x] == 1: continue
            
        last_curr, last_path = current, path
        nodes_expanded += 1
        
        if current in exits:
            t_end = time.perf_counter()
            total_time_ms += (t_end - t_start) * 1000
            yield current, path, True, {"nodes": nodes_expanded, "time_ms": total_time_ms, "mem_kb": (max_q_len * sys.getsizeof(current)) / 1024.0}
            return
            
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= ny < rows and 0 <= nx < cols:
                if grid[ny][nx] != 1 and (nx, ny) not in visited_paths:
                    new_path = path + [(nx, ny)]
                    visited_paths[(nx, ny)] = new_path
                    queue.append(((nx, ny), new_path))
                    if len(queue) > max_q_len: max_q_len = len(queue)
                        
        t_end = time.perf_counter()
        total_time_ms += (t_end - t_start) * 1000
        yield current, path, False, {"nodes": nodes_expanded, "time_ms": total_time_ms, "mem_kb": (max_q_len * sys.getsizeof(start)) / 1024.0}