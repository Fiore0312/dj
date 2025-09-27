"""
Music Library Browser Component
Provides track browsing, search, filtering, and drag-and-drop functionality
for music library management in the DJ interface.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import time
from typing import List, Dict, Any, Optional, Callable
import threading
import logging
from pathlib import Path

from ..themes.dj_dark_theme import DJTheme, create_themed_frame, create_themed_label, create_themed_button
from ..utils.state_manager import get_state_manager, TrackInfo
from ..utils.threading_utils import TaskManager

logger = logging.getLogger(__name__)


class TrackMetadata:
    """Track metadata container with audio file parsing."""

    @staticmethod
    def extract_metadata(file_path: str) -> TrackInfo:
        """Extract metadata from audio file."""
        try:
            # Try to import mutagen for metadata extraction
            try:
                from mutagen import File
                audio_file = File(file_path)

                if audio_file is not None:
                    # Extract basic metadata
                    title = str(audio_file.get('TIT2', [''])[0] or audio_file.get('TITLE', [''])[0] or '')
                    artist = str(audio_file.get('TPE1', [''])[0] or audio_file.get('ARTIST', [''])[0] or '')
                    album = str(audio_file.get('TALB', [''])[0] or audio_file.get('ALBUM', [''])[0] or '')
                    genre = str(audio_file.get('TCON', [''])[0] or audio_file.get('GENRE', [''])[0] or '')

                    # Get duration
                    duration = float(audio_file.info.length) if hasattr(audio_file, 'info') and audio_file.info else 0.0

                    # Try to extract BPM
                    bpm = 0.0
                    bpm_tags = ['TBPM', 'BPM', 'bpm']
                    for tag in bpm_tags:
                        if tag in audio_file:
                            try:
                                bpm = float(str(audio_file[tag][0]))
                                break
                            except (ValueError, IndexError):
                                continue

                    return TrackInfo(
                        title=title or Path(file_path).stem,
                        artist=artist,
                        album=album,
                        genre=genre,
                        bpm=bpm,
                        duration=duration,
                        file_path=file_path,
                        key="",
                        energy=5
                    )

            except ImportError:
                # Fallback without metadata library
                logger.warning("Mutagen not available, using filename only")

        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {e}")

        # Fallback to filename
        return TrackInfo(
            title=Path(file_path).stem,
            artist="",
            album="",
            genre="",
            bpm=0.0,
            duration=0.0,
            file_path=file_path,
            key="",
            energy=5
        )


class LibraryScanner:
    """Background library scanner for audio files."""

    SUPPORTED_FORMATS = {'.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg', '.wma'}

    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
        self._scanning = False
        self._scan_progress_callback: Optional[Callable[[int, int], None]] = None

    def scan_directory(self, directory: str, progress_callback: Optional[Callable[[int, int], None]] = None) -> List[TrackInfo]:
        """Scan directory for audio files and extract metadata."""
        self._scan_progress_callback = progress_callback
        self._scanning = True

        def scan_worker():
            try:
                tracks = []
                audio_files = []

                # Find all audio files
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if Path(file).suffix.lower() in self.SUPPORTED_FORMATS:
                            audio_files.append(os.path.join(root, file))

                total_files = len(audio_files)
                logger.info(f"Found {total_files} audio files in {directory}")

                # Process files
                for i, file_path in enumerate(audio_files):
                    if not self._scanning:
                        break

                    try:
                        track_info = TrackMetadata.extract_metadata(file_path)
                        tracks.append(track_info)

                        # Update progress
                        if self._scan_progress_callback:
                            self._scan_progress_callback(i + 1, total_files)

                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {e}")

                logger.info(f"Scanned {len(tracks)} tracks successfully")
                return tracks

            except Exception as e:
                logger.error(f"Error scanning directory {directory}: {e}")
                return []

        # Submit scanning task
        return self.task_manager.submit_background_task('library_scan', scan_worker)

    def stop_scan(self):
        """Stop current scanning operation."""
        self._scanning = False


class MusicLibraryBrowser:
    """
    Music Library Browser component.
    Provides track browsing, search, filtering, and drag-and-drop functionality.
    """

    def __init__(self, parent, theme: DJTheme, task_manager: TaskManager):
        self.parent = parent
        self.theme = theme
        self.task_manager = task_manager
        self.state_manager = get_state_manager()

        # Library data
        self.tracks: List[TrackInfo] = []
        self.filtered_tracks: List[TrackInfo] = []
        self.current_directory = ""

        # Search and filter variables
        self.search_term = tk.StringVar()
        self.genre_filter = tk.StringVar(value="All")
        self.bpm_min = tk.IntVar(value=0)
        self.bpm_max = tk.IntVar(value=200)

        # Scanner
        self.scanner = LibraryScanner(task_manager)

        # Callbacks
        self.track_load_callback: Optional[Callable[[str, TrackInfo], None]] = None

        # Create the browser
        self.frame = self._create_browser()
        self._setup_search_bindings()

        logger.info("Music Library Browser initialized")

    def _create_browser(self) -> ttk.Frame:
        """Create the music library browser UI."""
        # Main browser frame
        browser_frame = create_themed_frame(self.parent, "DJPanel.TFrame")

        # Title and controls
        self._create_header(browser_frame)

        # Search and filter section
        self._create_search_section(browser_frame)

        # Track list
        self._create_track_list(browser_frame)

        # Status bar
        self._create_status_bar(browser_frame)

        return browser_frame

    def _create_header(self, parent):
        """Create header with library controls."""
        header_frame = create_themed_frame(parent, "DJ.TFrame")
        header_frame.pack(fill='x', padx=10, pady=(10, 5))

        # Title
        title_label = create_themed_label(header_frame, "📚 MUSIC LIBRARY", "DJTitle.TLabel")
        title_label.pack(side='left')

        # Control buttons
        button_frame = create_themed_frame(header_frame, "DJ.TFrame")
        button_frame.pack(side='right')

        self.scan_button = create_themed_button(
            button_frame,
            "SCAN FOLDER",
            command=self._scan_folder,
            style_name="DJ.TButton"
        )
        self.scan_button.pack(side='left', padx=(0, 5))

        self.refresh_button = create_themed_button(
            button_frame,
            "REFRESH",
            command=self._refresh_library,
            style_name="DJ.TButton"
        )
        self.refresh_button.pack(side='left', padx=(0, 5))

        self.settings_button = create_themed_button(
            button_frame,
            "SETTINGS",
            command=self._show_settings,
            style_name="DJ.TButton"
        )
        self.settings_button.pack(side='left')

    def _create_search_section(self, parent):
        """Create search and filter controls."""
        search_frame = create_themed_frame(parent, "DJControl.TFrame")
        search_frame.pack(fill='x', padx=10, pady=5)

        # Search bar
        search_bar_frame = create_themed_frame(search_frame, "DJ.TFrame")
        search_bar_frame.pack(fill='x', pady=5)

        search_label = create_themed_label(search_bar_frame, "Search:", "DJ.TLabel")
        search_label.pack(side='left', padx=(5, 10))

        self.search_entry = ttk.Entry(
            search_bar_frame,
            textvariable=self.search_term,
            style="DJ.TEntry",
            width=30
        )
        self.search_entry.pack(side='left', expand=True, fill='x', padx=(0, 10))

        clear_button = create_themed_button(
            search_bar_frame,
            "CLEAR",
            command=self._clear_search,
            style_name="DJ.TButton"
        )
        clear_button.pack(side='right', padx=5)

        # Filter controls
        filter_frame = create_themed_frame(search_frame, "DJ.TFrame")
        filter_frame.pack(fill='x', pady=5)

        # Genre filter
        genre_label = create_themed_label(filter_frame, "Genre:", "DJ.TLabel")
        genre_label.pack(side='left', padx=(5, 5))

        self.genre_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.genre_filter,
            style="DJ.TCombobox",
            state="readonly",
            width=15
        )
        self.genre_combo.pack(side='left', padx=(0, 20))

        # BPM range filter
        bpm_label = create_themed_label(filter_frame, "BPM:", "DJ.TLabel")
        bpm_label.pack(side='left', padx=(0, 5))

        self.bpm_min_entry = ttk.Entry(
            filter_frame,
            textvariable=self.bpm_min,
            style="DJ.TEntry",
            width=5
        )
        self.bpm_min_entry.pack(side='left', padx=(0, 5))

        dash_label = create_themed_label(filter_frame, "-", "DJ.TLabel")
        dash_label.pack(side='left')

        self.bpm_max_entry = ttk.Entry(
            filter_frame,
            textvariable=self.bpm_max,
            style="DJ.TEntry",
            width=5
        )
        self.bpm_max_entry.pack(side='left', padx=(5, 0))

    def _create_track_list(self, parent):
        """Create track list with treeview."""
        list_frame = create_themed_frame(parent, "DJ.TFrame")
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Create treeview with scrollbars
        tree_frame = create_themed_frame(list_frame, "DJ.TFrame")
        tree_frame.pack(fill='both', expand=True)

        # Treeview
        self.track_tree = ttk.Treeview(
            tree_frame,
            style="DJ.Treeview",
            columns=('artist', 'title', 'album', 'genre', 'bpm', 'duration'),
            show='headings',
            height=15
        )

        # Configure columns
        self.track_tree.heading('artist', text='Artist')
        self.track_tree.heading('title', text='Title')
        self.track_tree.heading('album', text='Album')
        self.track_tree.heading('genre', text='Genre')
        self.track_tree.heading('bpm', text='BPM')
        self.track_tree.heading('duration', text='Duration')

        self.track_tree.column('artist', width=150, minwidth=100)
        self.track_tree.column('title', width=200, minwidth=150)
        self.track_tree.column('album', width=150, minwidth=100)
        self.track_tree.column('genre', width=100, minwidth=80)
        self.track_tree.column('bpm', width=60, minwidth=50)
        self.track_tree.column('duration', width=80, minwidth=60)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.track_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.track_tree.xview)
        self.track_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack treeview and scrollbars
        self.track_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')

        # Bind events
        self.track_tree.bind('<Double-1>', self._on_track_double_click)
        self.track_tree.bind('<Button-3>', self._on_track_right_click)

        # Enable drag and drop
        self._setup_drag_drop()

    def _create_status_bar(self, parent):
        """Create status bar."""
        status_frame = create_themed_frame(parent, "DJ.TFrame")
        status_frame.pack(fill='x', padx=10, pady=(5, 10))

        self.status_label = create_themed_label(
            status_frame,
            "No library loaded",
            "DJStatus.TLabel"
        )
        self.status_label.pack(side='left')

        # Progress bar (hidden by default)
        self.progress_bar = ttk.Progressbar(
            status_frame,
            style="DJ.TProgressbar",
            mode='determinate',
            length=200
        )
        # Don't pack initially

    def _setup_search_bindings(self):
        """Setup search and filter event bindings."""
        self.search_term.trace_add('write', self._on_search_change)
        self.genre_filter.trace_add('write', self._on_filter_change)
        self.bpm_min.trace_add('write', self._on_filter_change)
        self.bpm_max.trace_add('write', self._on_filter_change)

    def _setup_drag_drop(self):
        """Setup drag and drop functionality."""
        # Note: Basic drag detection, full drag-drop would need additional libraries
        self.track_tree.bind('<Button-1>', self._on_drag_start)
        self.track_tree.bind('<B1-Motion>', self._on_drag_motion)

    def _scan_folder(self):
        """Scan a folder for music files."""
        directory = filedialog.askdirectory(
            title="Select Music Folder",
            initialdir=self.current_directory or os.path.expanduser("~/Music")
        )

        if directory:
            self.current_directory = directory
            self._start_scan(directory)

    def _start_scan(self, directory: str):
        """Start background scanning of directory."""
        try:
            # Show progress
            self.progress_bar.pack(side='right', padx=(10, 0))
            self.progress_bar['value'] = 0
            self.scan_button.configure(text="SCANNING...", state='disabled')
            self.status_label.configure(text=f"Scanning {directory}...")

            # Start scan
            scan_future = self.scanner.scan_directory(directory, self._on_scan_progress)

            # Monitor scan completion
            self.task_manager.start_periodic_task(
                'monitor_scan',
                0.5,
                self._monitor_scan,
                scan_future
            )

        except Exception as e:
            logger.error(f"Error starting scan: {e}")
            messagebox.showerror("Error", f"Failed to start scan: {e}")
            self._scan_complete([])

    def _on_scan_progress(self, current: int, total: int):
        """Handle scan progress updates."""
        if total > 0:
            progress = (current / total) * 100
            self.task_manager.schedule_gui_update(
                self.progress_bar.configure,
                value=progress
            )
            self.task_manager.schedule_gui_update(
                self.status_label.configure,
                text=f"Scanning... {current}/{total}"
            )

    def _monitor_scan(self, scan_future):
        """Monitor scan completion."""
        if scan_future.done():
            try:
                tracks = scan_future.result()
                self.task_manager.schedule_gui_update(self._scan_complete, tracks)
            except Exception as e:
                logger.error(f"Scan failed: {e}")
                self.task_manager.schedule_gui_update(self._scan_complete, [])

            # Stop monitoring
            self.task_manager.stop_periodic_task('monitor_scan')

    def _scan_complete(self, tracks: List[TrackInfo]):
        """Handle scan completion."""
        self.tracks = tracks
        self.filtered_tracks = tracks.copy()

        # Update UI
        self.scan_button.configure(text="SCAN FOLDER", state='normal')
        self.progress_bar.pack_forget()

        if tracks:
            self.status_label.configure(text=f"Loaded {len(tracks)} tracks")
            self._update_track_list()
            self._update_genre_filter()
        else:
            self.status_label.configure(text="No tracks found")

        logger.info(f"Library scan complete: {len(tracks)} tracks")

    def _update_track_list(self):
        """Update the track list display."""
        # Clear existing items
        for item in self.track_tree.get_children():
            self.track_tree.delete(item)

        # Add filtered tracks
        for track in self.filtered_tracks:
            # Format duration
            if track.duration > 0:
                minutes = int(track.duration // 60)
                seconds = int(track.duration % 60)
                duration_str = f"{minutes:02d}:{seconds:02d}"
            else:
                duration_str = "--:--"

            # Format BPM
            bpm_str = f"{track.bpm:.1f}" if track.bpm > 0 else "--"

            self.track_tree.insert('', 'end', values=(
                track.artist or "Unknown Artist",
                track.title or "Unknown Title",
                track.album or "",
                track.genre or "",
                bpm_str,
                duration_str
            ), tags=(track.file_path,))

    def _update_genre_filter(self):
        """Update genre filter options."""
        genres = set(track.genre for track in self.tracks if track.genre)
        genre_list = ["All"] + sorted(genres)
        self.genre_combo['values'] = genre_list

    def _apply_filters(self):
        """Apply search and filter criteria."""
        search = self.search_term.get().lower()
        genre = self.genre_filter.get()
        bpm_min_val = self.bpm_min.get()
        bpm_max_val = self.bpm_max.get()

        self.filtered_tracks = []

        for track in self.tracks:
            # Search filter
            if search:
                search_text = f"{track.artist} {track.title} {track.album}".lower()
                if search not in search_text:
                    continue

            # Genre filter
            if genre != "All" and track.genre != genre:
                continue

            # BPM filter
            if track.bpm > 0:
                if track.bpm < bpm_min_val or track.bpm > bpm_max_val:
                    continue

            self.filtered_tracks.append(track)

        self._update_track_list()
        self.status_label.configure(
            text=f"Showing {len(self.filtered_tracks)} of {len(self.tracks)} tracks"
        )

    def _on_search_change(self, *args):
        """Handle search term change."""
        self._apply_filters()

    def _on_filter_change(self, *args):
        """Handle filter change."""
        self._apply_filters()

    def _clear_search(self):
        """Clear search and filters."""
        self.search_term.set("")
        self.genre_filter.set("All")
        self.bpm_min.set(0)
        self.bpm_max.set(200)

    def _refresh_library(self):
        """Refresh the current library."""
        if self.current_directory:
            self._start_scan(self.current_directory)

    def _show_settings(self):
        """Show library settings dialog."""
        # Placeholder for settings dialog
        messagebox.showinfo("Settings", "Library settings coming soon!")

    def _on_track_double_click(self, event):
        """Handle track double-click."""
        selection = self.track_tree.selection()
        if selection:
            item = self.track_tree.item(selection[0])
            file_path = item['tags'][0] if item['tags'] else None

            if file_path:
                # Find track info
                track = next((t for t in self.tracks if t.file_path == file_path), None)
                if track:
                    self._load_track_to_deck(track)

    def _on_track_right_click(self, event):
        """Handle track right-click context menu."""
        selection = self.track_tree.selection()
        if selection:
            # Create context menu
            context_menu = tk.Menu(self.track_tree, tearoff=0)
            context_menu.configure(
                bg=self.theme.colors.SECONDARY_DARK,
                fg=self.theme.colors.TEXT_PRIMARY,
                activebackground=self.theme.colors.NEON_BLUE,
                activeforeground=self.theme.colors.PRIMARY_DARK
            )

            context_menu.add_command(label="Load to Deck A", command=lambda: self._load_to_specific_deck("A"))
            context_menu.add_command(label="Load to Deck B", command=lambda: self._load_to_specific_deck("B"))
            context_menu.add_separator()
            context_menu.add_command(label="Show File Info", command=self._show_file_info)

            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()

    def _load_track_to_deck(self, track: TrackInfo):
        """Load track to available deck."""
        # Determine best deck to load to
        system_state = self.state_manager.get_state()

        if system_state.deck_a.state.value in ["stopped", "paused"]:
            target_deck = "A"
        elif system_state.deck_b.state.value in ["stopped", "paused"]:
            target_deck = "B"
        else:
            # Ask user which deck
            target_deck = self._ask_deck_selection()

        if target_deck:
            self._load_to_deck(target_deck, track)

    def _load_to_specific_deck(self, deck_id: str):
        """Load selected track to specific deck."""
        selection = self.track_tree.selection()
        if selection:
            item = self.track_tree.item(selection[0])
            file_path = item['tags'][0] if item['tags'] else None

            if file_path:
                track = next((t for t in self.tracks if t.file_path == file_path), None)
                if track:
                    self._load_to_deck(deck_id, track)

    def _load_to_deck(self, deck_id: str, track: TrackInfo):
        """Load track to specified deck."""
        try:
            # Update state
            self.state_manager.set_track_info(deck_id, track)

            # Call external callback
            if self.track_load_callback:
                self.task_manager.submit_background_task(
                    f'load_track_{deck_id}',
                    self.track_load_callback,
                    deck_id,
                    track
                )

            logger.info(f"Loaded {track.display_name} to Deck {deck_id}")

        except Exception as e:
            logger.error(f"Error loading track to deck: {e}")
            messagebox.showerror("Error", f"Failed to load track: {e}")

    def _ask_deck_selection(self) -> Optional[str]:
        """Ask user to select deck for loading."""
        # Simple deck selection dialog
        result = messagebox.askyesnocancel(
            "Select Deck",
            "Load to Deck A?\n\nYes = Deck A\nNo = Deck B\nCancel = Don't load"
        )

        if result is True:
            return "A"
        elif result is False:
            return "B"
        else:
            return None

    def _show_file_info(self):
        """Show detailed file information."""
        selection = self.track_tree.selection()
        if selection:
            item = self.track_tree.item(selection[0])
            file_path = item['tags'][0] if item['tags'] else None

            if file_path:
                track = next((t for t in self.tracks if t.file_path == file_path), None)
                if track:
                    info_text = f"""Title: {track.title}
