from ui import MazeUI, COLOR_BFS, COLOR_DFS, COLOR_BFS_VISITED, COLOR_DFS_VISITED
from results import ResultsManager
import maze
import bfs
import dfs
import random
import time
import copy  # <-- NEW: Used to take a perfect snapshot of the 2D array

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

    def reset_simulation(self):
        if self._animation_job:
            self.ui.after_cancel(self._animation_job)
        self.is_paused = False
        self.is_animating = False 
        self.simulation_initialized = False 
        self.auto_play = False
        
        # 3. Every time we reset, load the blank maze...
        if getattr(self, 'base_maze_grid', None):
            self.maze_grid = copy.deepcopy(self.base_maze_grid)
            # 4. ... and throw NEW random targets on it!
            self.maze_grid = maze.place_random_start_exits(self.maze_grid, self.maze_width, self.maze_height)
            
        self.update_ui_maze()
        self.ui.update_metrics("bfs", 0, 0, 0, 0, False)
        self.ui.update_metrics("dfs", 0, 0, 0, 0, False)

    def init_simulation_state(self):
        """Initializes the generators once per run, regardless of play mode."""
        start, exits = self.get_start_and_exits()
        
        self.bfs_gen = bfs.run_bfs_generator(self.maze_grid, start, exits)
        self.dfs_gen = dfs.run_dfs_generator(self.maze_grid, start, exits)

        self.ui.update_metrics("bfs", 0, 0, 0, 0, True)
        self.ui.update_metrics("dfs", 0, 0, 0, 0, True)

        self.bfs_done = False
        self.dfs_done = False
        self.bfs_final_path = []
        self.dfs_final_path = []
        
        self.last_shift_time = time.time()
        self.shift_interval = random.uniform(1.0, 2.0) 
        
        self.simulation_initialized = True
        self.is_animating = True

    def run_simulation(self):
        """Auto-plays the simulation."""
        if not self.simulation_initialized:
            self.init_simulation_state()
            
        self.auto_play = True
        self.animate_search()

    def run_step_by_step(self):
        """Advances the simulation by exactly one node click-by-click."""
        if not self.simulation_initialized:
            self.init_simulation_state()
            
        self.auto_play = False # Stop the auto-player if it was running
        
        if self.bfs_done and self.dfs_done:
            return # Don't do anything if they both already finished
            
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
        """A helper method to advance generators by one step."""
        if not self.bfs_done:
            try:
                b_curr, b_path, self.bfs_done, b_metrics = next(self.bfs_gen)
                x, y = b_curr
                if self.maze_grid[y][x] not in ['S', 'E', 1]: 
                    self.ui.color_cell("bfs", x, y, COLOR_BFS_VISITED)
                self.ui.update_metrics("bfs", b_metrics["nodes"], b_metrics["time_ms"], len(b_path), b_metrics["mem_kb"], not self.bfs_done)
                if self.bfs_done: self.bfs_final_path = b_path
            except StopIteration:
                self.bfs_done = True

        if not self.dfs_done:
            try:
                d_curr, d_path, self.dfs_done, d_metrics = next(self.dfs_gen)
                x, y = d_curr
                if self.maze_grid[y][x] not in ['S', 'E', 1]:
                    self.ui.color_cell("dfs", x, y, COLOR_DFS_VISITED)
                self.ui.update_metrics("dfs", d_metrics["nodes"], d_metrics["time_ms"], len(d_path), d_metrics["mem_kb"], not self.dfs_done)
                if self.dfs_done: self.dfs_final_path = d_path
            except StopIteration:
                self.dfs_done = True

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

    def draw_final_paths(self):
        for x, y in self.bfs_final_path:
            if self.maze_grid[y][x] not in ['S', 'E', 1]:
                self.ui.color_cell("bfs", x, y, COLOR_BFS)
                
        for x, y in self.dfs_final_path:
            if self.maze_grid[y][x] not in ['S', 'E', 1]:
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

        self.results_manager.show_summary(bfs_final_data, dfs_final_data)

    def run(self):
        self.ui.mainloop()

if __name__ == "__main__":
    app = MazeController()
    app.run()