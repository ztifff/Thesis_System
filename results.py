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

    def show_summary(self, bfs_data, dfs_data):
        """Displays Desktop 3: Result Summary when a simulation finishes."""
        modal = ctk.CTkToplevel(self.parent)
        modal.title("Result Summary")
        modal.configure(fg_color=BG_SECONDARY)
        modal.attributes("-topmost", True)
        self.center_modal(modal, 550, 400)

        ctk.CTkLabel(modal, text="Result Summary:", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_LIGHT).pack(pady=(20, 20), anchor="w", padx=30)

        # Cards Container
        cards_frame = ctk.CTkFrame(modal, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30)
        cards_frame.grid_columnconfigure((0, 1), weight=1)

        # BFS Card
        bfs_frame = ctk.CTkFrame(cards_frame, fg_color=BG_MAIN, corner_radius=10)
        bfs_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        ctk.CTkLabel(bfs_frame, text="BFS RESULT", fg_color=COLOR_BFS, corner_radius=6, text_color="white", font=ctk.CTkFont(weight="bold")).pack(fill="x", padx=10, pady=10)
        self._populate_card_data(bfs_frame, bfs_data)

        # DFS Card
        dfs_frame = ctk.CTkFrame(cards_frame, fg_color=BG_MAIN, corner_radius=10)
        dfs_frame.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        ctk.CTkLabel(dfs_frame, text="DFS RESULT", fg_color=COLOR_DFS, corner_radius=6, text_color="white", font=ctk.CTkFont(weight="bold")).pack(fill="x", padx=10, pady=10)
        self._populate_card_data(dfs_frame, dfs_data)

        # Save Button
        btn_save = ctk.CTkButton(modal, text="💾 Save Result", fg_color=COLOR_BATCH, font=ctk.CTkFont(weight="bold", size=14), 
                                 command=lambda: self.save_result_action(bfs_data, dfs_data, modal))
        btn_save.pack(pady=30)

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
            
            # Display name like "1st Simulation", "2nd Simulation", etc.
            ordinal = f"{record['id']}{'th' if 11<=record['id']<=13 else {1:'st',2:'nd',3:'rd'}.get(record['id']%10, 'th')} Simulation"
            
            ctk.CTkLabel(row, text=ordinal, text_color="white", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=15, pady=10)
            
            # Delete Button
            btn_del = ctk.CTkButton(row, text="🗑", width=30, fg_color=COLOR_RESET, command=lambda i=index: self.delete_history_item(i, list_modal))
            btn_del.pack(side="right", padx=(5, 10), pady=10)
            
            # View Detail Button
            btn_view = ctk.CTkButton(row, text="↗", width=30, fg_color="transparent", border_width=1, border_color="white", 
                                     command=lambda rec=record, title=ordinal: self.show_history_detail(rec, title, list_modal))
            btn_view.pack(side="right", padx=5, pady=10)

    def delete_history_item(self, index, list_modal):
        del self.history[index]
        self.save_history()
        list_modal.destroy()
        self.show_history_list() # Refresh the list

    def show_history_detail(self, record, title, parent_modal):
        """Displays Desktop 5: Detailed view of a specific history record."""
        parent_modal.destroy() # Close the list modal
        
        detail_modal = ctk.CTkToplevel(self.parent)
        detail_modal.title("Result History Detail")
        detail_modal.configure(fg_color=BG_SECONDARY)
        detail_modal.attributes("-topmost", True)
        self.center_modal(detail_modal, 550, 400)

        header_frame = ctk.CTkFrame(detail_modal, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 20))
        
        ctk.CTkLabel(header_frame, text="Result History:", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_LIGHT).pack(side="left")
        
        # Back Button to return to list
        btn_back = ctk.CTkButton(header_frame, text="← Back to List", width=100, fg_color="transparent", border_width=1, command=lambda: [detail_modal.destroy(), self.show_history_list()])
        btn_back.pack(side="right")

        ctk.CTkLabel(detail_modal, text=f"Viewing: {title}", text_color=TEXT_MUTED, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=30, pady=(0, 10))

        # Cards Container (Reused from summary logic)
        cards_frame = ctk.CTkFrame(detail_modal, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30)
        cards_frame.grid_columnconfigure((0, 1), weight=1)

        bfs_frame = ctk.CTkFrame(cards_frame, fg_color=BG_MAIN, corner_radius=10)
        bfs_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        ctk.CTkLabel(bfs_frame, text="BFS RESULT", fg_color=COLOR_BFS, corner_radius=6, text_color="white", font=ctk.CTkFont(weight="bold")).pack(fill="x", padx=10, pady=10)
        self._populate_card_data(bfs_frame, record['bfs'])

        dfs_frame = ctk.CTkFrame(cards_frame, fg_color=BG_MAIN, corner_radius=10)
        dfs_frame.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        ctk.CTkLabel(dfs_frame, text="DFS RESULT", fg_color=COLOR_DFS, corner_radius=6, text_color="white", font=ctk.CTkFont(weight="bold")).pack(fill="x", padx=10, pady=10)
        self._populate_card_data(dfs_frame, record['dfs'])