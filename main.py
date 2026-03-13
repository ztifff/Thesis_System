from ui import MazeUI, COLOR_BFS, COLOR_DFS, COLOR_BFS_VISITED, COLOR_DFS_VISITED
from results import ResultsManager
import maze
import bfs
import dfs
import random
import time
import copy  # <-- NEW: Used to take a perfect snapshot of the 2D array
from collections import deque

class MazeController:
    def __init__(self):
        self.ui = MazeUI()
        self.results_manager = ResultsManager(self.ui)
        
        self.maze_width = 31
        self.maze_height = 31
        self.maze_grid = []
        self.original_maze_grid = []  # <-- NEW: Will hold the untouched pristine maze
        
        self.ui.btn_settings.configure(command=self.show_settings)
        self.ui.btn_run.configure(command=self.run_simulation)
        self.ui.btn_reset.configure(command=self.reset_simulation)
        
        # BIND THE NEW STEP BUTTON
        self.ui.btn_step.configure(command=self.run_step_by_step) 
        
        self.ui.bind("<Configure>", self.on_window_resize)
        self._resize_timer = None
        self._animation_job = None
        
        self.is_paused = False 
        self.is_animating = False 
        self.simulation_initialized = False # Tracks if we've started a run
        self.auto_play = False # Tracks if we are in looping mode
        
        self.generate_new_maze()
        
    def show_settings(self):
        self.ui.open_settings_modal(self.maze_width, self.maze_height, self.generate_new_maze, self.results_manager.show_history_list)

    def generate_new_maze(self, width=31, height=31):
        # 1. Generate the raw walls/paths ONLY
        self.maze_grid, self.maze_width, self.maze_height = maze.generate_maze(width, height)
        
        # 2. Save a deepcopy of the BLANK maze
        self.base_maze_grid = copy.deepcopy(self.maze_grid) 
        
        self.reset_simulation()

    def update_ui_maze(self):
        self.ui.draw_maze(self.maze_grid, self.maze_width, self.maze_height)

    def on_window_resize(self, event):
        if event.widget != self.ui:
            return
        if getattr(self, 'is_animating', False):
            return
        if self._resize_timer is not None:
            self.ui.after_cancel(self._resize_timer)
        self._resize_timer = self.ui.after(50, self.update_ui_maze)
        
    def get_start_and_exits(self):
        start = None
        exits = []
        for y in range(self.maze_height):
            for x in range(self.maze_width):
                if self.maze_grid[y][x] == 'S': start = (x, y)
                elif self.maze_grid[y][x] == 'E': exits.append((x, y))
        return start, set(exits)

    def reset_simulation(self, randomize=True):
        if self._animation_job:
            self.ui.after_cancel(self._animation_job)
        self.is_paused = False
        self.is_animating = False 
        self.simulation_initialized = False 
        self.auto_play = False
        self.bfs_done = False
        self.dfs_done = False
        
        if getattr(self, 'base_maze_grid', None):
            if randomize:
                # Normal Reset: Load blank map and randomize new targets
                self.maze_grid = copy.deepcopy(self.base_maze_grid)
                self.maze_grid = maze.place_random_start_exits(self.maze_grid, self.maze_width, self.maze_height)
                # Snapshot this exact layout in case the user wants to rerun it later!
                self.saved_target_grid = copy.deepcopy(self.maze_grid) 
            else:
                # Rerun Reset: Just restore the grid with the exact same targets
                self.maze_grid = copy.deepcopy(self.saved_target_grid)
            
        self.update_ui_maze()
        self.ui.update_metrics("bfs", 0, 0, 0, 0, False)
        self.ui.update_metrics("dfs", 0, 0, 0, 0, False)
    
    def rerun_exact_maze(self):
        """Restores the exact same layout but permanently closes the exits that were just used!"""
        if self._animation_job:
            self.ui.after_cancel(self._animation_job)
        self.is_paused = False
        self.is_animating = False 
        self.simulation_initialized = False 
        self.auto_play = False
        
        # ---> FIX: Changed to the correct variable name 'saved_target_grid' <---
        if getattr(self, 'saved_target_grid', None) is not None:
            
            # 1. Gather the winning paths
            paths_to_check = []
            if getattr(self, 'bfs_final_path', []): 
                paths_to_check.append(self.bfs_final_path)
            if getattr(self, 'dfs_final_path', []): 
                paths_to_check.append(self.dfs_final_path)
            
            # 2. BRUTE FORCE SEALING
            for path in paths_to_check:
                if path: # Safety check to ensure the path isn't empty
                    ex, ey = path[-1] # The absolute last step is mathematically the exit door
                    
                    # Blindly smash that exact coordinate into a solid black wall
                    self.saved_target_grid[ey][ex] = 1 
                    print(f"DEBUG: FORCE SEALED exit at x:{ex}, y:{ey}")
            
            # 3. Load the newly updated snapshot with the permanently sealed doors
            self.maze_grid = copy.deepcopy(self.saved_target_grid)
            
        self.bfs_done = False
        self.dfs_done = False
            
        self.update_ui_maze()
        self.ui.update_metrics("bfs", 0, 0, 0, 0, False)
        self.ui.update_metrics("dfs", 0, 0, 0, 0, False)
        
        # Instantly run the next race!
        self.run_simulation()

    def init_simulation_state(self):
        """Initializes the generators once per run, regardless of play mode."""
        start, exits = self.get_start_and_exits()
        
        self.active_exits = exits # <--- NEW: Store exits for the trap
        self.triggered_exits = set()

        self.bfs_gen = bfs.run_bfs_generator(self.maze_grid, start, exits)
        self.dfs_gen = dfs.run_dfs_generator(self.maze_grid, start, exits)

        self.ui.update_metrics("bfs", 0, 0, 0, 0, True)
        self.ui.update_metrics("dfs", 0, 0, 0, 0, True)

        self.bfs_done = False
        self.dfs_done = False
        self.bfs_final_path = []
        self.dfs_final_path = []
        
        # ---> NEW: Sets to remember exactly where each algorithm has stepped <---
        self.bfs_explored = set()
        self.dfs_explored = set()
        
        self.last_shift_time = time.time()
        self.shift_interval = random.uniform(1.0, 2.0) 
        
        self.simulation_initialized = True
        self.is_animating = True

    def run_simulation(self):
        """Auto-plays the simulation."""
        
        # ---> NEW: Guard Clause to prevent button spamming <---
        if getattr(self, 'auto_play', False) and not (getattr(self, 'bfs_done', False) and getattr(self, 'dfs_done', False)):
            return # The system is currently running, ignore the click!

        # If the simulation is already finished, reset the maze automatically
        if getattr(self, 'bfs_done', False) and getattr(self, 'dfs_done', False):
            self.reset_simulation()
            
        if not self.simulation_initialized:
            self.init_simulation_state()
            
        self.auto_play = True
        self.animate_search()

    def run_step_by_step(self):
        """Advances the simulation by exactly one node click-by-click."""
        # ---> NEW: If the simulation is already finished, reset the maze automatically
        if getattr(self, 'bfs_done', False) and getattr(self, 'dfs_done', False):
            self.reset_simulation()
            
        if not self.simulation_initialized:
            self.init_simulation_state()
            
        self.auto_play = False # Stop the auto-player if it was running
            
        # 1. Manual Step Dynamic Wall Check
        if time.time() - self.last_shift_time >= self.shift_interval:
            self.maze_grid, cx, cy, val = maze.update_maze_dynamically(self.maze_grid, self.maze_width, self.maze_height)
            if cx != -1:
                self.ui.update_single_wall(cx, cy, val == 1)
            self.last_shift_time = time.time()
            self.shift_interval = random.uniform(1.0, 2.0)

        # 2. Advance exactly one node
        self.process_algorithm_steps()

        # 3. Check for finish
        if self.bfs_done and self.dfs_done:
            self.draw_final_paths()
    def unpause(self):
        self.is_paused = False

    def process_algorithm_steps(self):
        active_heads = [] # <--- NEW
        
        if not self.bfs_done:
            try:
                b_curr, b_path, self.bfs_done, b_metrics = next(self.bfs_gen)
                x, y = b_curr
                self.bfs_explored.add((x, y))
                active_heads.append((x, y)) # <--- NEW: Track BFS position
                
                if self.maze_grid[y][x] not in ['S', 'E', 1, 'B']: # <-- Added 'B'
                    self.ui.color_cell("bfs", x, y, COLOR_BFS_VISITED)
                self.ui.update_metrics("bfs", b_metrics["nodes"], b_metrics["time_ms"], len(b_path), b_metrics["mem_kb"], not self.bfs_done)
                if self.bfs_done: self.bfs_final_path = b_path
            except StopIteration:
                self.bfs_done = True

        if not self.dfs_done:
            try:
                d_curr, d_path, self.dfs_done, d_metrics = next(self.dfs_gen)
                x, y = d_curr
                self.dfs_explored.add((x, y))
                active_heads.append((x, y)) # <--- NEW: Track DFS position
                
                if self.maze_grid[y][x] not in ['S', 'E', 1, 'B']: # <-- Added 'B'
                    self.ui.color_cell("dfs", x, y, COLOR_DFS_VISITED)
                self.ui.update_metrics("dfs", d_metrics["nodes"], d_metrics["time_ms"], len(d_path), d_metrics["mem_kb"], not self.dfs_done)
                if self.dfs_done: self.dfs_final_path = d_path
            except StopIteration:
                self.dfs_done = True

        # ---> NEW: TRIGGER THE 50% PROXIMITY TRAP! <---
        if active_heads and hasattr(self, 'active_exits'):
            self.maze_grid, blocked = maze.proximity_exit_blocker(
                self.maze_grid, active_heads, self.active_exits, self.triggered_exits
            )
            # If any traps triggered, instantly draw the Red Box!
            for bx, by in blocked:
                self.ui.color_cell("bfs", bx, by, "#ff0000")
                self.ui.color_cell("dfs", bx, by, "#ff0000")

    def animate_search(self):
        """The looping method for auto-play."""
        if not self.auto_play:
            return # Kills the loop if the user clicked Step-by-Step

        if self.is_paused:
            self._animation_job = self.ui.after(10, self.animate_search)
            return

        if time.time() - self.last_shift_time >= self.shift_interval:
            self.maze_grid, cx, cy, val = maze.update_maze_dynamically(self.maze_grid, self.maze_width, self.maze_height)
            if cx != -1:
                self.ui.update_single_wall(cx, cy, val == 1)
            
            self.last_shift_time = time.time()
            self.shift_interval = random.uniform(1.0, 2.0)
            
            self.is_paused = True
            self.ui.after(600, self.unpause)
            self._animation_job = self.ui.after(10, self.animate_search)
            return

        self.process_algorithm_steps()

        if not self.bfs_done or not self.dfs_done:
            self._animation_job = self.ui.after(10, self.animate_search)
        else:
            self.draw_final_paths()

    def repair_final_path(self, path, explored_memory):
        """Validates if a path was broken. Repairs it ONLY using previously explored nodes."""
        if not path: return []
        
        is_broken = False
        for x, y in path:
            if self.maze_grid[y][x] == 1:
                is_broken = True
                break
                
        if not is_broken:
            return path 
            
        start = path[0]
        end = path[-1]
        
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            curr, p = queue.popleft()
            if curr == end:
                return p 
                
            x, y = curr
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= ny < self.maze_height and 0 <= nx < self.maze_width:
                    # ---> NEW: Must not be a wall, not visited, AND MUST be in explored memory (or the exit/start) <---
                    if self.maze_grid[ny][nx] != 1 and (nx, ny) not in visited:
                        if (nx, ny) in explored_memory or (nx, ny) == end or (nx, ny) == start:
                            visited.add((nx, ny))
                            queue.append(((nx, ny), p + [(nx, ny)]))
                        
        return path # Fallback to the original broken path if no known bypass exists

    def draw_final_paths(self):
        # ---> NEW: Pass the explored memory to the repair tool <---
        self.bfs_final_path = self.repair_final_path(self.bfs_final_path, self.bfs_explored)
        self.dfs_final_path = self.repair_final_path(self.dfs_final_path, self.dfs_explored)

        self.ui.bfs_path_lbl.configure(text=f"Path: {len(self.bfs_final_path)}")
        self.ui.dfs_path_lbl.configure(text=f"Path: {len(self.dfs_final_path)}")

        for x, y in self.bfs_final_path:
            if self.maze_grid[y][x] not in ['S', 1]: 
                self.ui.color_cell("bfs", x, y, COLOR_BFS)
                
        for x, y in self.dfs_final_path:
            if self.maze_grid[y][x] not in ['S', 1]: 
                self.ui.color_cell("dfs", x, y, COLOR_DFS)
                
        self.is_animating = False

        bfs_final_data = {
            "nodes": int(self.ui.bfs_nodes_lbl.cget("text").split(": ")[1]),
            "time_ms": float(self.ui.bfs_time_lbl.cget("text").split(": ")[1].replace("ms", "")),
            "path": len(self.bfs_final_path),
            "mem_kb": float(self.ui.bfs_mem_lbl.cget("text").split(": ")[1].replace("KB", ""))
        }
        
        dfs_final_data = {
            "nodes": int(self.ui.dfs_nodes_lbl.cget("text").split(": ")[1]),
            "time_ms": float(self.ui.dfs_time_lbl.cget("text").split(": ")[1].replace("ms", "")),
            "path": len(self.dfs_final_path),
            "mem_kb": float(self.ui.dfs_mem_lbl.cget("text").split(": ")[1].replace("KB", ""))
        }

        self.results_manager.show_summary(bfs_final_data, dfs_final_data, self.rerun_exact_maze) # <--- UPDATED

    def run(self):
        self.ui.mainloop()

if __name__ == "__main__":
    app = MazeController()
    app.run()