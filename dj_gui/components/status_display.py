"""
Real-time Status Display Component
Shows current track information, BPM, deck status, and audio levels
with real-time updates optimized for DJ monitoring.
"""

import tkinter as tk
from tkinter import ttk
import time
from typing import Dict, Any, Optional
import math
import logging

from ..themes.dj_dark_theme import DJTheme, create_themed_frame, create_themed_label
from ..utils.state_manager import get_state_manager, DeckStatus, DeckState, MixerStatus
from ..utils.threading_utils import TaskManager

logger = logging.getLogger(__name__)


class DeckStatusWidget:
    """Individual deck status display widget."""

    def __init__(self, parent, deck_id: str, theme: DJTheme, task_manager: TaskManager):
        self.parent = parent
        self.deck_id = deck_id
        self.theme = theme
        self.task_manager = task_manager

        # Create the deck widget
        self.frame = self._create_deck_widget()

    def _create_deck_widget(self) -> ttk.Frame:
        """Create deck status widget."""
        # Main deck frame with deck-specific color
        deck_frame = create_themed_frame(self.parent, "DJControl.TFrame")

        # Deck header
        header_frame = create_themed_frame(deck_frame, "DJ.TFrame")
        header_frame.pack(fill='x', padx=5, pady=5)

        deck_color = self.theme.create_deck_color(self.deck_id)

        # Deck label
        deck_label = create_themed_label(
            header_frame,
            f"DECK {self.deck_id}",
            "DJTitle.TLabel"
        )
        deck_label.configure(foreground=deck_color)
        deck_label.pack(side='left')

        # Deck state indicator
        self.state_indicator = create_themed_label(
            header_frame,
            "●",
            "DJDisplay.TLabel"
        )
        self.state_indicator.configure(foreground=self.theme.colors.STATUS_OFFLINE)
        self.state_indicator.pack(side='right')

        # Track info section
        track_frame = create_themed_frame(deck_frame, "DJ.TFrame")
        track_frame.pack(fill='x', padx=5, pady=5)

        # Track title
        self.track_title = create_themed_label(
            track_frame,
            "No Track Loaded",
            "DJ.TLabel"
        )
        self.track_title.pack(anchor='w')

        # Track artist
        self.track_artist = create_themed_label(
            track_frame,
            "",
            "DJStatus.TLabel"
        )
        self.track_artist.pack(anchor='w')

        # BPM and time section
        info_frame = create_themed_frame(deck_frame, "DJ.TFrame")
        info_frame.pack(fill='x', padx=5, pady=5)

        # BPM display
        bpm_frame = create_themed_frame(info_frame, "DJ.TFrame")
        bpm_frame.pack(side='left', expand=True, fill='x')

        bpm_label = create_themed_label(bpm_frame, "BPM:", "DJ.TLabel")
        bpm_label.pack(anchor='w')

        self.bpm_display = create_themed_label(
            bpm_frame,
            "000.0",
            "DJDisplay.TLabel"
        )
        self.bpm_display.configure(foreground=self.theme.colors.BPM_COLOR)
        self.bpm_display.pack(anchor='w')

        # Time display
        time_frame = create_themed_frame(info_frame, "DJ.TFrame")
        time_frame.pack(side='right')

        time_label = create_themed_label(time_frame, "TIME:", "DJ.TLabel")
        time_label.pack(anchor='e')

        self.time_display = create_themed_label(
            time_frame,
            "00:00",
            "DJDisplay.TLabel"
        )
        self.time_display.pack(anchor='e')

        # Progress bar
        progress_frame = create_themed_frame(deck_frame, "DJ.TFrame")
        progress_frame.pack(fill='x', padx=5, pady=5)

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            style="DJ.TProgressbar",
            mode='determinate',
            length=200
        )
        self.progress_bar.pack(fill='x')

        # Controls status
        controls_frame = create_themed_frame(deck_frame, "DJ.TFrame")
        controls_frame.pack(fill='x', padx=5, pady=5)

        # Sync indicator
        self.sync_indicator = create_themed_label(
            controls_frame,
            "SYNC",
            "DJStatus.TLabel"
        )
        self.sync_indicator.pack(side='left', padx=(0, 10))

        # Keylock indicator
        self.keylock_indicator = create_themed_label(
            controls_frame,
            "KEY",
            "DJStatus.TLabel"
        )
        self.keylock_indicator.pack(side='left', padx=(0, 10))

        # Loop indicator
        self.loop_indicator = create_themed_label(
            controls_frame,
            "LOOP",
            "DJStatus.TLabel"
        )
        self.loop_indicator.pack(side='left')

        # Pitch display
        self.pitch_display = create_themed_label(
            controls_frame,
            "+0.0%",
            "DJStatus.TLabel"
        )
        self.pitch_display.pack(side='right')

        return deck_frame

    def update_status(self, deck_status: DeckStatus):
        """Update deck status display."""
        # Update state indicator
        state_colors = {
            DeckState.PLAYING: self.theme.colors.STATUS_ONLINE,
            DeckState.PAUSED: self.theme.colors.STATUS_WARNING,
            DeckState.STOPPED: self.theme.colors.STATUS_OFFLINE,
            DeckState.CUEING: self.theme.colors.NEON_BLUE,
            DeckState.LOADING: self.theme.colors.STATUS_WARNING
        }
        self.state_indicator.configure(
            foreground=state_colors.get(deck_status.state, self.theme.colors.STATUS_NEUTRAL)
        )

        # Update track info
        if deck_status.track.title:
            self.track_title.configure(text=deck_status.track.title)
            if deck_status.track.artist:
                self.track_artist.configure(text=deck_status.track.artist)
            else:
                self.track_artist.configure(text="")
        else:
            self.track_title.configure(text="No Track Loaded")
            self.track_artist.configure(text="")

        # Update BPM
        if deck_status.bpm > 0:
            self.bpm_display.configure(text=f"{deck_status.bpm:.1f}")
        else:
            self.bpm_display.configure(text="000.0")

        # Update time and progress
        if deck_status.track.duration > 0:
            current_time = deck_status.position
            total_time = deck_status.track.duration

            # Format time display
            current_min = int(current_time // 60)
            current_sec = int(current_time % 60)
            total_min = int(total_time // 60)
            total_sec = int(total_time % 60)

            self.time_display.configure(
                text=f"{current_min:02d}:{current_sec:02d} / {total_min:02d}:{total_sec:02d}"
            )

            # Update progress bar
            progress = (current_time / total_time) * 100
            self.progress_bar['value'] = progress
        else:
            self.time_display.configure(text="00:00")
            self.progress_bar['value'] = 0

        # Update control indicators
        self._update_indicator(
            self.sync_indicator,
            deck_status.sync_enabled,
            "SYNC"
        )
        self._update_indicator(
            self.keylock_indicator,
            deck_status.keylock_enabled,
            "KEY"
        )
        self._update_indicator(
            self.loop_indicator,
            deck_status.loop_active,
            "LOOP"
        )

        # Update pitch display
        pitch_sign = "+" if deck_status.pitch >= 0 else ""
        self.pitch_display.configure(text=f"{pitch_sign}{deck_status.pitch:.1f}%")

    def _update_indicator(self, indicator_widget, active: bool, text: str):
        """Update status indicator appearance."""
        if active:
            indicator_widget.configure(
                text=text,
                foreground=self.theme.colors.NEON_BLUE
            )
        else:
            indicator_widget.configure(
                text=text,
                foreground=self.theme.colors.TEXT_DISABLED
            )


class CrossfaderWidget:
    """Crossfader position visualization widget."""

    def __init__(self, parent, theme: DJTheme):
        self.parent = parent
        self.theme = theme
        self.canvas = self._create_crossfader_widget()

    def _create_crossfader_widget(self) -> tk.Canvas:
        """Create crossfader visualization."""
        canvas = tk.Canvas(
            self.parent,
            height=60,
            bg=self.theme.colors.PRIMARY_DARK,
            highlightthickness=0
        )

        # Draw crossfader track
        canvas.create_rectangle(
            10, 25, 190, 35,
            fill=self.theme.colors.SLIDER_TRACK,
            outline=""
        )

        # Draw A and B labels
        canvas.create_text(
            25, 15,
            text="A",
            fill=self.theme.colors.DECK_A_COLOR,
            font=self.theme.get_font("sans", 12, "bold")
        )
        canvas.create_text(
            175, 15,
            text="B",
            fill=self.theme.colors.DECK_B_COLOR,
            font=self.theme.get_font("sans", 12, "bold")
        )

        # Draw center mark
        canvas.create_line(
            100, 20, 100, 40,
            fill=self.theme.colors.TEXT_SECONDARY,
            width=1
        )

        # Crossfader slider (will be updated)
        self.slider = canvas.create_oval(
            95, 20, 105, 40,
            fill=self.theme.colors.NEON_BLUE,
            outline=self.theme.colors.TEXT_PRIMARY,
            width=2
        )

        return canvas

    def update_position(self, position: float):
        """Update crossfader position (-1.0 to +1.0)."""
        # Convert position to canvas coordinates
        x_pos = 100 + (position * 80)  # 80 pixels range from center

        # Update slider position
        self.canvas.coords(self.slider, x_pos - 5, 20, x_pos + 5, 40)

        # Color based on position
        if abs(position) < 0.1:  # Center
            color = self.theme.colors.NEON_BLUE
        elif position < 0:  # A side
            color = self.theme.colors.DECK_A_COLOR
        else:  # B side
            color = self.theme.colors.DECK_B_COLOR

        self.canvas.itemconfig(self.slider, fill=color)


class AudioLevelMeter:
    """Audio level meter widget."""

    def __init__(self, parent, theme: DJTheme, label: str, orientation: str = "vertical"):
        self.parent = parent
        self.theme = theme
        self.label = label
        self.orientation = orientation
        self.level = 0.0
        self.peak_level = 0.0
        self.peak_hold_time = 0.0

        self.frame = self._create_meter()

    def _create_meter(self) -> ttk.Frame:
        """Create level meter widget."""
        frame = create_themed_frame(self.parent, "DJ.TFrame")

        # Label
        label_widget = create_themed_label(frame, self.label, "DJStatus.TLabel")
        label_widget.pack(pady=(0, 5))

        # Meter canvas
        if self.orientation == "vertical":
            self.canvas = tk.Canvas(
                frame,
                width=20,
                height=100,
                bg=self.theme.colors.PRIMARY_DARK,
                highlightthickness=0
            )
        else:
            self.canvas = tk.Canvas(
                frame,
                width=100,
                height=20,
                bg=self.theme.colors.PRIMARY_DARK,
                highlightthickness=0
            )

        self.canvas.pack()

        # Draw meter background
        self._draw_meter_background()

        return frame

    def _draw_meter_background(self):
        """Draw meter background and scale."""
        if self.orientation == "vertical":
            # Vertical meter
            self.canvas.create_rectangle(
                5, 5, 15, 95,
                fill=self.theme.colors.SLIDER_TRACK,
                outline=""
            )
            # Scale marks
            for i in range(0, 101, 20):
                y = 95 - (i * 0.9)
                self.canvas.create_line(
                    2, y, 4, y,
                    fill=self.theme.colors.TEXT_SECONDARY
                )
        else:
            # Horizontal meter
            self.canvas.create_rectangle(
                5, 5, 95, 15,
                fill=self.theme.colors.SLIDER_TRACK,
                outline=""
            )
            # Scale marks
            for i in range(0, 101, 20):
                x = 5 + (i * 0.9)
                self.canvas.create_line(
                    x, 2, x, 4,
                    fill=self.theme.colors.TEXT_SECONDARY
                )

        # Level bar (will be updated)
        self.level_bar = self.canvas.create_rectangle(
            0, 0, 0, 0,
            fill=self.theme.colors.LEVEL_COLOR,
            outline=""
        )

        # Peak indicator
        self.peak_indicator = self.canvas.create_line(
            0, 0, 0, 0,
            fill=self.theme.colors.LEVEL_PEAK,
            width=2
        )

    def update_level(self, level: float):
        """Update audio level (0.0 to 1.0)."""
        self.level = max(0.0, min(1.0, level))

        # Update peak hold
        current_time = time.time()
        if self.level > self.peak_level or (current_time - self.peak_hold_time) > 2.0:
            self.peak_level = self.level
            self.peak_hold_time = current_time

        # Update visual elements
        if self.orientation == "vertical":
            # Vertical level bar
            bar_height = self.level * 90
            self.canvas.coords(
                self.level_bar,
                5, 95 - bar_height, 15, 95
            )

            # Peak indicator line
            peak_y = 95 - (self.peak_level * 90)
            self.canvas.coords(
                self.peak_indicator,
                3, peak_y, 17, peak_y
            )
        else:
            # Horizontal level bar
            bar_width = self.level * 90
            self.canvas.coords(
                self.level_bar,
                5, 5, 5 + bar_width, 15
            )

            # Peak indicator line
            peak_x = 5 + (self.peak_level * 90)
            self.canvas.coords(
                self.peak_indicator,
                peak_x, 3, peak_x, 17
            )

        # Color coding based on level
        if self.level > 0.9:  # Peak/red zone
            color = self.theme.colors.LEVEL_PEAK
        elif self.level > 0.7:  # Warning/orange zone
            color = self.theme.colors.STATUS_WARNING
        else:  # Normal/blue zone
            color = self.theme.colors.LEVEL_COLOR

        self.canvas.itemconfig(self.level_bar, fill=color)


class StatusDisplay:
    """
    Main status display component combining all status widgets.
    Shows real-time information about decks, mixer, and audio levels.
    """

    def __init__(self, parent, theme: DJTheme, task_manager: TaskManager):
        self.parent = parent
        self.theme = theme
        self.task_manager = task_manager
        self.state_manager = get_state_manager()

        # Create the main display
        self.frame = self._create_status_display()
        self._setup_observers()

        logger.info("Status Display initialized")

    def _create_status_display(self) -> ttk.Frame:
        """Create the complete status display."""
        # Main status frame
        status_frame = create_themed_frame(self.parent, "DJPanel.TFrame")

        # Title
        title_label = create_themed_label(status_frame, "📊 SYSTEM STATUS", "DJTitle.TLabel")
        title_label.pack(pady=(10, 15))

        # Deck status section
        deck_section = create_themed_frame(status_frame, "DJ.TFrame")
        deck_section.pack(fill='x', padx=10, pady=5)

        # Deck A and B widgets
        decks_frame = create_themed_frame(deck_section, "DJ.TFrame")
        decks_frame.pack(fill='x', pady=5)

        # Deck A
        deck_a_frame = create_themed_frame(decks_frame, "DJ.TFrame")
        deck_a_frame.pack(side='left', expand=True, fill='both', padx=(0, 5))
        self.deck_a_widget = DeckStatusWidget(deck_a_frame, "A", self.theme, self.task_manager)

        # Deck B
        deck_b_frame = create_themed_frame(decks_frame, "DJ.TFrame")
        deck_b_frame.pack(side='right', expand=True, fill='both', padx=(5, 0))
        self.deck_b_widget = DeckStatusWidget(deck_b_frame, "B", self.theme, self.task_manager)

        # Crossfader section
        crossfader_section = create_themed_frame(status_frame, "DJ.TFrame")
        crossfader_section.pack(fill='x', padx=10, pady=10)

        crossfader_label = create_themed_label(
            crossfader_section,
            "Crossfader Position",
            "DJ.TLabel"
        )
        crossfader_label.pack()

        self.crossfader_widget = CrossfaderWidget(crossfader_section, self.theme)
        self.crossfader_widget.canvas.pack(pady=5)

        # Audio levels section
        levels_section = create_themed_frame(status_frame, "DJControl.TFrame")
        levels_section.pack(fill='x', padx=10, pady=10)

        levels_title = create_themed_label(
            levels_section,
            "Audio Levels",
            "DJTitle.TLabel"
        )
        levels_title.pack(pady=(5, 10))

        # Level meters
        meters_frame = create_themed_frame(levels_section, "DJ.TFrame")
        meters_frame.pack(fill='x', pady=5)

        # Master levels
        master_frame = create_themed_frame(meters_frame, "DJ.TFrame")
        master_frame.pack(side='left', padx=10)

        self.master_left_meter = AudioLevelMeter(
            master_frame, self.theme, "MASTER L"
        )
        self.master_left_meter.frame.pack(side='left', padx=(0, 5))

        self.master_right_meter = AudioLevelMeter(
            master_frame, self.theme, "MASTER R"
        )
        self.master_right_meter.frame.pack(side='left')

        # Deck A levels
        deck_a_levels_frame = create_themed_frame(meters_frame, "DJ.TFrame")
        deck_a_levels_frame.pack(side='left', padx=10)

        self.deck_a_left_meter = AudioLevelMeter(
            deck_a_levels_frame, self.theme, "DECK A L"
        )
        self.deck_a_left_meter.frame.pack(side='left', padx=(0, 5))

        self.deck_a_right_meter = AudioLevelMeter(
            deck_a_levels_frame, self.theme, "DECK A R"
        )
        self.deck_a_right_meter.frame.pack(side='left')

        # Deck B levels
        deck_b_levels_frame = create_themed_frame(meters_frame, "DJ.TFrame")
        deck_b_levels_frame.pack(side='right', padx=10)

        self.deck_b_left_meter = AudioLevelMeter(
            deck_b_levels_frame, self.theme, "DECK B L"
        )
        self.deck_b_left_meter.frame.pack(side='left', padx=(0, 5))

        self.deck_b_right_meter = AudioLevelMeter(
            deck_b_levels_frame, self.theme, "DECK B R"
        )
        self.deck_b_right_meter.frame.pack(side='left')

        return status_frame

    def _setup_observers(self):
        """Setup state change observers."""
        self.state_manager.subscribe('deck_update', self._on_deck_update)
        self.state_manager.subscribe('mixer_update', self._on_mixer_update)
        self.state_manager.subscribe('audio_levels', self._on_audio_levels_update)

        # Start periodic updates for smooth display
        self.task_manager.start_periodic_task(
            'status_display_update',
            0.1,  # 10 FPS for smooth level meters
            self._periodic_update
        )

    def _on_deck_update(self, data):
        """Handle deck status updates."""
        deck_id = data['deck_id']
        deck_status = data['deck_status']

        # Schedule GUI update
        if deck_id.upper() == "A":
            self.task_manager.schedule_gui_update(
                self.deck_a_widget.update_status,
                deck_status
            )
        elif deck_id.upper() == "B":
            self.task_manager.schedule_gui_update(
                self.deck_b_widget.update_status,
                deck_status
            )

    def _on_mixer_update(self, data):
        """Handle mixer status updates."""
        mixer_status: MixerStatus = data['mixer_status']

        # Update crossfader
        self.task_manager.schedule_gui_update(
            self.crossfader_widget.update_position,
            mixer_status.crossfader_position
        )

    def _on_audio_levels_update(self, data):
        """Handle audio level updates."""
        levels = data['levels']

        # Schedule level meter updates
        if 'master_left' in levels:
            self.task_manager.schedule_gui_update(
                self.master_left_meter.update_level,
                levels['master_left']
            )
        if 'master_right' in levels:
            self.task_manager.schedule_gui_update(
                self.master_right_meter.update_level,
                levels['master_right']
            )
        if 'deck_a_left' in levels:
            self.task_manager.schedule_gui_update(
                self.deck_a_left_meter.update_level,
                levels['deck_a_left']
            )
        if 'deck_a_right' in levels:
            self.task_manager.schedule_gui_update(
                self.deck_a_right_meter.update_level,
                levels['deck_a_right']
            )
        if 'deck_b_left' in levels:
            self.task_manager.schedule_gui_update(
                self.deck_b_left_meter.update_level,
                levels['deck_b_left']
            )
        if 'deck_b_right' in levels:
            self.task_manager.schedule_gui_update(
                self.deck_b_right_meter.update_level,
                levels['deck_b_right']
            )

    def _periodic_update(self):
        """Periodic update for smooth animations."""
        # This can be used for time-based animations or smooth level decay
        pass

    def get_frame(self) -> ttk.Frame:
        """Get the main status display frame."""
        return self.frame

    def cleanup(self):
        """Cleanup resources."""
        # Stop periodic tasks
        self.task_manager.stop_periodic_task('status_display_update')

        # Unsubscribe from events
        self.state_manager.unsubscribe('deck_update', self._on_deck_update)
        self.state_manager.unsubscribe('mixer_update', self._on_mixer_update)
        self.state_manager.unsubscribe('audio_levels', self._on_audio_levels_update)

        logger.info("Status Display cleanup complete")


# Export the main class
__all__ = ['StatusDisplay']