#!/usr/bin/env python3
"""
🎧 Autonomous DJ System - Main GUI Window
Professional DJ interface with dark theme and real-time controls
"""

import tkinter as tk
from tkinter import ttk
import threading
import asyncio
from typing import Optional, Dict, Any
import sys
import os

# Import relative modules
from .themes.dj_dark_theme import DJTheme, apply_dj_theme
from .components.agent_control import AgentControlPanel


class StatusDisplay:
    """Simple status display panel"""

    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self._create_widgets()

    def _create_widgets(self):
        """Create status display widgets"""
        self.main_frame = tk.Frame(self.parent, bg='#2d2d2d', relief='solid', bd=1)

        # Title
        self.title_label = tk.Label(
            self.main_frame,
            text="📊 STATUS DISPLAY",
            bg='#2d2d2d',
            fg='#00d4ff',
            font=('Helvetica', 14, 'bold')
        )

        # Deck A status
        self.deck_a_frame = tk.Frame(self.main_frame, bg='#3d3d3d', relief='raised', bd=1)
        self.deck_a_label = tk.Label(
            self.deck_a_frame,
            text="DECK A",
            bg='#0099ff',
            fg='#ffffff',
            font=('Helvetica', 12, 'bold')
        )
        self.deck_a_track = tk.Label(
            self.deck_a_frame,
            text="No Track Loaded",
            bg='#3d3d3d',
            fg='#cccccc',
            font=('Helvetica', 10)
        )
        self.deck_a_bpm = tk.Label(
            self.deck_a_frame,
            text="BPM: ---",
            bg='#3d3d3d',
            fg='#00ff88',
            font=('Courier', 12, 'bold')
        )

        # Deck B status
        self.deck_b_frame = tk.Frame(self.main_frame, bg='#3d3d3d', relief='raised', bd=1)
        self.deck_b_label = tk.Label(
            self.deck_b_frame,
            text="DECK B",
            bg='#ff9900',
            fg='#ffffff',
            font=('Helvetica', 12, 'bold')
        )
        self.deck_b_track = tk.Label(
            self.deck_b_frame,
            text="No Track Loaded",
            bg='#3d3d3d',
            fg='#cccccc',
            font=('Helvetica', 10)
        )
        self.deck_b_bpm = tk.Label(
            self.deck_b_frame,
            text="BPM: ---",
            bg='#3d3d3d',
            fg='#00ff88',
            font=('Courier', 12, 'bold')
        )

        # Crossfader display
        self.crossfader_label = tk.Label(
            self.main_frame,
            text="Crossfader Position:",
            bg='#2d2d2d',
            fg='#ffffff',
            font=('Helvetica', 10)
        )

        self.crossfader_var = tk.DoubleVar(value=50.0)
        self.crossfader_display = tk.Scale(
            self.main_frame,
            variable=self.crossfader_var,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            bg='#2d2d2d',
            fg='#ffffff',
            troughcolor='#4d4d4d',
            activebackground='#00d4ff',
            state='disabled'
        )

        # Agent status
        self.agent_status = tk.Label(
            self.main_frame,
            text="Agent Status: Idle",
            bg='#2d2d2d',
            fg='#ffaa00',
            font=('Helvetica', 10, 'italic')
        )

        self._setup_layout()

    def _setup_layout(self):
        """Setup layout for status display"""
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Title
        self.title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")

        # Deck A
        self.deck_a_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.deck_a_label.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        self.deck_a_track.grid(row=1, column=0, sticky="ew", padx=5, pady=2)
        self.deck_a_bpm.grid(row=2, column=0, sticky="ew", padx=5, pady=2)

        # Deck B
        self.deck_b_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        self.deck_b_label.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        self.deck_b_track.grid(row=1, column=0, sticky="ew", padx=5, pady=2)
        self.deck_b_bpm.grid(row=2, column=0, sticky="ew", padx=5, pady=2)

        # Crossfader
        self.crossfader_label.grid(row=2, column=0, columnspan=2, pady=(10, 2), sticky="ew")
        self.crossfader_display.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=2)

        # Agent status
        self.agent_status.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

    def get_frame(self) -> tk.Frame:
        """Get the main frame"""
        return self.main_frame

    def update_deck_info(self, deck: str, track_name: str, bpm: float):
        """Update deck information"""
        if deck.upper() == 'A':
            self.deck_a_track.config(text=track_name)
            self.deck_a_bpm.config(text=f"BPM: {bpm:.1f}")
        elif deck.upper() == 'B':
            self.deck_b_track.config(text=track_name)
            self.deck_b_bpm.config(text=f"BPM: {bpm:.1f}")

    def update_crossfader(self, position: float):
        """Update crossfader position (0-100)"""
        self.crossfader_var.set(position)

    def update_agent_status(self, status: str):
        """Update agent status text"""
        self.agent_status.config(text=f"Agent Status: {status}")


