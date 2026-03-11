import customtkinter as ctk
import json
import os
from datetime import datetime

# Color Palette
BG_MAIN = "#1e1e24"
BG_SECONDARY = "#2a2b36"
COLOR_BFS = "#2dbd82"
COLOR_DFS = "#9d72ff"
COLOR_BATCH = "#3b82f6"
COLOR_RESET = "#ef4444"
TEXT_LIGHT = "#ffffff"
TEXT_MUTED = "#a1a1aa"
COLOR_RECOMMENDATION = "#facc15" # A nice yellow/gold for the recommendation text and "glow"

class ResultsManager:
    def __init__(self, parent_ui):
        self.parent = parent_ui
        self.history_file = "simulation_history.json"
        self.history = self.load_history()

    def load_history(self):
        """Loads saved results from a JSON file."""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []

    def save_history(self):
        """Saves current history to a JSON file."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=4)

    def center_modal(self, modal, width, height):
        modal.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (width // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (height // 2)
        modal.geometry(f"{width}x{height}+{x}+{y}")

    def _get_recommendation(self, bfs_data, dfs_data):
        """Analyzes the metrics and returns a tuple: (recommendation_text, winner_name)"""
        bfs_path = bfs_data['path']
        dfs_path = dfs_data['path']
        bfs_time = bfs_data['time_ms']
        dfs_time = dfs_data['time_ms']

        # Logic 1: Shortest Path wins
        if bfs_path < dfs_path:
            return f"💡 Recommendation: BFS is optimal for this maze. It successfully found a significantly shorter route to an exit ({bfs_path} steps vs DFS's {dfs_path} steps), demonstrating its theoretical pathfinding superiority.", "BFS"
        elif dfs_path < bfs_path:
            return f"💡 Recommendation: DFS is recommended for this maze. It managed to find a shorter route ({dfs_path} steps) and bypassed the heavy memory queue expansion of BFS.", "DFS"
        
        # Logic 2: If path lengths are identical, the faster execution time wins
        else:
            if bfs_time < dfs_time:
                return f"💡 Recommendation: BFS is recommended. Both algorithms found an equally optimal path ({bfs_path} steps), but BFS processed the dynamic graph faster ({bfs_time:.2f}ms).", "BFS"
            else:
                return f"💡 Recommendation: DFS is recommended. Both algorithms found an equally optimal path ({bfs_path} steps), but DFS computed it faster ({dfs_time:.2f}ms) with lower memory overhead.", "DFS"

    def show_summary(self, bfs_data, dfs_data):
        """Displays Desktop 3: Result Summary when a simulation finishes."""
        modal = ctk.CTkToplevel(self.parent)
        modal.title("Result Summary")
        modal.configure(fg_color=BG_SECONDARY)
        modal.attributes("-topmost", True)
        self.center_modal(modal, 550, 480)

        ctk.CTkLabel(modal, text="Result Summary:", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_LIGHT).pack(pady=(20, 15), anchor="w", padx=30)

        # Get the recommendation and the winner
        rec_text, winner = self._get_recommendation(bfs_data, dfs_data)

        # Cards Container
        cards_frame = ctk.CTkFrame(modal, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30)
        cards_frame.grid_columnconfigure((0, 1), weight=1)

        # BFS Card (with dynamic border glow)
        bfs_bw = 3 if winner == "BFS" else 0
        bfs_bc = COLOR_RECOMMENDATION if winner == "BFS" else BG_MAIN
        bfs_frame = ctk.CTkFrame(cards_frame, fg_color=BG_MAIN, corner_radius=10, border_width=bfs_bw, border_color=bfs_bc)
        bfs_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        ctk.CTkLabel(bfs_frame, text="BFS RESULT", fg_color=COLOR_BFS, corner_radius=6, text_color="white", font=ctk.CTkFont(weight="bold")).pack(fill="x", padx=10, pady=10)
        self._populate_card_data(bfs_frame, bfs_data)

        # DFS Card (with dynamic border glow)
        dfs_bw = 3 if winner == "DFS" else 0
        dfs_bc = COLOR_RECOMMENDATION if winner == "DFS" else BG_MAIN
        dfs_frame = ctk.CTkFrame(cards_frame, fg_color=BG_MAIN, corner_radius=10, border_width=dfs_bw, border_color=dfs_bc)
        dfs_frame.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        ctk.CTkLabel(dfs_frame, text="DFS RESULT", fg_color=COLOR_DFS, corner_radius=6, text_color="white", font=ctk.CTkFont(weight="bold")).pack(fill="x", padx=10, pady=10)
        self._populate_card_data(dfs_frame, dfs_data)

        # Recommendation Text
        rec_label = ctk.CTkLabel(modal, text=rec_text, text_color=COLOR_RECOMMENDATION, font=ctk.CTkFont(weight="bold", slant="italic"), wraplength=490, justify="left")
        rec_label.pack(pady=(20, 5), padx=30, fill="x", anchor="w")

        # Save Button
        btn_save = ctk.CTkButton(modal, text="💾 Save Result", fg_color=COLOR_BATCH, font=ctk.CTkFont(weight="bold", size=14), 
                                 command=lambda: self.save_result_action(bfs_data, dfs_data, modal))
        btn_save.pack(pady=20)

    def _populate_card_data(self, frame, data):
        """Helper to fill stats in the summary cards."""
        ctk.CTkLabel(frame, text=f"Nodes: {data['nodes']}", text_color=TEXT_LIGHT, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(5, 2))
        ctk.CTkLabel(frame, text=f"Time: {data['time_ms']:.2f}ms", text_color=TEXT_LIGHT, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=2)
        ctk.CTkLabel(frame, text=f"Path: {data['path']}", text_color=TEXT_LIGHT, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=2)
        ctk.CTkLabel(frame, text=f"Memory: {data['mem_kb']:.2f}KB", text_color=TEXT_LIGHT, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(2, 15))

    def save_result_action(self, bfs_data, dfs_data, modal):
        record = {
            "id": len(self.history) + 1,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "bfs": bfs_data,
            "dfs": dfs_data
        }
        self.history.append(record)
        self.save_history()
        modal.destroy()
        print("Result saved successfully.")

    def show_history_list(self):
        """Displays Desktop 4: Result History List."""
        list_modal = ctk.CTkToplevel(self.parent)
        list_modal.title("Result History")
        list_modal.configure(fg_color=BG_SECONDARY)
        list_modal.attributes("-topmost", True)
        self.center_modal(list_modal, 450, 500)

        ctk.CTkLabel(list_modal, text="Result History:", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_LIGHT).pack(pady=(20, 10), anchor="w", padx=30)

        scroll_frame = ctk.CTkScrollableFrame(list_modal, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        if not self.history:
            ctk.CTkLabel(scroll_frame, text="No saved results yet.", text_color=TEXT_MUTED).pack(pady=20)
            return

        for index, record in enumerate(self.history):
            row = ctk.CTkFrame(scroll_frame, fg_color=COLOR_BATCH, corner_radius=6)
            row.pack(fill="x", pady=5)
            
            ordinal = f"{record['id']}{'th' if 11<=record['id']<=13 else {1:'st',2:'nd',3:'rd'}.get(record['id']%10, 'th')} Simulation"
            
            ctk.CTkLabel(row, text=ordinal, text_color="white", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=15, pady=10)
            
            btn_del = ctk.CTkButton(row, text="🗑", width=30, fg_color=COLOR_RESET, command=lambda i=index: self.delete_history_item(i, list_modal))
            btn_del.pack(side="right", padx=(5, 10), pady=10)
            
            btn_view = ctk.CTkButton(row, text="↗", width=30, fg_color="transparent", border_width=1, border_color="white", 
                                     command=lambda rec=record, title=ordinal: self.show_history_detail(rec, title, list_modal))
            btn_view.pack(side="right", padx=5, pady=10)

    def delete_history_item(self, index, list_modal):
        del self.history[index]
        self.save_history()
        list_modal.destroy()
        self.show_history_list() 

    def show_history_detail(self, record, title, parent_modal):
        """Displays Desktop 5: Detailed view of a specific history record."""
        parent_modal.destroy() 
        
        detail_modal = ctk.CTkToplevel(self.parent)
        detail_modal.title("Result History Detail")
        detail_modal.configure(fg_color=BG_SECONDARY)
        detail_modal.attributes("-topmost", True)
        self.center_modal(detail_modal, 550, 450)

        header_frame = ctk.CTkFrame(detail_modal, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))
        
        ctk.CTkLabel(header_frame, text="Result History:", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_LIGHT).pack(side="left")
        
        btn_back = ctk.CTkButton(header_frame, text="← Back to List", width=100, fg_color="transparent", border_width=1, command=lambda: [detail_modal.destroy(), self.show_history_list()])
        btn_back.pack(side="right")

        ctk.CTkLabel(detail_modal, text=f"Viewing: {title}", text_color=TEXT_MUTED, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=30, pady=(0, 15))

        # Get the recommendation and the winner for historical records
        rec_text, winner = self._get_recommendation(record['bfs'], record['dfs'])

        # Cards Container 
        cards_frame = ctk.CTkFrame(detail_modal, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30)
        cards_frame.grid_columnconfigure((0, 1), weight=1)

        # BFS Card (with dynamic border glow)
        bfs_bw = 3 if winner == "BFS" else 0
        bfs_bc = COLOR_RECOMMENDATION if winner == "BFS" else BG_MAIN
        bfs_frame = ctk.CTkFrame(cards_frame, fg_color=BG_MAIN, corner_radius=10, border_width=bfs_bw, border_color=bfs_bc)
        bfs_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        ctk.CTkLabel(bfs_frame, text="BFS RESULT", fg_color=COLOR_BFS, corner_radius=6, text_color="white", font=ctk.CTkFont(weight="bold")).pack(fill="x", padx=10, pady=10)
        self._populate_card_data(bfs_frame, record['bfs'])

        # DFS Card (with dynamic border glow)
        dfs_bw = 3 if winner == "DFS" else 0
        dfs_bc = COLOR_RECOMMENDATION if winner == "DFS" else BG_MAIN
        dfs_frame = ctk.CTkFrame(cards_frame, fg_color=BG_MAIN, corner_radius=10, border_width=dfs_bw, border_color=dfs_bc)
        dfs_frame.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        ctk.CTkLabel(dfs_frame, text="DFS RESULT", fg_color=COLOR_DFS, corner_radius=6, text_color="white", font=ctk.CTkFont(weight="bold")).pack(fill="x", padx=10, pady=10)
        self._populate_card_data(dfs_frame, record['dfs'])

        # Recommendation Text
        rec_label = ctk.CTkLabel(detail_modal, text=rec_text, text_color=COLOR_RECOMMENDATION, font=ctk.CTkFont(weight="bold", slant="italic"), wraplength=490, justify="left")
        rec_label.pack(pady=(20, 10), padx=30, fill="x", anchor="w")