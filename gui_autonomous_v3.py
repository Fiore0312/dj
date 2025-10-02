#!/usr/bin/env python3
"""
🎧 GUI for Autonomous DJ System v3.0
Interfaccia grafica integrata con il nuovo sistema autonomo
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import asyncio
import threading
import logging
from datetime import datetime
from typing import Optional

from config import DJConfig
from autonomous_dj_agent_v3 import (
    AutonomousDJMasterV3,
    DJContext,
    MixingPhase
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutonomousGUIv3:
    """
    GUI per Autonomous DJ System v3.0

    Features:
    - Start/Stop autonomous session
    - Real-time status display
    - Current track info
    - Statistics dashboard
    - Manual override controls
    - Energy level adjustment
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎧 Autonomous DJ System v3.0")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a1a')

        # System
        self.dj: Optional[AutonomousDJMasterV3] = None
        self.running = False
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None
        self.loop_thread: Optional[threading.Thread] = None

        # UI
        self._create_ui()

    def _create_ui(self):
        """Create UI components"""

        # Top: Title and status
        top_frame = tk.Frame(self.root, bg='#1a1a1a')
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        title_label = tk.Label(
            top_frame,
            text="🎧 Autonomous DJ System v3.0",
            font=('Arial', 20, 'bold'),
            bg='#1a1a1a',
            fg='#00ff88'
        )
        title_label.pack()

        self.status_var = tk.StringVar(value="⏸️ Not Running")
        status_label = tk.Label(
            top_frame,
            textvariable=self.status_var,
            font=('Arial', 14),
            bg='#1a1a1a',
            fg='#ffaa00'
        )
        status_label.pack()

        # Main container
        main_container = tk.Frame(self.root, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left: Controls
        left_frame = tk.Frame(main_container, bg='#2a2a2a', width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))

        self._create_controls(left_frame)

        # Right: Status and logs
        right_frame = tk.Frame(main_container, bg='#2a2a2a')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._create_status_panel(right_frame)
        self._create_log_panel(right_frame)

    def _create_controls(self, parent):
        """Create control panel"""
        # Title
        tk.Label(
            parent,
            text="🎛️ Controls",
            font=('Arial', 16, 'bold'),
            bg='#2a2a2a',
            fg='white'
        ).pack(pady=10)

        # Session config
        config_frame = ttk.LabelFrame(parent, text="Session Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)

        # Venue
        tk.Label(config_frame, text="Venue:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.venue_var = tk.StringVar(value="club")
        venue_combo = ttk.Combobox(
            config_frame,
            textvariable=self.venue_var,
            values=["club", "bar", "festival", "lounge", "party"],
            width=15
        )
        venue_combo.grid(row=0, column=1, pady=2)

        # Event
        tk.Label(config_frame, text="Event:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.event_var = tk.StringVar(value="party")
        event_combo = ttk.Combobox(
            config_frame,
            textvariable=self.event_var,
            values=["party", "wedding", "corporate", "rave", "chill"],
            width=15
        )
        event_combo.grid(row=1, column=1, pady=2)

        # Duration
        tk.Label(config_frame, text="Duration (hours):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.duration_var = tk.StringVar(value="2.0")
        duration_entry = tk.Entry(config_frame, textvariable=self.duration_var, width=17)
        duration_entry.grid(row=2, column=1, pady=2)

        # Start/Stop buttons
        button_frame = tk.Frame(parent, bg='#2a2a2a')
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        self.start_button = tk.Button(
            button_frame,
            text="🚀 Start Session",
            command=self._start_session,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 12, 'bold'),
            height=2
        )
        self.start_button.pack(fill=tk.X, pady=2)

        self.stop_button = tk.Button(
            button_frame,
            text="⏹️ Stop Session",
            command=self._stop_session,
            bg='#f44336',
            fg='white',
            font=('Arial', 12, 'bold'),
            height=2,
            state=tk.DISABLED
        )
        self.stop_button.pack(fill=tk.X, pady=2)

        # Manual controls
        manual_frame = ttk.LabelFrame(parent, text="Manual Override", padding=10)
        manual_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(
            manual_frame,
            text="⏭️ Skip Track",
            command=self._skip_track,
            width=20
        ).pack(pady=2)

        tk.Button(
            manual_frame,
            text="⏸️ Pause/Resume",
            command=self._toggle_pause,
            width=20
        ).pack(pady=2)

        # Energy control
        tk.Label(manual_frame, text="Target Energy:").pack(pady=(10, 2))
        self.energy_var = tk.DoubleVar(value=0.5)
        energy_scale = tk.Scale(
            manual_frame,
            from_=0.0,
            to=1.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.energy_var,
            command=self._update_energy
        )
        energy_scale.pack(fill=tk.X, pady=2)

    def _create_status_panel(self, parent):
        """Create status display panel"""
        status_frame = ttk.LabelFrame(parent, text="📊 Current Status", padding=10)
        status_frame.pack(fill=tk.BOTH, padx=10, pady=5, expand=False)

        # Deck A info
        deck_a_frame = tk.Frame(status_frame, bg='#3a3a3a', relief=tk.RIDGE, borderwidth=2)
        deck_a_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(
            deck_a_frame,
            text="🔊 DECK A",
            font=('Arial', 12, 'bold'),
            bg='#3a3a3a',
            fg='#ff4444'
        ).pack(pady=5)

        self.deck_a_var = tk.StringVar(value="No track loaded")
        tk.Label(
            deck_a_frame,
            textvariable=self.deck_a_var,
            bg='#3a3a3a',
            fg='white',
            wraplength=200,
            justify=tk.CENTER
        ).pack(pady=5)

        # Deck B info
        deck_b_frame = tk.Frame(status_frame, bg='#3a3a3a', relief=tk.RIDGE, borderwidth=2)
        deck_b_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(
            deck_b_frame,
            text="🔊 DECK B",
            font=('Arial', 12, 'bold'),
            bg='#3a3a3a',
            fg='#4444ff'
        ).pack(pady=5)

        self.deck_b_var = tk.StringVar(value="No track loaded")
        tk.Label(
            deck_b_frame,
            textvariable=self.deck_b_var,
            bg='#3a3a3a',
            fg='white',
            wraplength=200,
            justify=tk.CENTER
        ).pack(pady=5)

        # Statistics
        stats_frame = tk.Frame(parent, bg='#2a2a2a')
        stats_frame.pack(fill=tk.X, padx=10, pady=5)

        self.stats_var = tk.StringVar(value="Tracks: 0 | Transitions: 0 | Elapsed: 0:00")
        tk.Label(
            stats_frame,
            textvariable=self.stats_var,
            bg='#2a2a2a',
            fg='#00ff88',
            font=('Courier', 10)
        ).pack()

    def _create_log_panel(self, parent):
        """Create log display"""
        log_frame = ttk.LabelFrame(parent, text="📝 System Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            bg='#1a1a1a',
            fg='#00ff88',
            font=('Courier', 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _log(self, message: str, level: str = "INFO"):
        """Add log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": "#00ff88",
            "WARNING": "#ffaa00",
            "ERROR": "#ff4444",
            "SUCCESS": "#00ffff"
        }

        self.log_text.insert(tk.END, f"[{timestamp}] {level}: {message}\n")
        self.log_text.see(tk.END)

    def _start_session(self):
        """Start autonomous session"""
        if self.running:
            messagebox.showwarning("Warning", "Session already running")
            return

        # Get config
        try:
            venue = self.venue_var.get()
            event = self.event_var.get()
            duration = float(self.duration_var.get())

            if duration <= 0:
                raise ValueError("Duration must be positive")

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid configuration: {e}")
            return

        # Disable start button
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Start in background thread
        self._log("🚀 Starting autonomous session...", "INFO")
        self._log(f"   Venue: {venue}", "INFO")
        self._log(f"   Event: {event}", "INFO")
        self._log(f"   Duration: {duration} hours", "INFO")

        self.running = True
        self.status_var.set("▶️ Running")

        # Create and start event loop thread
        self.loop_thread = threading.Thread(
            target=self._run_async_session,
            args=(venue, event, duration),
            daemon=True
        )
        self.loop_thread.start()

        # Start status update loop
        self._update_status()

    def _run_async_session(self, venue: str, event: str, duration: float):
        """Run async session in background thread"""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.event_loop = loop

            # Create DJ system
            config = DJConfig()
            self.dj = AutonomousDJMasterV3(config)

            # Run session
            loop.run_until_complete(self._async_session(venue, event, duration))

        except Exception as e:
            self._log(f"❌ Session error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
        finally:
            self.running = False
            self.root.after(0, self._session_ended)

    async def _async_session(self, venue: str, event: str, duration: float):
        """Async session logic"""
        # Initialize
        self._log("🔧 Initializing system...", "INFO")

        if not await self.dj.initialize():
            self._log("❌ Initialization failed!", "ERROR")
            return

        self._log("✅ System initialized", "SUCCESS")

        # Start session
        await self.dj.start_autonomous_session(venue, event, duration)

    def _stop_session(self):
        """Stop autonomous session"""
        if not self.running:
            return

        self._log("⏹️ Stopping session...", "WARNING")
        self.running = False

        if self.dj:
            self.dj.running = False

        self._session_ended()

    def _session_ended(self):
        """Handle session end"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("⏸️ Not Running")
        self._log("✅ Session ended", "INFO")

    def _skip_track(self):
        """Skip current track"""
        if not self.dj or not self.running:
            messagebox.showinfo("Info", "No active session")
            return

        self._log("⏭️ Skip track requested", "WARNING")
        # TODO: Implement skip logic

    def _toggle_pause(self):
        """Pause/resume session"""
        if not self.dj or not self.running:
            messagebox.showinfo("Info", "No active session")
            return

        if self.dj.paused:
            self.dj.paused = False
            self._log("▶️ Resumed", "INFO")
        else:
            self.dj.paused = True
            self._log("⏸️ Paused", "WARNING")

    def _update_energy(self, value):
        """Update target energy"""
        if self.dj and self.running:
            energy = float(value)
            self.dj.context.current_energy_level = energy
            self._log(f"🎚️ Energy target: {energy:.1f}", "INFO")

    def _update_status(self):
        """Update status display"""
        if not self.running:
            return

        try:
            if self.dj and self.dj.context:
                context = self.dj.context

                # Update deck info
                if context.deck_a_track:
                    track_a = context.deck_a_track
                    self.deck_a_var.set(f"{track_a.artist}\n{track_a.title}\n{track_a.bpm} BPM")
                else:
                    self.deck_a_var.set("No track")

                if context.deck_b_track:
                    track_b = context.deck_b_track
                    self.deck_b_var.set(f"{track_b.artist}\n{track_b.title}\n{track_b.bpm} BPM")
                else:
                    self.deck_b_var.set("No track")

                # Update stats
                elapsed_hours = context.get_elapsed_time_hours()
                elapsed_min = int(elapsed_hours * 60)
                stats_text = (
                    f"Tracks: {context.total_tracks_played} | "
                    f"Transitions: {context.successful_transitions} | "
                    f"Elapsed: {elapsed_min // 60}:{elapsed_min % 60:02d}"
                )
                self.stats_var.set(stats_text)

        except Exception as e:
            pass  # Ignore errors in status update

        # Schedule next update
        if self.running:
            self.root.after(1000, self._update_status)

    def run(self):
        """Start GUI"""
        self.root.mainloop()


if __name__ == "__main__":
    print("🎧 Launching Autonomous DJ GUI v3.0...")
    app = AutonomousGUIv3()
    app.run()