Artist: {track.artist}
Album: {track.album}
Genre: {track.genre}
BPM: {track.bpm:.1f}
Duration: {int(track.duration//60):02d}:{int(track.duration%60):02d}
File: {track.file_path}"""

                    messagebox.showinfo("Track Information", info_text)

    def _on_drag_start(self, event):
        """Handle drag start."""
        # Basic drag detection
        selection = self.track_tree.selection()
        if selection:
            logger.debug("Drag started")

    def _on_drag_motion(self, event):
        """Handle drag motion."""
        # Basic drag motion
        pass

    def set_track_load_callback(self, callback: Callable[[str, TrackInfo], None]):
        """Set callback for track loading."""
        self.track_load_callback = callback

    def load_library_from_file(self, file_path: str):
        """Load library from saved file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            tracks = []
            for track_data in data.get('tracks', []):
                track = TrackInfo(**track_data)
                tracks.append(track)

            self.tracks = tracks
            self.filtered_tracks = tracks.copy()
            self.current_directory = data.get('directory', '')

            self._update_track_list()
            self._update_genre_filter()
            self.status_label.configure(text=f"Loaded {len(tracks)} tracks from file")

            logger.info(f"Loaded library from {file_path}: {len(tracks)} tracks")

        except Exception as e:
            logger.error(f"Error loading library from file: {e}")
            messagebox.showerror("Error", f"Failed to load library: {e}")

    def save_library_to_file(self, file_path: str):
        """Save library to file."""
        try:
            data = {
                'directory': self.current_directory,
                'tracks': [
                    {
                        'title': track.title,
                        'artist': track.artist,
                        'album': track.album,
                        'genre': track.genre,
                        'bpm': track.bpm,
                        'duration': track.duration,
                        'file_path': track.file_path,
                        'key': track.key,
                        'energy': track.energy
                    }
                    for track in self.tracks
                ]
            }

            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved library to {file_path}: {len(self.tracks)} tracks")

        except Exception as e:
            logger.error(f"Error saving library to file: {e}")
            messagebox.showerror("Error", f"Failed to save library: {e}")

    def get_frame(self) -> ttk.Frame:
        """Get the main browser frame."""
        return self.frame

    def get_track_count(self) -> int:
        """Get total track count."""
        return len(self.tracks)

    def get_filtered_count(self) -> int:
        """Get filtered track count."""
        return len(self.filtered_tracks)

    def cleanup(self):
        """Cleanup resources."""
        # Stop any ongoing scans
        self.scanner.stop_scan()

        # Stop monitoring tasks
        self.task_manager.stop_periodic_task('monitor_scan')

        logger.info("Music Library Browser cleanup complete")


# Export the main class
__all__ = ['MusicLibraryBrowser']