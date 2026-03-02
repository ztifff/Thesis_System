import customtkinter as ctk
import tkinter as tk

# Figma-matched Color Palette
BG_MAIN = "#1e1e24"
BG_SECONDARY = "#2a2b36"
COLOR_BFS = "#2dbd82"
COLOR_DFS = "#9d72ff"
COLOR_RESET = "#ef4444"
COLOR_BATCH = "#3b82f6"
TEXT_LIGHT = "#ffffff"

# Animation Colors
COLOR_BFS_VISITED = "#1e5e45" # Dark green for searching
COLOR_DFS_VISITED = "#4a3382" # Dark purple for searching

ctk.set_appearance_mode("Dark")

class MazeUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Performance Evaluation of BFS and DFS Algorithms")
        self.geometry("1400x850")
        self.configure(fg_color=BG_MAIN)
        self.minsize(1000, 600)

        self.setup_ui()

    def setup_ui(self):
        # --- HEADER ---
        self.header_frame = ctk.CTkFrame(self, height=60, fg_color=BG_SECONDARY, corner_radius=0)
        self.header_frame.pack(fill="x", side="top")
        
        self.btn_settings = ctk.CTkButton(self.header_frame, text="⚙", width=40, height=40, 
                                          fg_color="transparent", hover_color="#3f3f4e", 
                                          font=ctk.CTkFont(size=20))
        self.btn_settings.pack(side="left", padx=15, pady=10)

        self.title_label = ctk.CTkLabel(self.header_frame, text="Performance Evaluation of BFS and DFS Algorithms in Multi-Exit Dynamic Maze Environments", 
                                        font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_LIGHT)
        self.title_label.pack(side="left", padx=10, pady=10)

        # --- MAIN CONTENT BODY ---
        self.body_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.body_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # --- LEFT PANEL (Stats) ---
        self.left_panel = ctk.CTkFrame(self.body_frame, width=250, fg_color="transparent")
        self.left_panel.pack(side="left", fill="y", padx=(0, 20))
        
        # BFS Stats Card
        self.bfs_card = ctk.CTkFrame(self.left_panel, fg_color=BG_SECONDARY, corner_radius=10)
        self.bfs_card.pack(fill="x", pady=(0, 20))
        
        self.bfs_status_lbl = ctk.CTkLabel(self.bfs_card, text="BFS STATUS: Idle", fg_color=COLOR_BFS, corner_radius=6, text_color="white", font=ctk.CTkFont(weight="bold"))
        self.bfs_status_lbl.pack(fill="x", padx=10, pady=10)
        
        self.bfs_nodes_lbl = ctk.CTkLabel(self.bfs_card, text="Nodes: 0", text_color=TEXT_LIGHT, font=ctk.CTkFont(weight="bold"))
        self.bfs_nodes_lbl.pack(anchor="w", padx=15, pady=(0,2))
        self.bfs_time_lbl = ctk.CTkLabel(self.bfs_card, text="Time: 0.0ms", text_color=TEXT_LIGHT, font=ctk.CTkFont(weight="bold"))
        self.bfs_time_lbl.pack(anchor="w", padx=15, pady=(0,2))
        self.bfs_path_lbl = ctk.CTkLabel(self.bfs_card, text="Path: 0", text_color=TEXT_LIGHT, font=ctk.CTkFont(weight="bold"))
        self.bfs_path_lbl.pack(anchor="w", padx=15, pady=(0,2))
        self.bfs_mem_lbl = ctk.CTkLabel(self.bfs_card, text="Memory: 0KB", text_color=TEXT_LIGHT, font=ctk.CTkFont(weight="bold"))
        self.bfs_mem_lbl.pack(anchor="w", padx=15, pady=(0, 15))

        # DFS Stats Card
        self.dfs_card = ctk.CTkFrame(self.left_panel, fg_color=BG_SECONDARY, corner_radius=10)
        self.dfs_card.pack(fill="x")
        
        self.dfs_status_lbl = ctk.CTkLabel(self.dfs_card, text="DFS STATUS: Idle", fg_color=COLOR_DFS, corner_radius=6, text_color="white", font=ctk.CTkFont(weight="bold"))
        self.dfs_status_lbl.pack(fill="x", padx=10, pady=10)
        
        self.dfs_nodes_lbl = ctk.CTkLabel(self.dfs_card, text="Nodes: 0", text_color=TEXT_LIGHT, font=ctk.CTkFont(weight="bold"))
        self.dfs_nodes_lbl.pack(anchor="w", padx=15, pady=(0,2))
        self.dfs_time_lbl = ctk.CTkLabel(self.dfs_card, text="Time: 0.0ms", text_color=TEXT_LIGHT, font=ctk.CTkFont(weight="bold"))
        self.dfs_time_lbl.pack(anchor="w", padx=15, pady=(0,2))
        self.dfs_path_lbl = ctk.CTkLabel(self.dfs_card, text="Path: 0", text_color=TEXT_LIGHT, font=ctk.CTkFont(weight="bold"))
        self.dfs_path_lbl.pack(anchor="w", padx=15, pady=(0,2))
        self.dfs_mem_lbl = ctk.CTkLabel(self.dfs_card, text="Memory: 0KB", text_color=TEXT_LIGHT, font=ctk.CTkFont(weight="bold"))
        self.dfs_mem_lbl.pack(anchor="w", padx=15, pady=(0, 15))

        # --- RIGHT PANEL (Mazes & Controls) ---
        self.right_panel = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        self.right_panel.pack(side="left", fill="both", expand=True)

        self.maze_container = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.maze_container.pack(fill="both", expand=True)
        self.maze_container.grid_columnconfigure((0, 1), weight=1)
        self.maze_container.grid_rowconfigure(1, weight=1)

        # BFS Canvas
        ctk.CTkLabel(self.maze_container, text="BFS Visualization", fg_color=COLOR_BFS, 
                     corner_radius=15, text_color="white", width=160, height=28).grid(row=0, column=0, pady=(0, 10))
        self.bfs_canvas_wrapper = ctk.CTkFrame(self.maze_container, fg_color="white", corner_radius=10)
        self.bfs_canvas_wrapper.grid(row=1, column=0, padx=10, sticky="nsew")
        self.bfs_canvas = tk.Canvas(self.bfs_canvas_wrapper, bg="white", highlightthickness=0)
        self.bfs_canvas.pack(fill="both", expand=True, padx=5, pady=5)

        # DFS Canvas
        ctk.CTkLabel(self.maze_container, text="DFS Visualization", fg_color=COLOR_DFS, 
                     corner_radius=15, text_color="white", width=160, height=28).grid(row=0, column=1, pady=(0, 10))
        self.dfs_canvas_wrapper = ctk.CTkFrame(self.maze_container, fg_color="white", corner_radius=10)
        self.dfs_canvas_wrapper.grid(row=1, column=1, padx=10, sticky="nsew")
        self.dfs_canvas = tk.Canvas(self.dfs_canvas_wrapper, bg="white", highlightthickness=0)
        self.dfs_canvas.pack(fill="both", expand=True, padx=5, pady=5)

        # --- BOTTOM PANEL (Controls) ---
        self.controls_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent", height=50)
        self.controls_frame.pack(fill="x", pady=(20, 0))

        self.btn_reset = ctk.CTkButton(self.controls_frame, text="↻ Reset Simulations", fg_color=COLOR_RESET, hover_color="#c83333", font=ctk.CTkFont(weight="bold"))
        self.btn_reset.pack(side="left", padx=(10, 5))
        
        self.btn_run = ctk.CTkButton(self.controls_frame, text="▶ Run Simulation", fg_color=COLOR_BFS, hover_color="#229666", font=ctk.CTkFont(weight="bold"))
        self.btn_run.pack(side="left", padx=5)
        
        self.btn_batch = ctk.CTkButton(self.controls_frame, text="▶ Run Step-by-Step", fg_color=COLOR_BATCH, hover_color="#2b61c2", font=ctk.CTkFont(weight="bold"))
        self.btn_batch.pack(side="left", padx=5)

    def draw_maze(self, maze_grid, width, height):
        self.update_idletasks()
        
        canvas_w = self.bfs_canvas.winfo_width()
        canvas_h = self.bfs_canvas.winfo_height()

        if canvas_w < 10 or canvas_h < 10:
            return

        self.cell_size = min(canvas_w / width, canvas_h / height)
        self.offset_x = (canvas_w - (self.cell_size * width)) / 2
        self.offset_y = (canvas_h - (self.cell_size * height)) / 2

        self.bfs_canvas.delete("all")
        self.dfs_canvas.delete("all")

        for y in range(height):
            for x in range(width):
                val = maze_grid[y][x]
                color = "#000000" if val == 1 else "#ffffff"
                self.color_cell("bfs", x, y, color)
                self.color_cell("dfs", x, y, color)

                padding = self.cell_size * 0.2
                x1 = self.offset_x + (x * self.cell_size)
                y1 = self.offset_y + (y * self.cell_size)
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                if val == 'S':
                    self.bfs_canvas.create_oval(x1+padding, y1+padding, x2-padding, y2-padding, fill=COLOR_BFS, outline="")
                    self.dfs_canvas.create_oval(x1+padding, y1+padding, x2-padding, y2-padding, fill=COLOR_DFS, outline="")
                elif val == 'E':
                    self.bfs_canvas.create_oval(x1+padding, y1+padding, x2-padding, y2-padding, fill=COLOR_RESET, outline="")
                    self.dfs_canvas.create_oval(x1+padding, y1+padding, x2-padding, y2-padding, fill=COLOR_RESET, outline="")

    def color_cell(self, canvas_type, x, y, color):
        """Draws a single colored square. Used for fast animations."""
        x1 = self.offset_x + (x * self.cell_size)
        y1 = self.offset_y + (y * self.cell_size)
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        
        canvas = self.bfs_canvas if canvas_type == "bfs" else self.dfs_canvas
        # We removed canvas.tag_lower(rect) here so the animation draws ON TOP of the white paths
        canvas.create_rectangle(x1, y1, x2+1, y2+1, fill=color, outline=color)

    def update_metrics(self, algo, nodes, time_ms, path_len, mem_kb, is_running=False):
        """Updates the left panel text."""
        status_text = f"{algo.upper()} STATUS: " + ("Running" if is_running else ("Finished" if nodes > 0 else "Idle"))
        if algo == "bfs":
            self.bfs_status_lbl.configure(text=status_text)
            self.bfs_nodes_lbl.configure(text=f"Nodes: {nodes}")
            self.bfs_time_lbl.configure(text=f"Time: {time_ms:.2f}ms")
            self.bfs_path_lbl.configure(text=f"Path: {path_len}")
            self.bfs_mem_lbl.configure(text=f"Memory: {mem_kb:.2f}KB")
        else:
            self.dfs_status_lbl.configure(text=status_text)
            self.dfs_nodes_lbl.configure(text=f"Nodes: {nodes}")
            self.dfs_time_lbl.configure(text=f"Time: {time_ms:.2f}ms")
            self.dfs_path_lbl.configure(text=f"Path: {path_len}")
            self.dfs_mem_lbl.configure(text=f"Memory: {mem_kb:.2f}KB")
    
    def update_single_wall(self, x, y, is_wall):
        """Dynamically draws a single wall or path without clearing the canvas."""
        x1 = self.offset_x + (x * self.cell_size)
        y1 = self.offset_y + (y * self.cell_size)
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        
        color = "#000000" if is_wall else "#ffffff"
        
        # Draw over both canvases
        self.bfs_canvas.create_rectangle(x1, y1, x2+1, y2+1, fill=color, outline=color)
        self.dfs_canvas.create_rectangle(x1, y1, x2+1, y2+1, fill=color, outline=color)

    def open_settings_modal(self, current_w, current_h, on_generate_callback):
        modal = ctk.CTkToplevel(self)
        modal.title("Menu")
        modal.geometry("400x370") 
        modal.configure(fg_color=BG_SECONDARY)
        modal.attributes("-topmost", True)
        
        modal.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 200
        y = self.winfo_y() + (self.winfo_height() // 2) - 185
        modal.geometry(f"+{x}+{y}")

        ctk.CTkLabel(modal, text="Rows (10-100):", text_color=TEXT_LIGHT).pack(pady=(20, 0), anchor="w", padx=40)
        rows_entry = ctk.CTkEntry(modal, fg_color=BG_MAIN, border_width=0)
        rows_entry.pack(pady=5, padx=40, fill="x")
        rows_entry.insert(0, str(current_h))

        ctk.CTkLabel(modal, text="Columns (10-100):", text_color=TEXT_LIGHT).pack(pady=(10, 0), anchor="w", padx=40)
        cols_entry = ctk.CTkEntry(modal, fg_color=BG_MAIN, border_width=0)
        cols_entry.pack(pady=5, padx=40, fill="x")
        cols_entry.insert(0, str(current_w))

        # Error Label for Validation
        error_label = ctk.CTkLabel(modal, text="", text_color=COLOR_RESET, font=ctk.CTkFont(size=12))
        error_label.pack(pady=(5, 0))

        btn_frame = ctk.CTkFrame(modal, fg_color="transparent")
        btn_frame.pack(pady=10)

        def apply_and_generate():
            try:
                r = int(rows_entry.get())
                c = int(cols_entry.get())
                
                # Validation 10-100
                if 10 <= r <= 100 and 10 <= c <= 100:
                    on_generate_callback(c, r)  
                    modal.destroy()
                else:
                    error_label.configure(text="Values must be between 10 and 100.")
            except ValueError:
                error_label.configure(text="Please enter valid integers.")

        ctk.CTkButton(btn_frame, text="Generate Maze", fg_color=COLOR_BFS, command=apply_and_generate).pack(side="left", padx=5)
        ctk.CTkButton(modal, text="Result History", fg_color=COLOR_BATCH).pack(pady=10, padx=40, fill="x")