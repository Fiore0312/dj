"""
DJ Dark Theme System
Complete dark theme optimized for DJ environments with low-light visibility
and professional aesthetics.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Tuple, Optional


class DJColors:
    """DJ-optimized color palette for low-light environments."""

    # Primary DJ colors
    PRIMARY_DARK = "#1a1a1a"      # Main background
    SECONDARY_DARK = "#2d2d2d"    # Secondary backgrounds
    TERTIARY_DARK = "#3d3d3d"     # Raised elements

    # Text colors
    TEXT_PRIMARY = "#ffffff"      # Main text
    TEXT_SECONDARY = "#cccccc"    # Secondary text
    TEXT_DISABLED = "#666666"     # Disabled text

    # Accent colors
    NEON_BLUE = "#00d4ff"        # Active elements
    NEON_GREEN = "#00ff88"       # Success/play states
    NEON_RED = "#ff3366"         # Error/stop states
    NEON_ORANGE = "#ff6600"      # Warning states
    NEON_PURPLE = "#cc66ff"      # Special functions

    # Deck colors
    DECK_A_COLOR = "#0099ff"     # Deck A accent
    DECK_B_COLOR = "#ff9900"     # Deck B accent

    # Control colors
    SLIDER_TRACK = "#4d4d4d"     # Slider backgrounds
    SLIDER_ACTIVE = "#00d4ff"    # Active sliders
    BUTTON_NORMAL = "#3d3d3d"    # Normal buttons
    BUTTON_ACTIVE = "#00d4ff"    # Active buttons
    BUTTON_HOVER = "#4d4d4d"     # Hover state

    # Visualization colors
    WAVEFORM_COLOR = "#00d4ff"   # Waveform display
    BPM_COLOR = "#00ff88"        # BPM indicators
    LEVEL_COLOR = "#00d4ff"      # Audio levels
    LEVEL_PEAK = "#ff3366"       # Peak levels

    # Status colors
    STATUS_ONLINE = "#00ff88"    # Connected/online
    STATUS_OFFLINE = "#ff3366"   # Disconnected/offline
    STATUS_WARNING = "#ff6600"   # Warning states
    STATUS_NEUTRAL = "#cccccc"   # Neutral states


class DJFonts:
    """Font specifications for DJ interface."""

    # Font families (fallback order)
    MONO_FAMILY = ("JetBrains Mono", "Monaco", "Consolas", "monospace")
    SANS_FAMILY = ("Inter", "Segoe UI", "Arial", "sans-serif")

    # Font sizes
    DISPLAY_SIZE = 24     # Large displays (BPM, time)
    TITLE_SIZE = 16       # Section titles
    NORMAL_SIZE = 12      # Normal text
    SMALL_SIZE = 10       # Small labels
    TINY_SIZE = 8         # Tiny indicators

    # Font weights
    LIGHT = "light"
    NORMAL = "normal"
    BOLD = "bold"


class DJDimensions:
    """Standard dimensions and spacing for DJ interface."""

    # Padding and margins
    PADDING_SMALL = 4
    PADDING_NORMAL = 8
    PADDING_LARGE = 16
    PADDING_XLARGE = 24

    # Widget sizes
    BUTTON_HEIGHT = 32
    BUTTON_WIDTH = 80
    SLIDER_WIDTH = 24
    SLIDER_LENGTH = 200

    # Panel sizes
    CONTROL_PANEL_WIDTH = 300
    STATUS_PANEL_HEIGHT = 120
    LIBRARY_PANEL_HEIGHT = 400

    # Border and corner radius
    BORDER_WIDTH = 1
    CORNER_RADIUS = 4


class DJTheme:
    """
    Main DJ theme class that applies dark theme styling to tkinter widgets.
    Optimized for low-light DJ booth environments.
    """

    def __init__(self):
        self.colors = DJColors()
        self.fonts = DJFonts()
        self.dimensions = DJDimensions()
        self._style = None

    def apply_theme(self, root: tk.Tk) -> ttk.Style:
        """
        Apply DJ dark theme to the root window and create styled ttk widgets.

        Args:
            root: Root tkinter window

        Returns:
            Configured ttk.Style instance
        """
        # Configure root window
        root.configure(bg=self.colors.PRIMARY_DARK)
        root.option_add("*Background", self.colors.PRIMARY_DARK)
        root.option_add("*Foreground", self.colors.TEXT_PRIMARY)
        root.option_add("*selectBackground", self.colors.NEON_BLUE)
        root.option_add("*selectForeground", self.colors.PRIMARY_DARK)

        # Create and configure ttk style
        self._style = ttk.Style(root)

        # Apply theme name
        try:
            self._style.theme_use('clam')  # Base theme
        except tk.TclError:
            self._style.theme_use('default')

        self._configure_styles()
        return self._style

    def _configure_styles(self):
        """Configure all widget styles for DJ theme."""

        # Configure main frame styles
        self._style.configure(
            "DJ.TFrame",
            background=self.colors.PRIMARY_DARK,
            borderwidth=0
        )

        self._style.configure(
            "DJPanel.TFrame",
            background=self.colors.SECONDARY_DARK,
            borderwidth=self.dimensions.BORDER_WIDTH,
            relief="solid"
        )

        self._style.configure(
            "DJControl.TFrame",
            background=self.colors.TERTIARY_DARK,
            borderwidth=self.dimensions.BORDER_WIDTH,
            relief="raised"
        )

        # Configure label styles
        self._style.configure(
            "DJ.TLabel",
            background=self.colors.PRIMARY_DARK,
            foreground=self.colors.TEXT_PRIMARY,
            font=(self.fonts.SANS_FAMILY[0], self.fonts.NORMAL_SIZE)
        )

        self._style.configure(
            "DJTitle.TLabel",
            background=self.colors.SECONDARY_DARK,
            foreground=self.colors.NEON_BLUE,
            font=(self.fonts.SANS_FAMILY[0], self.fonts.TITLE_SIZE, self.fonts.BOLD)
        )

        self._style.configure(
            "DJDisplay.TLabel",
            background=self.colors.PRIMARY_DARK,
            foreground=self.colors.NEON_GREEN,
            font=(self.fonts.MONO_FAMILY[0], self.fonts.DISPLAY_SIZE, self.fonts.BOLD)
        )

        self._style.configure(
            "DJStatus.TLabel",
            background=self.colors.SECONDARY_DARK,
            foreground=self.colors.TEXT_SECONDARY,
            font=(self.fonts.SANS_FAMILY[0], self.fonts.SMALL_SIZE)
        )

        # Configure button styles
        self._style.configure(
            "DJ.TButton",
            background=self.colors.BUTTON_NORMAL,
            foreground=self.colors.TEXT_PRIMARY,
            borderwidth=1,
            focuscolor="none",
            font=(self.fonts.SANS_FAMILY[0], self.fonts.NORMAL_SIZE)
        )

        self._style.map(
            "DJ.TButton",
            background=[
                ("active", self.colors.BUTTON_HOVER),
                ("pressed", self.colors.NEON_BLUE)
            ],
            foreground=[
                ("pressed", self.colors.PRIMARY_DARK)
            ]
        )

        self._style.configure(
            "DJActive.TButton",
            background=self.colors.NEON_BLUE,
            foreground=self.colors.PRIMARY_DARK,
            font=(self.fonts.SANS_FAMILY[0], self.fonts.NORMAL_SIZE, self.fonts.BOLD)
        )

        self._style.configure(
            "DJDanger.TButton",
            background=self.colors.NEON_RED,
            foreground=self.colors.TEXT_PRIMARY,
            font=(self.fonts.SANS_FAMILY[0], self.fonts.NORMAL_SIZE, self.fonts.BOLD)
        )

        # Configure scale (slider) styles
        self._style.configure(
            "DJ.TScale",
            background=self.colors.PRIMARY_DARK,
            troughcolor=self.colors.SLIDER_TRACK,
            borderwidth=0,
            lightcolor=self.colors.SLIDER_ACTIVE,
            darkcolor=self.colors.SLIDER_ACTIVE
        )

        self._style.configure(
            "DJVertical.TScale",
            background=self.colors.PRIMARY_DARK,
            troughcolor=self.colors.SLIDER_TRACK,
            borderwidth=0,
            lightcolor=self.colors.SLIDER_ACTIVE,
            darkcolor=self.colors.SLIDER_ACTIVE,
            orient="vertical"
        )

        # Configure progressbar styles
        self._style.configure(
            "DJ.TProgressbar",
            background=self.colors.NEON_BLUE,
            troughcolor=self.colors.SLIDER_TRACK,
            borderwidth=0,
            lightcolor=self.colors.NEON_BLUE,
            darkcolor=self.colors.NEON_BLUE
        )

        self._style.configure(
            "DJLevel.TProgressbar",
            background=self.colors.LEVEL_COLOR,
            troughcolor=self.colors.SLIDER_TRACK,
            borderwidth=0
        )

        # Configure entry styles
        self._style.configure(
            "DJ.TEntry",
            background=self.colors.TERTIARY_DARK,
            foreground=self.colors.TEXT_PRIMARY,
            borderwidth=1,
            insertcolor=self.colors.TEXT_PRIMARY,
            selectbackground=self.colors.NEON_BLUE,
            selectforeground=self.colors.PRIMARY_DARK
        )

        # Configure combobox styles
        self._style.configure(
            "DJ.TCombobox",
            background=self.colors.TERTIARY_DARK,
            foreground=self.colors.TEXT_PRIMARY,
            borderwidth=1,
            selectbackground=self.colors.NEON_BLUE,
            selectforeground=self.colors.PRIMARY_DARK,
            fieldbackground=self.colors.TERTIARY_DARK
        )

        # Configure treeview styles (for music library)
        self._style.configure(
            "DJ.Treeview",
            background=self.colors.SECONDARY_DARK,
            foreground=self.colors.TEXT_PRIMARY,
            borderwidth=1,
            fieldbackground=self.colors.SECONDARY_DARK
        )

        self._style.configure(
            "DJ.Treeview.Heading",
            background=self.colors.TERTIARY_DARK,
            foreground=self.colors.TEXT_PRIMARY,
            borderwidth=1
        )

        self._style.map(
            "DJ.Treeview",
            background=[("selected", self.colors.NEON_BLUE)],
            foreground=[("selected", self.colors.PRIMARY_DARK)]
        )

        # Configure notebook styles (for tabs)
        self._style.configure(
            "DJ.TNotebook",
            background=self.colors.PRIMARY_DARK,
            borderwidth=0
        )

        self._style.configure(
            "DJ.TNotebook.Tab",
            background=self.colors.SECONDARY_DARK,
            foreground=self.colors.TEXT_SECONDARY,
            padding=[12, 8]
        )

        self._style.map(
            "DJ.TNotebook.Tab",
            background=[
                ("selected", self.colors.TERTIARY_DARK),
                ("active", self.colors.BUTTON_HOVER)
            ],
            foreground=[
                ("selected", self.colors.TEXT_PRIMARY),
                ("active", self.colors.TEXT_PRIMARY)
            ]
        )

    def get_color(self, color_name: str) -> str:
        """Get color value by name."""
        return getattr(self.colors, color_name.upper(), self.colors.TEXT_PRIMARY)

    def get_font(self, family: str = "sans", size: int = 12, weight: str = "normal") -> Tuple[str, int, str]:
        """Get font tuple for widget configuration."""
        if family == "mono":
            font_family = self.fonts.MONO_FAMILY[0]
        else:
            font_family = self.fonts.SANS_FAMILY[0]

        return (font_family, size, weight)

    def create_status_color(self, status: str) -> str:
        """Get color for status indicators."""
        status_colors = {
            "online": self.colors.STATUS_ONLINE,
            "offline": self.colors.STATUS_OFFLINE,
            "warning": self.colors.STATUS_WARNING,
            "neutral": self.colors.STATUS_NEUTRAL,
            "active": self.colors.NEON_BLUE,
            "error": self.colors.NEON_RED,
            "success": self.colors.NEON_GREEN
        }
        return status_colors.get(status.lower(), self.colors.STATUS_NEUTRAL)

    def create_deck_color(self, deck: str) -> str:
        """Get color for deck-specific elements."""
        if deck.upper() == "A":
            return self.colors.DECK_A_COLOR
        elif deck.upper() == "B":
            return self.colors.DECK_B_COLOR
        else:
            return self.colors.NEON_BLUE


# Utility functions for theme application
def apply_dj_theme(root: tk.Tk) -> DJTheme:
    """
    Quick function to apply DJ theme to root window.

    Args:
        root: Root tkinter window

    Returns:
        Configured DJTheme instance
    """
    theme = DJTheme()
    theme.apply_theme(root)
    return theme


def create_themed_frame(parent, style_name: str = "DJ.TFrame") -> ttk.Frame:
    """Create a frame with DJ theme styling."""
    return ttk.Frame(parent, style=style_name)


def create_themed_label(parent, text: str = "", style_name: str = "DJ.TLabel") -> ttk.Label:
    """Create a label with DJ theme styling."""
    return ttk.Label(parent, text=text, style=style_name)


def create_themed_button(parent, text: str = "", command=None, style_name: str = "DJ.TButton") -> ttk.Button:
    """Create a button with DJ theme styling."""
    return ttk.Button(parent, text=text, command=command, style=style_name)


# Export theme constants for direct access
__all__ = [
    'DJTheme', 'DJColors', 'DJFonts', 'DJDimensions',
    'apply_dj_theme', 'create_themed_frame', 'create_themed_label', 'create_themed_button'
]