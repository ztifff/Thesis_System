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
COLOR_RECOMMENDATION = "#facc15" 

class ResultsManager:
    def __init__(self, parent_ui):
        self.parent = parent_ui
        self.history_file = "simulation_history.json"
        self.history = self.load_history()

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []

    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=4)

    def center_modal(self, modal, width, height):
        modal.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (width // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (height // 2)
        modal.geometry(f"{width}x{height}+{x}+{y}")

    def _get_recommendation(self, bfs_data, dfs_data):
        """Analyzes all 4 metrics and declares a winner based on majority rules."""
        bfs_points = 0
        dfs_points = 0
        
        # 1. Compare Path
        if bfs_data['path'] < dfs_data['path']: bfs_points += 1
        elif dfs_data['path'] < bfs_data['path']: dfs_points += 1
        
        # 2. Compare Time
        if bfs_data['time_ms'] < dfs_data['time_ms']: bfs_points += 1
        elif dfs_data['time_ms'] < bfs_data['time_ms']: dfs_points += 1
        
        # 3. Compare Nodes
        if bfs_data['nodes'] < dfs_data['nodes']: bfs_points += 1
        elif dfs_data['nodes'] < bfs_data['nodes']: dfs_points += 1
        
        # 4. Compare Memory
        if bfs_data['mem_kb'] < dfs_data['mem_kb']: bfs_points += 1
        elif dfs_data['mem_kb'] < dfs_data['mem_kb']: dfs_points += 1
        
        # Determine the winner based on points!
        if bfs_points > dfs_points:
            text = f"💡 Recommendation: BFS is optimal. It outperformed DFS in {bfs_points} out of 4 metrics, proving to be the overall most efficient algorithm for this specific maze layout."
            return text, "BFS"
            
        elif dfs_points > bfs_points:
            text = f"💡 Recommendation: DFS is recommended. It outperformed BFS in {dfs_points} out of 4 metrics, demonstrating superior efficiency by bypassing heavy queue expansion."
            return text, "DFS"
            
        else:
            # IT IS A 2-TO-2 TIE! Break the tie using the Execution Time.
            if bfs_data['time_ms'] < dfs_data['time_ms']:
                text = f"💡 Recommendation: BFS is recommended. Both algorithms tied in performance metrics (2 to 2), but BFS broke the tie with a faster execution time ({bfs_data['time_ms']:.2f}ms)."
                return text, "BFS"
            else:
                text = f"💡 Recommendation: DFS is recommended. Both algorithms tied in performance metrics (2 to 2), but DFS broke the tie with a faster execution time ({dfs_data['time_ms']:.2f}ms)."
                return text, "DFS"
    # ---> NEW: Added rerun_callback parameter <---
    def show_summary(self, bfs_data, dfs_data, rerun_callback=None):
        modal = ctk.CTkToplevel(self.parent)
        modal.title("Result Summary")
        modal.configure(fg_color=BG_SECONDARY)
        modal.attributes("-topmost", True)
        self.center_modal(modal, 550, 480)

        ctk.CTkLabel(modal, text="Result Summary:", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_LIGHT).pack(pady=(20, 15), anchor="w", padx=30)

        rec_text, winner = self._get_recommendation(bfs_data, dfs_data)

        cards_frame = ctk.CTkFrame(modal, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30)
        cards_frame.grid_columnconfigure((0, 1), weight=1)

        bfs_bw = 3 if winner == "BFS" else 0
        bfs_bc = COLOR_RECOMMENDATION if winner == "BFS" else BG_MAIN
        bfs_frame = ctk.CTkFrame(cards_frame, fg_color=BG_MAIN, corner_radius=10, border_width=bfs_bw, border_color=bfs_bc)
        bfs_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        ctk.CTkLabel(bfs_frame, text="BFS RESULT", fg_color=COLOR_BFS, corner_radius=6, text_color="white", font=ctk.CTkFont(weight="bold")).pack(fill="x", padx=10, pady=10)
        self._populate_card_data(bfs_frame, bfs_data)

        dfs_bw = 3 if winner == "DFS" else 0
        dfs_bc = COLOR_RECOMMENDATION if winner == "DFS" else BG_MAIN
        dfs_frame = ctk.CTkFrame(cards_frame, fg_color=BG_MAIN, corner_radius=10, border_width=dfs_bw, border_color=dfs_bc)
        dfs_frame.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        ctk.CTkLabel(dfs_frame, text="DFS RESULT", fg_color=COLOR_DFS, corner_radius=6, text_color="white", font=ctk.CTkFont(weight="bold")).pack(fill="x", padx=10, pady=10)
        self._populate_card_data(dfs_frame, dfs_data)

        rec_label = ctk.CTkLabel(modal, text=rec_text, text_color=COLOR_RECOMMENDATION, font=ctk.CTkFont(weight="bold", slant="italic"), wraplength=490, justify="left")
        rec_label.pack(pady=(20, 5), padx=30, fill="x", anchor="w")

        # ---> NEW: Side-by-side Button Layout <---
        btn_frame = ctk.CTkFrame(modal, fg_color="transparent")
        btn_frame.pack(pady=20)

        if rerun_callback:
            btn_rerun = ctk.CTkButton(btn_frame, text="🔄 Rerun Same Maze", fg_color=COLOR_DFS, font=ctk.CTkFont(weight="bold", size=14), 
                                      command=lambda: [modal.destroy(), rerun_callback()])
            btn_rerun.pack(side="left", padx=10)

        btn_save = ctk.CTkButton(btn_frame, text="💾 Save Result", fg_color=COLOR_BATCH, font=ctk.CTkFont(weight="bold", size=14), 
                                 command=lambda: self.save_result_action(bfs_data, dfs_data, modal))
        btn_save.pack(side="left", padx=10)

    def _populate_card_data(self, frame, data):
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

        rec_text, winner = self._get_recommendation(record['bfs'], record['dfs'])

        cards_frame = ctk.CTkFrame(detail_modal, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30)
        cards_frame.grid_columnconfigure((0, 1), weight=1)

        bfs_bw = 3 if winner == "BFS" else 0
        bfs_bc = COLOR_RECOMMENDATION if winner == "BFS" else BG_MAIN
        bfs_frame = ctk.CTkFrame(cards_frame, fg_color=BG_MAIN, corner_radius=10, border_width=bfs_bw, border_color=bfs_bc)
        bfs_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        ctk.CTkLabel(bfs_frame, text="BFS RESULT", fg_color=COLOR_BFS, corner_radius=6, text_color="white", font=ctk.CTkFont(weight="bold")).pack(fill="x", padx=10, pady=10)
        self._populate_card_data(bfs_frame, record['bfs'])

        dfs_bw = 3 if winner == "DFS" else 0
        dfs_bc = COLOR_RECOMMENDATION if winner == "DFS" else BG_MAIN
        dfs_frame = ctk.CTkFrame(cards_frame, fg_color=BG_MAIN, corner_radius=10, border_width=dfs_bw, border_color=dfs_bc)
        dfs_frame.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        ctk.CTkLabel(dfs_frame, text="DFS RESULT", fg_color=COLOR_DFS, corner_radius=6, text_color="white", font=ctk.CTkFont(weight="bold")).pack(fill="x", padx=10, pady=10)
        self._populate_card_data(dfs_frame, record['dfs'])

        rec_label = ctk.CTkLabel(detail_modal, text=rec_text, text_color=COLOR_RECOMMENDATION, font=ctk.CTkFont(weight="bold", slant="italic"), wraplength=490, justify="left")
        rec_label.pack(pady=(20, 10), padx=30, fill="x", anchor="w")