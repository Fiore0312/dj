#!/usr/bin/env python3
"""
🎛️ DJ Agent Control Panel
Controls for autonomous DJ behavior and session management
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Dict, Any
from enum import Enum


class DJGenre(Enum):
    """Supported DJ genres"""
    HOUSE = "House"
    TECHNO = "Techno"
    HIP_HOP = "Hip-Hop"
    POP = "Pop/Top 40"
    LATIN = "Latin"
    ELECTRONIC = "Electronic"
    AUTO = "Auto-Select"


class EnergyLevel(Enum):
    """Energy levels for DJ sessions"""
    LOW = "Low Energy"
    MEDIUM = "Medium Energy"
    HIGH = "High Energy"
    PEAK = "Peak Time"
    AUTO = "Auto-Adapt"


class BehaviorProfile(Enum):
    """DJ behavior profiles"""
    RADIO = "Radio DJ"
    CLUB = "Club DJ"
    MOBILE = "Mobile DJ"
    CUSTOM = "Custom"


class AgentControlPanel:
    """
    Main control panel for autonomous DJ agent.
    Provides intuitive controls for DJ behavior and session management.
    """

    def __init__(self, parent: tk.Widget):
        """Initialize the agent control panel"""
        self.parent = parent
        self.session_active = False
        self.session_time = 0
        self.timer_job = None

        # Callbacks for external integration
        self.on_session_start: Optional[Callable] = None
        self.on_session_stop: Optional[Callable] = None
        self.on_settings_change: Optional[Callable] = None

        # Current settings
        self.current_genre = DJGenre.AUTO
        self.current_energy = EnergyLevel.MEDIUM
        self.current_profile = BehaviorProfile.CLUB

        # UI variables
        self.genre_var = tk.StringVar(value=self.current_genre.value)
        self.energy_var = tk.StringVar(value=self.current_energy.value)
        self.profile_var = tk.StringVar(value=self.current_profile.value)
        self.session_time_var = tk.StringVar(value="00:00:00")

        self._create_widgets()
        self._setup_layout()

    def _create_widgets(self):
        """Create all UI widgets"""
        # Main frame with dark theme
        self.main_frame = tk.Frame(self.parent, bg='#2d2d2d', relief='solid', bd=1)

        # Title
        self.title_label = tk.Label(
            self.main_frame,
            text="🎛️ DJ AGENT CONTROL",
            bg='#2d2d2d',
            fg='#00d4ff',
            font=('Helvetica', 14, 'bold')
        )

        # Power button
        self.power_button = tk.Button(
            self.main_frame,
            text="START DJ SESSION",
            command=self._toggle_session,
            bg='#00d4ff',
            fg='#1a1a1a',
            font=('Helvetica', 12, 'bold'),
            relief='raised',
            bd=2
        )

        # Session timer
        self.session_time_display = tk.Label(
            self.main_frame,
            textvariable=self.session_time_var,
            bg='#2d2d2d',
            fg='#00ff88',
            font=('Courier', 16, 'bold')
        )

        # Genre selection
        self.genre_label = tk.Label(
            self.main_frame,
            text="Music Genre:",
            bg='#2d2d2d',
            fg='#ffffff',
            font=('Helvetica', 10)
        )

        self.genre_combo = ttk.Combobox(
            self.main_frame,
            textvariable=self.genre_var,
            values=[genre.value for genre in DJGenre],
            state="readonly"
        )

        # Energy level
        self.energy_label = tk.Label(
            self.main_frame,
            text="Energy Level:",
            bg='#2d2d2d',
            fg='#ffffff',
            font=('Helvetica', 10)
        )

        self.energy_scale = tk.Scale(
            self.main_frame,
            from_=0,
            to=4,
            orient=tk.HORIZONTAL,
            bg='#2d2d2d',
            fg='#ffffff',
            troughcolor='#4d4d4d',
            activebackground='#00d4ff',
            command=self._on_energy_change
        )

        # Profile selection
        self.profile_label = tk.Label(
            self.main_frame,
            text="DJ Style:",
            bg='#2d2d2d',
            fg='#ffffff',
            font=('Helvetica', 10)
        )

        self.profile_combo = ttk.Combobox(
            self.main_frame,
            textvariable=self.profile_var,
            values=[profile.value for profile in BehaviorProfile],
            state="readonly"
        )

        # Quick action buttons
        self.energy_up_btn = tk.Button(
            self.main_frame,
            text="🔥 ENERGY UP",
            command=self._energy_up,
            bg='#3d3d3d',
            fg='#ffffff',
            font=('Helvetica', 9, 'bold')
        )

        self.energy_down_btn = tk.Button(
            self.main_frame,
            text="😌 CHILL OUT",
            command=self._energy_down,
            bg='#3d3d3d',
            fg='#ffffff',
            font=('Helvetica', 9, 'bold')
        )

    def _setup_layout(self):
        """Setup widget layout using grid"""
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Title
        self.title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")

        # Power button
        self.power_button.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5, padx=10)

        # Session timer
        self.session_time_display.grid(row=2, column=0, columnspan=2, pady=5)

        # Genre
        self.genre_label.grid(row=3, column=0, sticky="w", padx=10, pady=2)
        self.genre_combo.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=2)

        # Energy
        self.energy_label.grid(row=5, column=0, sticky="w", padx=10, pady=2)
        self.energy_scale.grid(row=6, column=0, columnspan=2, sticky="ew", padx=10, pady=2)

        # Profile
        self.profile_label.grid(row=7, column=0, sticky="w", padx=10, pady=2)
        self.profile_combo.grid(row=8, column=0, columnspan=2, sticky="ew", padx=10, pady=2)

        # Action buttons
        self.energy_up_btn.grid(row=9, column=0, sticky="ew", padx=5, pady=5)
        self.energy_down_btn.grid(row=9, column=1, sticky="ew", padx=5, pady=5)

        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

    def _toggle_session(self):
        """Toggle DJ session on/off"""
        if not self.session_active:
            self._start_session()
        else:
            self._stop_session()

    def _start_session(self):
        """Start DJ session"""
        self.session_active = True
        self.session_time = 0
        self.power_button.config(text="STOP DJ SESSION", bg='#ff3366')
        self._update_timer()

        if self.on_session_start:
            settings = self._get_current_settings()
            self.on_session_start(settings)

    def _stop_session(self):
        """Stop DJ session"""
        self.session_active = False
        self.power_button.config(text="START DJ SESSION", bg='#00d4ff')

        if self.timer_job:
            self.parent.after_cancel(self.timer_job)
            self.timer_job = None

        if self.on_session_stop:
            self.on_session_stop()

    def _update_timer(self):
        """Update session timer"""
        if self.session_active:
            hours = self.session_time // 3600
            minutes = (self.session_time % 3600) // 60
            seconds = self.session_time % 60

            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.session_time_var.set(time_str)

            self.session_time += 1
            self.timer_job = self.parent.after(1000, self._update_timer)

    def _on_energy_change(self, value):
        """Handle energy level change"""
        energy_index = int(float(value))
        energy_levels = list(EnergyLevel)

        if 0 <= energy_index < len(energy_levels):
            self.current_energy = energy_levels[energy_index]
            self.energy_var.set(self.current_energy.value)

    def _energy_up(self):
        """Increase energy level"""
        current_value = self.energy_scale.get()
        new_value = min(4, current_value + 1)
        self.energy_scale.set(new_value)

    def _energy_down(self):
        """Decrease energy level"""
        current_value = self.energy_scale.get()
        new_value = max(0, current_value - 1)
        self.energy_scale.set(new_value)

    def _get_current_settings(self) -> Dict[str, Any]:
        """Get current DJ settings"""
        return {
            'genre': self.current_genre,
            'energy': self.current_energy,
            'profile': self.current_profile,
            'session_active': self.session_active,
            'session_time': self.session_time
        }

    def get_frame(self) -> tk.Frame:
        """Get the main frame for embedding in parent"""
        return self.main_frame

    def set_session_callback(self, start_callback: Callable, stop_callback: Callable):
        """Set callbacks for session start/stop"""
        self.on_session_start = start_callback
        self.on_session_stop = stop_callback