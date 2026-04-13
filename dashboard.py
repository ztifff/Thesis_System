"""
dashboard.py - Main Dashboard frame assembling all UI sections
"""
import customtkinter as ctk
from ui import (
    COLORS,
    TopNavBar,
    InfoBox,
    SectionHeader,
    ScenarioCard,
    AlgorithmCard,
    SummaryCard,
    TagBadge,
)
# ─── Static Data ──────────────────────────────────────────────────────────────
SCENARIOS = [
    {
        "id": "network",
        "icon": "🌐",
        "title": "Network Routing",
        "accent": COLORS["accent_cyan"],
        "description": (
            "Packets navigate through network nodes and routers to reach "
            "destination exits. Failed nodes act as dynamic obstacles disrupting routing paths."
        ),
        "dynamic_tag": "Router nodes fail randomly during traversal",
        "nodes": [
            ("Source Node", ""),
            ("Destination (+3)", ""),
            ("Failed Router", ""),
        ],
        "tags": [
            ("⚡ Dynamic", COLORS["accent_cyan"]),
            ("🚪 Multi-Exit", COLORS["accent_blue"]),
        ],
    },
    {
        "id": "robotics",
        "icon": "🤖",
        "title": "Robotics / Warehouse",
        "accent": COLORS["accent_yellow"],
        "description": (
            "Autonomous robots navigate a warehouse grid to reach delivery exits. "
            "Dynamic shelf rearrangements create shifting obstacles in real-time."
        ),
        "dynamic_tag": "Shelves shift and block paths dynamically",
        "nodes": [
            ("Robot Start", ""),
            ("Delivery Exit (+3)", ""),
            ("Shifted Shelf", ""),
        ],
        "tags": [
            ("⚡ Dynamic", COLORS["accent_yellow"]),
            ("🚪 Multi-Exit", COLORS["accent_blue"]),
        ],
    },
    {
        "id": "traffic",
        "icon": "🚗",
        "title": "Road Traffic",
        "accent": COLORS["accent_green"],
        "description": (
            "Vehicles navigate a city road grid to reach highway exits. "
            "Road closures and accidents create dynamic blockages during navigation."
        ),
        "dynamic_tag": "Road closures appear randomly during navigation",
        "nodes": [
            ("Vehicle Start", ""),
            ("Highway Exit (+3)", ""),
            ("Road Closure", ""),
        ],
        "tags": [
            ("⚡ Dynamic", COLORS["accent_green"]),
            ("🚪 Multi-Exit", COLORS["accent_blue"]),
        ],
    },
    {
        "id": "emergency",
        "icon": "🔥",
        "title": "Emergency Evacuation",
        "accent": COLORS["accent_red"],
        "description": (
            "People evacuate a building floor plan to reach emergency exits. "
            "Fire spreads dynamically, blocking corridors and cutting off escape routes."
        ),
        "dynamic_tag": "Fire spreads and blocks corridors in real-time",
        "nodes": [
            ("Evacuation Start", ""),
            ("Emergency Exit (+3)", ""),
            ("Fire / Blockage", ""),
        ],
        "tags": [
            ("🔥 Hybrid BFS-DFS", COLORS["hybrid_color"]),
            ("⚡ Dynamic", COLORS["accent_yellow"]),
            ("🚪 Multi-Exit", COLORS["accent_red"]),
        ],
    },
    {
        "id": "game",
        "icon": "🎮",
        "title": "Game AI Pathfinding",
        "accent": COLORS["accent_purple"],
        "description": (
            "Game agents navigate a dungeon-style map to reach goal portals. "
            "Enemy spawns and destructible terrain create dynamic environmental changes."
        ),
        "dynamic_tag": "Enemies spawn and terrain changes dynamically",
        "nodes": [
            ("Agent Spawn", ""),
            ("Goal Portal (+2)", ""),
            ("Enemy / Terrain", ""),
        ],
        "tags": [
            ("⚡ Dynamic", COLORS["accent_purple"]),
            ("🚪 Multi-Exit", COLORS["accent_blue"]),
        ],
    },
]
ALGORITHMS = [
    {
        "id": "bfs",
        "letter": "B",
        "title": "Standard BFS",
        "accent": COLORS["bfs_color"],
        "description": (
            "Breadth-First Search explores all neighbors level by level, "
            "guaranteeing the shortest path. Uses a queue (FIFO) data structure."
        ),
    },
    {
        "id": "dfs",
        "letter": "D",
        "title": "Standard DFS",
        "accent": COLORS["dfs_color"],
        "description": (
            "Depth-First Search explores as far as possible along each branch "
            "before backtracking. Uses a stack (LIFO) data structure."
        ),
    },
    {
        "id": "hybrid",
        "letter": "H",
        "title": "Hybrid BFS-DFS",
        "accent": COLORS["hybrid_color"],
        "description": (
            "Combines BFS broad exploration with DFS deep expansion. BFS drives "
            "the search; when a node is near an exit (heuristic condition met), "
            "DFS takes over for fast commitment."
        ),
        "proposed_tag": "Proposed Algorithm — BFS + DFS with heuristic switching",
    },
]
# ─── Dashboard ────────────────────────────────────────────────────────────────
class Dashboard(ctk.CTkFrame):
    """Main dashboard frame."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0, **kwargs)
        self._selected_scenario_idx: int = 3   # default: Emergency Evacuation
        self._selected_algo_idx: int = 2        # default: Hybrid BFS-DFS
        self._scenario_cards: list[ScenarioCard] = []
        self._algo_cards: list[AlgorithmCard] = []
        self._build()
    # ── Build ──────────────────────────────────────────────────────────────
    def _build(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # ── Top nav bar
        nav = TopNavBar(self)
        nav.grid(row=0, column=0, sticky="ew")
        # ── Scrollable main content
        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_dark"],
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["border_hover"],
        )
        self._scroll.grid(row=1, column=0, sticky="nsew")
        self._scroll.grid_columnconfigure(0, weight=1)
        content = self._scroll
        # ── Info box
        InfoBox(content).grid(row=0, column=0, sticky="ew", padx=40, pady=(20, 0))
        # ── Section 1: Scenarios
        SectionHeader(content, number="1", title="Select Real-World Scenario").grid(
            row=1, column=0, sticky="w", padx=40, pady=(24, 10)
        )
        scenario_grid = ctk.CTkFrame(content, fg_color="transparent")
        scenario_grid.grid(row=2, column=0, sticky="ew", padx=40)
        for col_idx in range(5):
            scenario_grid.grid_columnconfigure(col_idx, weight=1, uniform="sc")
        for i, sc_data in enumerate(SCENARIOS):
            card = ScenarioCard(
                scenario_grid,
                scenario_data=sc_data,
                on_select=lambda c, idx=i: self._on_scenario_select(idx),
            )
            card.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            self._scenario_cards.append(card)
        # ── Section 2: Algorithms
        SectionHeader(content, number="2", title="Select Search Algorithm").grid(
            row=3, column=0, sticky="w", padx=40, pady=(28, 10)
        )
        algo_grid = ctk.CTkFrame(content, fg_color="transparent")
        algo_grid.grid(row=4, column=0, sticky="ew", padx=40)
        for col_idx in range(3):
            algo_grid.grid_columnconfigure(col_idx, weight=1, uniform="al")
        for i, al_data in enumerate(ALGORITHMS):
            card = AlgorithmCard(
                algo_grid,
                algo_data=al_data,
                on_select=lambda c, idx=i: self._on_algo_select(idx),
            )
            card.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            self._algo_cards.append(card)
        # ── Summary card placeholder (will be rendered/updated)
        self._summary_container = ctk.CTkFrame(content, fg_color="transparent")
        self._summary_container.grid(row=5, column=0, sticky="ew", padx=40, pady=(20, 0))
        self._summary_container.grid_columnconfigure(0, weight=1)
        # ── Run button
        self._run_btn = ctk.CTkButton(
            content,
            text="▶  Run Simulation",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=48,
            corner_radius=10,
            fg_color=COLORS["accent_blue"],
            hover_color="#2563eb",
            command=self._on_run,
        )
        self._run_btn.grid(row=6, column=0, padx=120, pady=(20, 30), sticky="ew")
        # ── Apply initial selections
        self._refresh_selections()
    # ── Selection Handlers ─────────────────────────────────────────────────
    def _on_scenario_select(self, idx: int):
        self._selected_scenario_idx = idx
        self._refresh_selections()
    def _on_algo_select(self, idx: int):
        self._selected_algo_idx = idx
        self._refresh_selections()
    def _refresh_selections(self):
        sc_idx = self._selected_scenario_idx
        al_idx = self._selected_algo_idx
        # Update scenario cards
        for i, card in enumerate(self._scenario_cards):
            card.set_selected(i == sc_idx)
        # Update algorithm cards
        for i, card in enumerate(self._algo_cards):
            card.set_selected(i == al_idx)
        # Rebuild summary
        for widget in self._summary_container.winfo_children():
            widget.destroy()
        sc_data = SCENARIOS[sc_idx]
        al_data = ALGORITHMS[al_idx]
        SummaryCard(
            self._summary_container,
            scenario_data=sc_data,
            algo_data=al_data,
        ).grid(row=0, column=0, sticky="ew")
        # Update run button text
        sc_name = sc_data["title"]
        al_name = al_data["title"]
        self._run_btn.configure(text=f"▶  Run Simulation — {sc_name} + {al_name}")
    # ── Run Handler ────────────────────────────────────────────────────────
    def _on_run(self):
        sc = SCENARIOS[self._selected_scenario_idx]
        al = ALGORITHMS[self._selected_algo_idx]
        # Create result popup
        popup = ctk.CTkToplevel(self)
        popup.title("Simulation Result")
        popup.geometry("500x340")
        popup.grab_set()
        popup.configure(fg_color=COLORS["bg_dark"])
        accent = al.get("accent", COLORS["accent_blue"])
        ctk.CTkLabel(
            popup,
            text="🚀 Simulation Complete",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(pady=(28, 4))
        ctk.CTkLabel(
            popup,
            text=f"{sc['icon']}  {sc['title']}  ×  {al['title']}",
            font=ctk.CTkFont(size=13),
            text_color=accent,
        ).pack(pady=(0, 20))
        results_frame = ctk.CTkFrame(
            popup, fg_color=COLORS["bg_card"], corner_radius=10
        )
        results_frame.pack(padx=30, fill="x")
        metrics = [
            ("Nodes Explored",  "142"),
            ("Execution Time",  "0.83 ms"),
            ("Path Length",     "17 steps"),
            ("Memory Usage",    "2.4 KB"),
            ("Algorithm Used",  al["title"]),
            ("Scenario",        sc["title"]),
        ]
        for label, value in metrics:
            row = ctk.CTkFrame(results_frame, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=5)
            ctk.CTkLabel(
                row, text=label,
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_muted"],
            ).pack(side="left")
            ctk.CTkLabel(
                row, text=value,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS["text_primary"],
            ).pack(side="right")
        ctk.CTkButton(
            popup,
            text="Close",
            width=120,
            height=34,
            corner_radius=8,
            fg_color=COLORS["border"],
            hover_color=COLORS["border_hover"],
            command=popup.destroy,
        ).pack(pady=20)