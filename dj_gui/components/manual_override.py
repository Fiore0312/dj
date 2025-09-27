"""
Manual Override Panel Component
Provides emergency controls and manual overrides for the DJ system,
including crossfader control, EQ adjustments, and emergency stops.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, Dict, Any
import logging

from ..themes.dj_dark_theme import DJTheme, create_themed_frame, create_themed_label, create_themed_button
from ..utils.state_manager import get_state_manager, DJState, DeckState
from ..utils.threading_utils import TaskManager

logger = logging.getLogger(__name__)


class EQControl:
    """EQ control widget for a single deck."""

    def __init__(self, parent, deck_id: str, theme: DJTheme, task_manager: TaskManager):
        self.parent = parent
        self.deck_id = deck_id
        self.theme = theme
        self.task_manager = task_manager
        self.state_manager = get_state_manager()

        # EQ values (-1.0 to +1.0)
        self.eq_high = tk.DoubleVar(value=0.0)
        self.eq_mid = tk.DoubleVar(value=0.0)
        self.eq_low = tk.DoubleVar(value=0.0)

        # Callback for EQ changes
        self.eq_change_callback: Optional[Callable[[str, str, float], None]] = None

        self.frame = self._create_eq_control()

    def _create_eq_control(self) -> ttk.Frame:
        """Create EQ control widget."""
        eq_frame = create_themed_frame(self.parent, "DJControl.TFrame")

        # Title
        deck_color = self.theme.create_deck_color(self.deck_id)
        title_label = create_themed_label(
            eq_frame,
            f"DECK {self.deck_id} EQ",
            "DJTitle.TLabel"
        )
        title_label.configure(foreground=deck_color)
        title_label.pack(pady=(5, 10))

        # High EQ
        self._create_eq_knob(eq_frame, "HIGH", self.eq_high, self.theme.colors.NEON_RED)

        # Mid EQ
        self._create_eq_knob(eq_frame, "MID", self.eq_mid, self.theme.colors.NEON_ORANGE)

        # Low EQ
        self._create_eq_knob(eq_frame, "LOW", self.eq_low, self.theme.colors.NEON_BLUE)

        # Reset button
        reset_button = create_themed_button(
            eq_frame,
            "RESET EQ",
            command=self._reset_eq,
            style_name="DJ.TButton"
        )
        reset_button.pack(pady=10)

        return eq_frame

    def _create_eq_knob(self, parent, label: str, var: tk.DoubleVar, color: str):
        """Create individual EQ knob control."""
        knob_frame = create_themed_frame(parent, "DJ.TFrame")
        knob_frame.pack(pady=5)

        # Label
        eq_label = create_themed_label(knob_frame, label, "DJ.TLabel")
        eq_label.configure(foreground=color)
        eq_label.pack()

        # Scale control
        eq_scale = ttk.Scale(
            knob_frame,
            from_=-1.0, to=1.0,
            orient='horizontal',
            variable=var,
            style="DJ.TScale",
            length=80,
            command=lambda value, band=label.lower(): self._on_eq_change(band, value)
        )
        eq_scale.pack(pady=5)

        # Value display
        value_label = create_themed_label(knob_frame, "0.0", "DJStatus.TLabel")
        value_label.pack()

        # Update value display when variable changes
        def update_display(*args):
            value = var.get()
            value_label.configure(text=f"{value:+.1f}")

        var.trace_add('write', update_display)

    def _on_eq_change(self, band: str, value):
        """Handle EQ value change."""
        eq_value = float(value)

        # Update state
        eq_update = {f'eq_{band}': eq_value}
        self.state_manager.update_deck(self.deck_id, **eq_update)

        # Call external callback
        if self.eq_change_callback:
            self.eq_change_callback(self.deck_id, band, eq_value)

        logger.debug(f"Deck {self.deck_id} {band.upper()} EQ: {eq_value:+.1f}")

    def _reset_eq(self):
        """Reset all EQ values to neutral."""
        self.eq_high.set(0.0)
        self.eq_mid.set(0.0)
        self.eq_low.set(0.0)

        # Update state
        self.state_manager.update_deck(
            self.deck_id,
            eq_high=0.0,
            eq_mid=0.0,
            eq_low=0.0
        )

        logger.info(f"Deck {self.deck_id} EQ reset to neutral")

    def set_eq_values(self, high: float, mid: float, low: float):
        """Set EQ values programmatically."""
        self.eq_high.set(high)
        self.eq_mid.set(mid)
        self.eq_low.set(low)

    def set_eq_change_callback(self, callback: Callable[[str, str, float], None]):
        """Set callback for EQ changes."""
        self.eq_change_callback = callback


class CrossfaderControl:
    """Manual crossfader control widget."""

    def __init__(self, parent, theme: DJTheme, task_manager: TaskManager):
        self.parent = parent
        self.theme = theme
        self.task_manager = task_manager
        self.state_manager = get_state_manager()

        # Crossfader position (-1.0 to +1.0)
        self.crossfader_position = tk.DoubleVar(value=0.0)

        # Callback for crossfader changes
        self.crossfader_change_callback: Optional[Callable[[float], None]] = None

        self.frame = self._create_crossfader_control()

    def _create_crossfader_control(self) -> ttk.Frame:
        """Create crossfader control widget."""
        crossfader_frame = create_themed_frame(self.parent, "DJControl.TFrame")

        # Title
        title_label = create_themed_label(
            crossfader_frame,
            "CROSSFADER OVERRIDE",
            "DJTitle.TLabel"
        )
        title_label.pack(pady=(10, 15))

        # Crossfader control
        control_frame = create_themed_frame(crossfader_frame, "DJ.TFrame")
        control_frame.pack(fill='x', padx=10, pady=10)

        # A and B labels
        label_frame = create_themed_frame(control_frame, "DJ.TFrame")
        label_frame.pack(fill='x', pady=(0, 5))

        a_label = create_themed_label(label_frame, "A", "DJDisplay.TLabel")
        a_label.configure(foreground=self.theme.colors.DECK_A_COLOR)
        a_label.pack(side='left')

        center_label = create_themed_label(label_frame, "CENTER", "DJStatus.TLabel")
        center_label.pack()

        b_label = create_themed_label(label_frame, "B", "DJDisplay.TLabel")
        b_label.configure(foreground=self.theme.colors.DECK_B_COLOR)
        b_label.pack(side='right')

        # Crossfader scale
        self.crossfader_scale = ttk.Scale(
            control_frame,
            from_=-1.0, to=1.0,
            orient='horizontal',
            variable=self.crossfader_position,
            style="DJ.TScale",
            length=200,
            command=self._on_crossfader_change
        )
        self.crossfader_scale.pack(pady=5)

        # Position display
        self.position_display = create_themed_label(
            control_frame,
            "CENTER",
            "DJDisplay.TLabel"
        )
        self.position_display.pack(pady=5)

        # Quick position buttons
        button_frame = create_themed_frame(control_frame, "DJ.TFrame")
        button_frame.pack(pady=10)

        a_button = create_themed_button(
            button_frame,
            "FULL A",
            command=lambda: self._set_position(-1.0),
            style_name="DJ.TButton"
        )
        a_button.pack(side='left', padx=5)

        center_button = create_themed_button(
            button_frame,
            "CENTER",
            command=lambda: self._set_position(0.0),
            style_name="DJ.TButton"
        )
        center_button.pack(side='left', padx=5)

        b_button = create_themed_button(
            button_frame,
            "FULL B",
            command=lambda: self._set_position(1.0),
            style_name="DJ.TButton"
        )
        b_button.pack(side='left', padx=5)

        return crossfader_frame

    def _on_crossfader_change(self, value):
        """Handle crossfader position change."""
        position = float(value)

        # Update display
        if position < -0.8:
            display_text = "FULL A"
        elif position < -0.2:
            display_text = f"A {abs(position)*100:.0f}%"
        elif position < 0.2:
            display_text = "CENTER"
        elif position < 0.8:
            display_text = f"B {position*100:.0f}%"
        else:
            display_text = "FULL B"

        self.position_display.configure(text=display_text)

        # Update state
        self.state_manager.update_mixer(crossfader_position=position)

        # Call external callback
        if self.crossfader_change_callback:
            self.crossfader_change_callback(position)

        logger.debug(f"Crossfader position: {position:+.2f}")

    def _set_position(self, position: float):
        """Set crossfader to specific position."""
        self.crossfader_position.set(position)

    def set_crossfader_change_callback(self, callback: Callable[[float], None]):
        """Set callback for crossfader changes."""
        self.crossfader_change_callback = callback


class ManualOverridePanel:
    """
    Manual Override Panel component.
    Provides emergency controls and manual overrides for DJ system.
    """

    def __init__(self, parent, theme: DJTheme, task_manager: TaskManager):
        self.parent = parent
        self.theme = theme
        self.task_manager = task_manager
        self.state_manager = get_state_manager()

        # Override state
        self.override_active = tk.BooleanVar(value=False)

        # Callbacks
        self.emergency_stop_callback: Optional[Callable[[], None]] = None
        self.take_control_callback: Optional[Callable[[bool], None]] = None

        # Create the panel
        self.frame = self._create_panel()
        self._setup_observers()

        logger.info("Manual Override Panel initialized")

    def _create_panel(self) -> ttk.Frame:
        """Create the manual override panel UI."""
        # Main panel frame
        panel = create_themed_frame(self.parent, "DJPanel.TFrame")

        # Title
        title_label = create_themed_label(panel, "🚨 MANUAL OVERRIDE", "DJTitle.TLabel")
        title_label.pack(pady=(10, 15))

        # Emergency controls section
        self._create_emergency_section(panel)

        # Separator
        ttk.Separator(panel, orient='horizontal').pack(fill='x', pady=10)

        # Manual control section
        self._create_manual_control_section(panel)

        # Separator
        ttk.Separator(panel, orient='horizontal').pack(fill='x', pady=10)

        # EQ controls section
        self._create_eq_section(panel)

        return panel

    def _create_emergency_section(self, parent):
        """Create emergency controls section."""
        emergency_frame = create_themed_frame(parent, "DJ.TFrame")
        emergency_frame.pack(fill='x', padx=10, pady=5)

        # Emergency stop button
        self.emergency_button = create_themed_button(
            emergency_frame,
            "🛑 EMERGENCY STOP",
            command=self._emergency_stop,
            style_name="DJDanger.TButton"
        )
        self.emergency_button.pack(fill='x', pady=5)

        # Take control toggle
        self.take_control_button = create_themed_button(
            emergency_frame,
            "TAKE MANUAL CONTROL",
            command=self._toggle_manual_control,
            style_name="DJActive.TButton"
        )
        self.take_control_button.pack(fill='x', pady=5)

        # Override status
        self.override_status = create_themed_label(
            emergency_frame,
            "Agent Control Active",
            "DJStatus.TLabel"
        )
        self.override_status.pack(pady=5)

    def _create_manual_control_section(self, parent):
        """Create manual control section."""
        control_frame = create_themed_frame(parent, "DJ.TFrame")
        control_frame.pack(fill='x', padx=10, pady=5)

        # Deck control buttons
        deck_control_frame = create_themed_frame(control_frame, "DJ.TFrame")
        deck_control_frame.pack(fill='x', pady=5)

        # Deck A controls
        deck_a_frame = create_themed_frame(deck_control_frame, "DJ.TFrame")
        deck_a_frame.pack(side='left', expand=True, fill='x', padx=(0, 5))

        deck_a_title = create_themed_label(deck_a_frame, "DECK A", "DJTitle.TLabel")
        deck_a_title.configure(foreground=self.theme.colors.DECK_A_COLOR)
        deck_a_title.pack()

        self.deck_a_play_button = create_themed_button(
            deck_a_frame,
            "PLAY",
            command=lambda: self._deck_control("A", "play"),
            style_name="DJ.TButton"
        )
        self.deck_a_play_button.pack(fill='x', pady=2)

        self.deck_a_pause_button = create_themed_button(
            deck_a_frame,
            "PAUSE",
            command=lambda: self._deck_control("A", "pause"),
            style_name="DJ.TButton"
        )
        self.deck_a_pause_button.pack(fill='x', pady=2)

        self.deck_a_stop_button = create_themed_button(
            deck_a_frame,
            "STOP",
            command=lambda: self._deck_control("A", "stop"),
            style_name="DJDanger.TButton"
        )
        self.deck_a_stop_button.pack(fill='x', pady=2)

        # Deck B controls
        deck_b_frame = create_themed_frame(deck_control_frame, "DJ.TFrame")
        deck_b_frame.pack(side='right', expand=True, fill='x', padx=(5, 0))

        deck_b_title = create_themed_label(deck_b_frame, "DECK B", "DJTitle.TLabel")
        deck_b_title.configure(foreground=self.theme.colors.DECK_B_COLOR)
        deck_b_title.pack()

        self.deck_b_play_button = create_themed_button(
            deck_b_frame,
            "PLAY",
            command=lambda: self._deck_control("B", "play"),
            style_name="DJ.TButton"
        )
        self.deck_b_play_button.pack(fill='x', pady=2)

        self.deck_b_pause_button = create_themed_button(
            deck_b_frame,
            "PAUSE",
            command=lambda: self._deck_control("B", "pause"),
            style_name="DJ.TButton"
        )
        self.deck_b_pause_button.pack(fill='x', pady=2)

        self.deck_b_stop_button = create_themed_button(
            deck_b_frame,
            "STOP",
            command=lambda: self._deck_control("B", "stop"),
            style_name="DJDanger.TButton"
        )
        self.deck_b_stop_button.pack(fill='x', pady=2)

        # Initially disable manual controls
        self._set_manual_controls_state('disabled')

    def _create_eq_section(self, parent):
        """Create EQ controls section."""
        eq_section_frame = create_themed_frame(parent, "DJ.TFrame")
        eq_section_frame.pack(fill='x', padx=10, pady=5)

        eq_title = create_themed_label(eq_section_frame, "EQ CONTROLS", "DJTitle.TLabel")
        eq_title.pack(pady=(0, 10))

        # EQ controls container
        eq_container = create_themed_frame(eq_section_frame, "DJ.TFrame")
        eq_container.pack(fill='x')

        # Deck A EQ
        deck_a_eq_frame = create_themed_frame(eq_container, "DJ.TFrame")
        deck_a_eq_frame.pack(side='left', expand=True, fill='both', padx=(0, 5))
        self.deck_a_eq = EQControl(deck_a_eq_frame, "A", self.theme, self.task_manager)

        # Deck B EQ
        deck_b_eq_frame = create_themed_frame(eq_container, "DJ.TFrame")
        deck_b_eq_frame.pack(side='right', expand=True, fill='both', padx=(5, 0))
        self.deck_b_eq = EQControl(deck_b_eq_frame, "B", self.theme, self.task_manager)

        # Crossfader control
        crossfader_frame = create_themed_frame(eq_section_frame, "DJ.TFrame")
        crossfader_frame.pack(fill='x', pady=(10, 0))
        self.crossfader_control = CrossfaderControl(crossfader_frame, self.theme, self.task_manager)

    def _setup_observers(self):
        """Setup state change observers."""
        self.state_manager.subscribe('state_change', self._on_state_change)

    def _emergency_stop(self):
        """Execute emergency stop."""
        try:
            # Confirm emergency stop
            result = messagebox.askyesno(
                "Emergency Stop",
                "This will immediately stop all decks and disable the agent.\n\nContinue?",
                icon='warning'
            )

            if result:
                # Update state
                self.state_manager.update_dj_state(DJState.STOPPED)
                self.state_manager.update_deck("A", state=DeckState.STOPPED)
                self.state_manager.update_deck("B", state=DeckState.STOPPED)
                self.state_manager.update_agent(active=False, current_action="Emergency Stop")

                # Call external callback
                if self.emergency_stop_callback:
                    self.task_manager.submit_background_task(
                        'emergency_stop',
                        self.emergency_stop_callback
                    )

                logger.warning("Emergency stop executed")

        except Exception as e:
            logger.error(f"Error during emergency stop: {e}")
            messagebox.showerror("Error", f"Emergency stop failed: {e}")

    def _toggle_manual_control(self):
        """Toggle manual control mode."""
        try:
            current_state = self.override_active.get()
            new_state = not current_state

            if new_state:
                # Taking manual control
                result = messagebox.askyesno(
                    "Manual Control",
                    "This will disable the AI agent and give you full manual control.\n\nContinue?",
                    icon='question'
                )

                if result:
                    self.override_active.set(True)
                    self.take_control_button.configure(text="RETURN TO AGENT")
                    self.override_status.configure(
                        text="Manual Control Active",
                        foreground=self.theme.colors.STATUS_WARNING
                    )
                    self._set_manual_controls_state('normal')

                    # Update state
                    self.state_manager.update_agent(active=False, current_action="Manual Override")

                    # Call external callback
                    if self.take_control_callback:
                        self.task_manager.submit_background_task(
                            'take_control',
                            self.take_control_callback,
                            True
                        )

                    logger.info("Manual control activated")

            else:
                # Returning to agent control
                self.override_active.set(False)
                self.take_control_button.configure(text="TAKE MANUAL CONTROL")
                self.override_status.configure(
                    text="Agent Control Active",
                    foreground=self.theme.colors.STATUS_ONLINE
                )
                self._set_manual_controls_state('disabled')

                # Call external callback
                if self.take_control_callback:
                    self.task_manager.submit_background_task(
                        'return_control',
                        self.take_control_callback,
                        False
                    )

                logger.info("Returned to agent control")

        except Exception as e:
            logger.error(f"Error toggling manual control: {e}")
            messagebox.showerror("Error", f"Failed to toggle control: {e}")

    def _deck_control(self, deck_id: str, action: str):
        """Execute deck control action."""
        try:
            if action == "play":
                new_state = DeckState.PLAYING
            elif action == "pause":
                new_state = DeckState.PAUSED
            elif action == "stop":
                new_state = DeckState.STOPPED
            else:
                logger.warning(f"Unknown deck action: {action}")
                return

            # Update state
            self.state_manager.update_deck(deck_id, state=new_state)

            logger.info(f"Manual deck control: Deck {deck_id} {action}")

        except Exception as e:
            logger.error(f"Error in deck control: {e}")
            messagebox.showerror("Error", f"Deck control failed: {e}")

    def _set_manual_controls_state(self, state: str):
        """Enable or disable manual controls."""
        controls = [
            self.deck_a_play_button,
            self.deck_a_pause_button,
            self.deck_a_stop_button,
            self.deck_b_play_button,
            self.deck_b_pause_button,
            self.deck_b_stop_button,
        ]

        for control in controls:
            control.configure(state=state)

    def _on_state_change(self, data):
        """Handle overall state changes."""
        new_state = data['new_state']

        # Update UI based on system state
        if new_state == DJState.ERROR:
            self.task_manager.schedule_gui_update(
                self.override_status.configure,
                text="SYSTEM ERROR",
                foreground=self.theme.colors.STATUS_OFFLINE
            )

    def set_emergency_stop_callback(self, callback: Callable[[], None]):
        """Set callback for emergency stop."""
        self.emergency_stop_callback = callback

    def set_take_control_callback(self, callback: Callable[[bool], None]):
        """Set callback for manual control toggle."""
        self.take_control_callback = callback

    def set_eq_change_callback(self, callback: Callable[[str, str, float], None]):
        """Set callback for EQ changes."""
        self.deck_a_eq.set_eq_change_callback(callback)
        self.deck_b_eq.set_eq_change_callback(callback)

    def set_crossfader_change_callback(self, callback: Callable[[float], None]):
        """Set callback for crossfader changes."""
        self.crossfader_control.set_crossfader_change_callback(callback)

    def get_frame(self) -> ttk.Frame:
        """Get the main panel frame."""
        return self.frame

    def force_manual_mode(self):
        """Force manual control mode (for emergencies)."""
        if not self.override_active.get():
            self.override_active.set(True)
            self.take_control_button.configure(text="RETURN TO AGENT")
            self.override_status.configure(
                text="Manual Control Active (Forced)",
                foreground=self.theme.colors.STATUS_WARNING
            )
            self._set_manual_controls_state('normal')

    def get_current_settings(self) -> Dict[str, Any]:
        """Get current override settings."""
        return {
            'override_active': self.override_active.get(),
            'crossfader_position': self.crossfader_control.crossfader_position.get(),
            'deck_a_eq': {
                'high': self.deck_a_eq.eq_high.get(),
                'mid': self.deck_a_eq.eq_mid.get(),
                'low': self.deck_a_eq.eq_low.get()
            },
            'deck_b_eq': {
                'high': self.deck_b_eq.eq_high.get(),
                'mid': self.deck_b_eq.eq_mid.get(),
                'low': self.deck_b_eq.eq_low.get()
            }
        }

    def cleanup(self):
        """Cleanup resources."""
        # Unsubscribe from events
        self.state_manager.unsubscribe('state_change', self._on_state_change)

        logger.info("Manual Override Panel cleanup complete")


# Export the main class
__all__ = ['ManualOverridePanel']