class ManualOverridePanel:
    """Manual override controls"""

    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self._create_widgets()

    def _create_widgets(self):
        """Create manual override widgets"""
        self.main_frame = tk.Frame(self.parent, bg='#2d2d2d', relief='solid', bd=1)

        # Title
        self.title_label = tk.Label(
            self.main_frame,
            text="🚨 MANUAL OVERRIDE",
            bg='#2d2d2d',
            fg='#ff3366',
            font=('Helvetica', 14, 'bold')
        )

        # Emergency stop
        self.emergency_stop = tk.Button(
            self.main_frame,
            text="🛑 EMERGENCY STOP",
            bg='#ff3366',
            fg='#ffffff',
            font=('Helvetica', 12, 'bold'),
            relief='raised',
            bd=3
        )

        # Take control
        self.take_control = tk.Button(
            self.main_frame,
            text="🎛️ TAKE CONTROL",
            bg='#ffaa00',
            fg='#1a1a1a',
            font=('Helvetica', 10, 'bold')
        )

        # Manual crossfader
        self.manual_cf_label = tk.Label(
            self.main_frame,
            text="Manual Crossfader:",
            bg='#2d2d2d',
            fg='#ffffff',
            font=('Helvetica', 10)
        )

        self.manual_crossfader = tk.Scale(
            self.main_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            bg='#2d2d2d',
            fg='#ffffff',
            troughcolor='#4d4d4d',
            activebackground='#ffaa00'
        )

        # Basic EQ controls
        self.eq_label = tk.Label(
            self.main_frame,
            text="Quick EQ:",
            bg='#2d2d2d',
            fg='#ffffff',
            font=('Helvetica', 10)
        )

        # EQ buttons
        self.eq_frame = tk.Frame(self.main_frame, bg='#2d2d2d')

        self.bass_cut_a = tk.Button(
            self.eq_frame,
            text="Bass Cut A",
            bg='#3d3d3d',
            fg='#ffffff',
            font=('Helvetica', 8)
        )

        self.bass_cut_b = tk.Button(
            self.eq_frame,
            text="Bass Cut B",
            bg='#3d3d3d',
            fg='#ffffff',
            font=('Helvetica', 8)
        )

        self._setup_layout()

    def _setup_layout(self):
        """Setup layout for manual override panel"""
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Title
        self.title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")

        # Emergency stop
        self.emergency_stop.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        # Take control
        self.take_control.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=2)

        # Manual crossfader
        self.manual_cf_label.grid(row=3, column=0, columnspan=2, pady=(10, 2), sticky="w", padx=10)
        self.manual_crossfader.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=2)

        # EQ controls
        self.eq_label.grid(row=5, column=0, columnspan=2, pady=(10, 2), sticky="w", padx=10)
        self.eq_frame.grid(row=6, column=0, columnspan=2, sticky="ew", padx=10, pady=2)

        self.bass_cut_a.grid(row=0, column=0, sticky="ew", padx=2)
        self.bass_cut_b.grid(row=0, column=1, sticky="ew", padx=2)

        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.eq_frame.columnconfigure(0, weight=1)
        self.eq_frame.columnconfigure(1, weight=1)

    def get_frame(self) -> tk.Frame:
        """Get the main frame"""
        return self.main_frame


