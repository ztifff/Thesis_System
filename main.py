from ui import MazeUI, COLOR_BFS, COLOR_DFS, COLOR_BFS_VISITED, COLOR_DFS_VISITED
import maze
import bfs
import dfs
import random
import time

class MazeController:
    def __init__(self):
        self.ui = MazeUI()
        self.maze_width = 31
        self.maze_height = 31
        self.maze_grid = []
        
        self.ui.btn_settings.configure(command=self.show_settings)
        self.ui.btn_run.configure(command=self.run_simulation)
        self.ui.btn_reset.configure(command=self.reset_simulation)
        
        self.ui.bind("<Configure>", self.on_window_resize)
        self._resize_timer = None
        self._animation_job = None
        
        self.is_paused = False 
        self.is_animating = False # Tracks if simulation is actively running
        
        self.generate_new_maze()
        
    def show_settings(self):
        self.ui.open_settings_modal(self.maze_width, self.maze_height, self.generate_new_maze)

    def generate_new_maze(self, width=31, height=31):
        self.maze_grid, self.maze_width, self.maze_height = maze.generate_maze(width, height)
        self.reset_simulation()

    def update_ui_maze(self):
        self.ui.draw_maze(self.maze_grid, self.maze_width, self.maze_height)

    def on_window_resize(self, event):
        # 1. Ignore events triggered by buttons/labels updating inside the window
        if event.widget != self.ui:
            return
            
        # 2. FIX: Prevent the canvas from wiping while the algorithms are searching!
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
        self.is_animating = False # Reset state
        self.update_ui_maze()
        self.ui.update_metrics("bfs", 0, 0, 0, 0, False)
        self.ui.update_metrics("dfs", 0, 0, 0, 0, False)

    def run_simulation(self):
        self.reset_simulation()
        
        # Lock the canvas so it doesn't wipe
        self.is_animating = True 
        
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
        self.shift_interval = random.uniform(1.0, 3.0) 
        
        self.animate_search()

    def unpause(self):
        self.is_paused = False

    def animate_search(self):
        if self.is_paused:
            self._animation_job = self.ui.after(10, self.animate_search)
            return

        # 1-3 Second Dynamic Shift Trigger
        if time.time() - self.last_shift_time >= self.shift_interval:
            self.maze_grid, cx, cy, val = maze.update_maze_dynamically(self.maze_grid, self.maze_width, self.maze_height)
            if cx != -1:
                self.ui.update_single_wall(cx, cy, val == 1)
            
            self.last_shift_time = time.time()
            self.shift_interval = random.uniform(1.0, 3.0)
            
            self.is_paused = True
            self.ui.after(600, self.unpause)
            self._animation_job = self.ui.after(10, self.animate_search)
            return

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
                
        # Unlock the canvas when finished
        self.is_animating = False

    def run(self):
        self.ui.mainloop()

if __name__ == "__main__":
    app = MazeController()
    app.run()