class AutonomousDJGUI:
    """
    Main GUI application for the Autonomous DJ System.
    Provides professional interface for DJ control and monitoring.
    """

    def __init__(self):
        """Initialize the main GUI application"""
        self.root = tk.Tk()
        self.root.title("🎧 Autonomous DJ System")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)

        # Initialize theme
        self.theme = apply_dj_theme(self.root)

        # Initialize components
        self.agent_control: Optional[AgentControlPanel] = None
        self.status_display: Optional[StatusDisplay] = None
        self.manual_override: Optional[ManualOverridePanel] = None

        # Setup GUI
        self._setup_main_layout()
        self._create_components()
        self._setup_callbacks()
        self._setup_menu()

        # Status variables
        self.connected_to_traktor = False
        self.dj_agent_running = False

    def _setup_main_layout(self):
        """Setup the main window layout"""
        # Configure main grid
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=2)

        # Create main frames
        self.top_frame = tk.Frame(self.root, bg=self.theme.colors.PRIMARY_DARK)
        self.bottom_frame = tk.Frame(self.root, bg=self.theme.colors.PRIMARY_DARK)

        self.top_frame.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        self.bottom_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)

        # Configure frame grids
        self.top_frame.columnconfigure(0, weight=1)
        self.top_frame.columnconfigure(1, weight=2)
        self.top_frame.columnconfigure(2, weight=1)
        self.top_frame.rowconfigure(0, weight=1)

        self.bottom_frame.columnconfigure(0, weight=2)
        self.bottom_frame.columnconfigure(1, weight=1)
        self.bottom_frame.rowconfigure(0, weight=1)

    def _create_components(self):
        """Create all GUI components"""
        # Agent Control Panel (top-left)
        self.agent_control = AgentControlPanel(self.top_frame)
        self.agent_control.get_frame().grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        # Status Display (top-center)
        self.status_display = StatusDisplay(self.top_frame)
        self.status_display.get_frame().grid(row=0, column=1, sticky="nsew", padx=2, pady=2)

        # Manual Override (top-right)
        self.manual_override = ManualOverridePanel(self.top_frame)
        self.manual_override.get_frame().grid(row=0, column=2, sticky="nsew", padx=2, pady=2)

        # Music Library placeholder (bottom-left)
        self.library_frame = tk.Frame(self.bottom_frame, bg='#2d2d2d', relief='solid', bd=1)
        self.library_label = tk.Label(
            self.library_frame,
            text="📚 MUSIC LIBRARY\n(Coming Soon)",
            bg='#2d2d2d',
            fg='#cccccc',
            font=('Helvetica', 12)
        )
        self.library_label.pack(expand=True)
        self.library_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        # Audio Levels placeholder (bottom-right)
        self.levels_frame = tk.Frame(self.bottom_frame, bg='#2d2d2d', relief='solid', bd=1)
        self.levels_label = tk.Label(
            self.levels_frame,
            text="📈 AUDIO LEVELS\n(Coming Soon)",
            bg='#2d2d2d',
            fg='#cccccc',
            font=('Helvetica', 12)
        )
        self.levels_label.pack(expand=True)
        self.levels_frame.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)

    def _setup_callbacks(self):
        """Setup callbacks for component interactions"""
        if self.agent_control:
            self.agent_control.set_session_callback(
                self._on_dj_session_start,
                self._on_dj_session_stop
            )

    def _setup_menu(self):
        """Setup application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Connect to Traktor", command=self._connect_traktor)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Full Screen", command=self._toggle_fullscreen)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

        # Setup window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_dj_session_start(self, settings: Dict[str, Any]):
        """Handle DJ session start"""
        print(f"DJ Session started with settings: {settings}")
        self.dj_agent_running = True

        if self.status_display:
            self.status_display.update_agent_status("Starting...")

        # Here you would integrate with the actual DJ agent
        # For now, simulate some activity
        self.root.after(2000, lambda: self.status_display.update_agent_status("Mixing..."))

    def _on_dj_session_stop(self):
        """Handle DJ session stop"""
        print("DJ Session stopped")
        self.dj_agent_running = False

        if self.status_display:
            self.status_display.update_agent_status("Idle")

    def _connect_traktor(self):
        """Connect to Traktor Pro"""
        # Here you would integrate with the MIDI driver
        print("Connecting to Traktor...")
        self.connected_to_traktor = True

        if self.status_display:
            self.status_display.update_agent_status("Connected to Traktor")

    def _toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)

    def _show_about(self):
        """Show about dialog"""
        about_text = """
🎧 Autonomous DJ System v1.0

Professional DJ software with autonomous mixing capabilities.

Features:
• Traktor Pro integration via MIDI
• Intelligent track selection and mixing
• Real-time performance monitoring
• Manual override controls

Built with Claude Code + MCP Agents
        """

        about_window = tk.Toplevel(self.root)
        about_window.title("About Autonomous DJ System")
        about_window.geometry("400x300")
        about_window.configure(bg=self.theme.colors.PRIMARY_DARK)

        about_label = tk.Label(
            about_window,
            text=about_text,
            bg=self.theme.colors.PRIMARY_DARK,
            fg=self.theme.colors.TEXT_PRIMARY,
            font=('Helvetica', 10),
            justify=tk.LEFT
        )
        about_label.pack(expand=True, padx=20, pady=20)

    def _on_closing(self):
        """Handle application closing"""
        if self.dj_agent_running:
            # Stop DJ session if running
            if self.agent_control:
                self.agent_control._stop_session()

        self.root.quit()
        self.root.destroy()

    def run(self):
        """Start the GUI application"""
        print("🎧 Starting Autonomous DJ System GUI...")
        print("Window size: 1200x800")
        print("Theme: DJ Dark Theme")

        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nShutting down gracefully...")
            self._on_closing()

    def update_from_midi_driver(self, status: Dict[str, Any]):
        """Update GUI based on MIDI driver status"""
        if self.status_display:
            # Update deck information
            if 'deck_a' in status:
                deck_a = status['deck_a']
                self.status_display.update_deck_info(
                    'A',
                    deck_a.get('track_name', 'Unknown'),
                    deck_a.get('bpm', 0.0)
                )

            if 'deck_b' in status:
                deck_b = status['deck_b']
                self.status_display.update_deck_info(
                    'B',
                    deck_b.get('track_name', 'Unknown'),
                    deck_b.get('bpm', 0.0)
                )

            # Update crossfader position
            if 'crossfader_position' in status:
                cf_pos = status['crossfader_position'] * 100  # Convert to 0-100
                self.status_display.update_crossfader(cf_pos)


def main():
    """Main entry point"""
    try:
        app = AutonomousDJGUI()
        app.run()
    except Exception as e:
        print(f"Error starting DJ GUI: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()