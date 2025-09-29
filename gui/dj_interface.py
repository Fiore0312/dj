#!/usr/bin/env python3
"""
🖥️ DJ AI Interface - GUI Unificata Semplice
Interface utente semplice per controllo DJ AI con chat tempo reale
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import asyncio
import threading
import time
import logging
from typing import Optional, Dict, Any, Callable
from pathlib import Path
import json

# Imports del sistema DJ
from config import DJConfig, VENUE_TYPES, EVENT_TYPES, get_config, check_system_requirements
from core.openrouter_client import OpenRouterClient, DJContext, get_openrouter_client
from core.persistent_config import get_persistent_settings
from traktor_control import TraktorController, get_traktor_controller, DeckID
from music_library import MusicLibraryScanner, get_music_scanner

logger = logging.getLogger(__name__)

class DJInterface:
    """Interfaccia DJ AI unificata"""

    def __init__(self):
        """Inizializza interfaccia"""
        # Load persistent settings first
        self.persistent_settings = get_persistent_settings()

        self.root = tk.Tk()
        self.root.title("🎧 AI DJ System - Powered by OpenRouter")

        # Use persistent window size
        window_size = f"{self.persistent_settings.window_width}x{self.persistent_settings.window_height}"
        self.root.geometry(window_size)
        self.root.configure(bg='#1a1a1a')

        # Configurazione
        self.config = get_config()
        self.setup_complete = False

        # Componenti sistema
        self.ai_client: Optional[OpenRouterClient] = None
        self.traktor_controller: Optional[TraktorController] = None
        self.music_scanner: Optional[MusicLibraryScanner] = None

        # Stato DJ
        self.dj_context = DJContext()
        self.ai_enabled = False
        self.session_active = False

        # Threading
        self.ai_thread: Optional[threading.Thread] = None
        self.update_thread: Optional[threading.Thread] = None
        self.running = True

        # Statistiche
        self.stats = {
            'session_start': 0.0,
            'tracks_mixed': 0,
            'ai_decisions': 0,
            'manual_overrides': 0
        }

        self._create_interface()
        self._setup_bindings()

        # Controllo sistema all'avvio
        self.root.after(100, self._check_system)

    def _create_interface(self):
        """Crea interfaccia utente"""

        # Enhanced dark theme with modern styling
        style = ttk.Style()
        style.theme_use('clam')

        # Base colors
        bg_primary = '#1a1a1a'
        bg_secondary = '#2a2a2a'
        bg_accent = '#333333'
        fg_primary = '#ffffff'
        fg_secondary = '#cccccc'
        accent_color = '#00ff88'  # DJ green
        error_color = '#ff4444'
        warning_color = '#ffaa00'

        # Configure styles
        style.configure('TLabel', background=bg_primary, foreground=fg_primary, font=('Arial', 9))
        style.configure('TFrame', background=bg_primary)
        style.configure('TLabelFrame', background=bg_primary, foreground=fg_primary,
                       borderwidth=1, relief='solid')
        style.configure('TButton', background=bg_accent, foreground=fg_primary,
                       padding=(10, 5), font=('Arial', 9, 'bold'))
        style.map('TButton',
                 background=[('active', accent_color), ('pressed', '#006644')])
        style.configure('Horizontal.TScale', background=bg_primary, troughcolor=bg_secondary)
        style.configure('TCombobox', fieldbackground=bg_secondary, foreground=fg_primary)
        style.configure('TEntry', fieldbackground=bg_secondary, foreground=fg_primary)

        # Custom styles for status indicators
        style.configure('Success.TLabel', background=bg_primary, foreground=accent_color,
                       font=('Arial', 9, 'bold'))
        style.configure('Error.TLabel', background=bg_primary, foreground=error_color,
                       font=('Arial', 9, 'bold'))
        style.configure('Warning.TLabel', background=bg_primary, foreground=warning_color,
                       font=('Arial', 9, 'bold'))
        style.configure('Status.TLabel', background=bg_secondary, foreground=fg_secondary,
                       font=('Courier', 8))

        # Frame principale
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # === TOP: Setup e Controlli ===
        self._create_setup_section(main_frame)

        # === MIDDLE: Status e Controlli DJ ===
        self._create_dj_controls(main_frame)

        # === BOTTOM: Chat AI e Log ===
        self._create_chat_section(main_frame)

        # === STATUS BAR ===
        self._create_status_bar(main_frame)

    def _create_setup_section(self, parent):
        """Sezione setup iniziale"""
        setup_frame = ttk.LabelFrame(parent, text="🔧 Setup Sistema", padding=10)
        setup_frame.pack(fill=tk.X, pady=(0, 10))

        # Status sistema con indicatori real-time
        status_frame = ttk.Frame(setup_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))

        # Status indicators grid
        status_grid = ttk.Frame(status_frame)
        status_grid.pack(fill=tk.X)

        # System status indicators
        self.system_status_var = tk.StringVar(value="🔄 Checking...")
        self.system_status_label = ttk.Label(status_grid, textvariable=self.system_status_var,
                                            style='Status.TLabel')
        self.system_status_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))

        # MIDI status indicator
        self.midi_connection_var = tk.StringVar(value="🔴 MIDI: Disconnected")
        self.midi_connection_label = ttk.Label(status_grid, textvariable=self.midi_connection_var,
                                             style='Error.TLabel')
        self.midi_connection_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))

        # AI status indicator
        self.ai_connection_var = tk.StringVar(value="🔴 AI: Disconnected")
        self.ai_connection_label = ttk.Label(status_grid, textvariable=self.ai_connection_var,
                                           style='Error.TLabel')
        self.ai_connection_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 20))

        # Music library indicator
        self.library_status_var = tk.StringVar(value="📁 Library: Unknown")
        self.library_status_label = ttk.Label(status_grid, textvariable=self.library_status_var,
                                             style='Status.TLabel')
        self.library_status_label.grid(row=0, column=3, sticky=tk.W)

        # Setup veloce
        setup_row = ttk.Frame(setup_frame)
        setup_row.pack(fill=tk.X)

        # Venue type - load from persistent settings
        ttk.Label(setup_row, text="Locale:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.venue_var = tk.StringVar(value=self.persistent_settings.last_venue_type)
        venue_combo = ttk.Combobox(setup_row, textvariable=self.venue_var,
                                  values=list(VENUE_TYPES.keys()), state="readonly", width=15)
        venue_combo.grid(row=0, column=1, padx=5)
        venue_combo.bind('<<ComboboxSelected>>', self._on_venue_change)

        # Event type - load from persistent settings
        ttk.Label(setup_row, text="Evento:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.event_var = tk.StringVar(value=self.persistent_settings.last_event_type)
        event_combo = ttk.Combobox(setup_row, textvariable=self.event_var,
                                  values=list(EVENT_TYPES.keys()), state="readonly", width=15)
        event_combo.grid(row=0, column=3, padx=5)
        event_combo.bind('<<ComboboxSelected>>', self._on_event_change)

        # API Key
        ttk.Label(setup_row, text="API Key:").grid(row=0, column=4, sticky=tk.W, padx=(10, 5))
        # Auto-load API key from persistent settings or environment
        api_key_value = (self.persistent_settings.openrouter_api_key or
                        self.config.openrouter_api_key or "")
        if api_key_value:
            # Mask the key for display but keep full value
            display_value = f"***{api_key_value[-8:]}" if len(api_key_value) > 8 else "***"
        else:
            display_value = ""
        self.api_key_var = tk.StringVar(value=api_key_value)
        self.api_key_display_var = tk.StringVar(value=display_value)
        api_entry = ttk.Entry(setup_row, textvariable=self.api_key_display_var, show="*", width=20)
        api_entry.grid(row=0, column=5, padx=5)
        api_entry.bind('<FocusIn>', self._on_api_key_focus_in)
        api_entry.bind('<FocusOut>', self._on_api_key_focus_out)

        # Bottone avvio
        self.start_button = ttk.Button(setup_row, text="🚀 AVVIA DJ AI", command=self._start_dj_system)
        self.start_button.grid(row=0, column=6, padx=10)

    def _create_dj_controls(self, parent):
        """Controlli DJ principali"""
        controls_frame = ttk.LabelFrame(parent, text="🎛️ Controlli DJ", padding=10)
        controls_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Left: Status e Info
        left_frame = ttk.Frame(controls_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))

        # Status display
        self.status_text = scrolledtext.ScrolledText(left_frame, height=15, width=40,
                                                    bg='#2a2a2a', fg='#00ff00',
                                                    font=('Courier', 9))
        self.status_text.pack(fill=tk.BOTH, expand=True)

        # Right: Controlli
        right_frame = ttk.Frame(controls_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        # Energy slider - load from persistent settings
        ttk.Label(right_frame, text="Energia (1-10):").pack(anchor=tk.W)
        self.energy_var = tk.IntVar(value=self.persistent_settings.default_energy_level)
        self.energy_slider = ttk.Scale(right_frame, from_=1, to=10, orient=tk.HORIZONTAL,
                                      variable=self.energy_var, command=self._on_energy_change)
        self.energy_slider.pack(fill=tk.X, pady=5)

        # Controlli rapidi
        controls_grid = ttk.Frame(right_frame)
        controls_grid.pack(fill=tk.X, pady=10)

        buttons = [
            ("▶️ Play A", lambda: self._deck_control("play", "A")),
            ("⏸️ Pause A", lambda: self._deck_control("pause", "A")),
            ("▶️ Play B", lambda: self._deck_control("play", "B")),
            ("⏸️ Pause B", lambda: self._deck_control("pause", "B")),
            ("🎧 Cue A", lambda: self._deck_control("cue", "A")),
            ("🎧 Cue B", lambda: self._deck_control("cue", "B")),
        ]

        for i, (text, command) in enumerate(buttons):
            row, col = divmod(i, 2)
            btn = ttk.Button(controls_grid, text=text, command=command, width=12)
            btn.grid(row=row, column=col, padx=2, pady=2)

        # Crossfader
        ttk.Label(right_frame, text="Crossfader:").pack(anchor=tk.W, pady=(10, 0))
        self.crossfader_var = tk.DoubleVar(value=0.5)
        self.crossfader_slider = ttk.Scale(right_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL,
                                          variable=self.crossfader_var, command=self._on_crossfader_change)
        self.crossfader_slider.pack(fill=tk.X, pady=5)

        # Emergency stop
        self.emergency_btn = ttk.Button(right_frame, text="🚨 EMERGENCY STOP",
                                       command=self._emergency_stop)
        self.emergency_btn.pack(fill=tk.X, pady=10)

        # Toggle AI
        self.ai_toggle_btn = ttk.Button(right_frame, text="🤖 AI: OFF",
                                       command=self._toggle_ai)
        self.ai_toggle_btn.pack(fill=tk.X, pady=5)

        # Auto-Mix Toggle
        self.auto_mix_active = False
        self.auto_mix_timer = None
        self.auto_mix_btn = ttk.Button(right_frame, text="🎵 Auto-Mix: OFF",
                                     command=self._toggle_auto_mix)
        self.auto_mix_btn.pack(fill=tk.X, pady=5)

        # Auto-Mix Interval Selector
        interval_frame = ttk.Frame(right_frame)
        interval_frame.pack(fill=tk.X, pady=2)
        ttk.Label(interval_frame, text="Intervallo:").pack(side=tk.LEFT)
        self.auto_mix_interval_var = tk.IntVar(value=180)  # 3 minuti default
        interval_combo = ttk.Combobox(interval_frame, textvariable=self.auto_mix_interval_var,
                                    values=[60, 120, 180, 240, 300], width=8, state="readonly")
        interval_combo.pack(side=tk.RIGHT)

        # MIDI Test Button
        self.midi_test_btn = ttk.Button(right_frame, text="🎛️ Test MIDI",
                                       command=self._test_midi_connection)
        self.midi_test_btn.pack(fill=tk.X, pady=5)

        # MIDI Test Status
        self.midi_status_var = tk.StringVar(value="🔴 MIDI: Non testato")
        self.midi_status_label = ttk.Label(right_frame, textvariable=self.midi_status_var)
        self.midi_status_label.pack(fill=tk.X, pady=2)

    def _create_chat_section(self, parent):
        """Sezione chat AI"""
        chat_frame = ttk.LabelFrame(parent, text="💬 Chat con AI DJ", padding=10)
        chat_frame.pack(fill=tk.X, pady=(0, 0))

        # Chat display
        self.chat_text = scrolledtext.ScrolledText(chat_frame, height=8,
                                                  bg='#2a2a2a', fg='#ffffff',
                                                  font=('Arial', 10))
        self.chat_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Input frame
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X)

        self.chat_entry = ttk.Entry(input_frame, font=('Arial', 11), width=50)
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Placeholder text
        self.chat_entry.insert(0, "Scrivi qui per comunicare con l'AI DJ...")
        self.chat_entry.bind('<FocusIn>', self._on_chat_focus_in)
        self.chat_entry.bind('<FocusOut>', self._on_chat_focus_out)

        ttk.Button(input_frame, text="Invia", command=self._send_chat).pack(side=tk.RIGHT)

        # Quick commands
        quick_frame = ttk.Frame(chat_frame)
        quick_frame.pack(fill=tk.X, pady=(10, 0))

        quick_commands = [
            "Aumenta energia gradualmente",
            "Crowd sembra annoiato",
            "Prepara closing",
            "Suggerisci prossimo brano"
        ]

        for cmd in quick_commands:
            btn = ttk.Button(quick_frame, text=cmd,
                           command=lambda c=cmd: self._quick_chat(c))
            btn.pack(side=tk.LEFT, padx=2)

    def _create_status_bar(self, parent):
        """Crea status bar con informazioni modello AI"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(10, 0))

        # Separatore
        separator = ttk.Separator(status_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 5))

        # Status bar content
        status_content = ttk.Frame(status_frame)
        status_content.pack(fill=tk.X)

        # Model info (left)
        self.model_status_var = tk.StringVar(value="🤖 Modello: nousresearch/hermes-3-llama-3.1-405b")
        self.model_status_label = ttk.Label(status_content, textvariable=self.model_status_var,
                                           font=('Arial', 9))
        self.model_status_label.pack(side=tk.LEFT)

        # Connection status (center)
        self.connection_status_var = tk.StringVar(value="🔴 Disconnesso")
        self.connection_status_label = ttk.Label(status_content, textvariable=self.connection_status_var,
                                                font=('Arial', 9))
        self.connection_status_label.pack(side=tk.LEFT, padx=(20, 0))

        # Performance info (right)
        self.perf_status_var = tk.StringVar(value="⏱️ Latenza: -- ms")
        self.perf_status_label = ttk.Label(status_content, textvariable=self.perf_status_var,
                                          font=('Arial', 9))
        self.perf_status_label.pack(side=tk.RIGHT)

    def _setup_bindings(self):
        """Setup keybindings"""
        self.chat_entry.bind('<Return>', lambda e: self._send_chat())
        self.root.bind('<Control-q>', lambda e: self._quit_application())
        self.root.protocol("WM_DELETE_WINDOW", self._quit_application)

    def _on_api_key_focus_in(self, event):
        """Handle API key field focus in - show actual key for editing"""
        self.api_key_display_var.set(self.api_key_var.get())

    def _on_api_key_focus_out(self, event):
        """Handle API key field focus out - update actual key and mask display"""
        # Update the actual API key value
        new_value = self.api_key_display_var.get()
        self.api_key_var.set(new_value)

        # Save to persistent settings if changed
        if hasattr(self.persistent_settings, 'openrouter_api_key'):
            old_value = self.persistent_settings.openrouter_api_key
            if new_value != old_value:
                self.persistent_settings.openrouter_api_key = new_value
                self.persistent_settings.save_to_file()
                print(f"✅ API key saved to persistent settings")

        # Mask the display value
        if new_value:
            display_value = f"***{new_value[-8:]}" if len(new_value) > 8 else "***"
            self.api_key_display_var.set(display_value)

    def _on_chat_focus_in(self, event):
        """Quando il campo chat riceve il focus"""
        if self.chat_entry.get() == "Scrivi qui per comunicare con l'AI DJ...":
            self.chat_entry.delete(0, tk.END)

    def _on_chat_focus_out(self, event):
        """Quando il campo chat perde il focus"""
        if not self.chat_entry.get():
            self.chat_entry.insert(0, "Scrivi qui per comunicare con l'AI DJ...")

    def _on_venue_change(self, event):
        """Handle venue type change - save to persistent settings"""
        new_venue = self.venue_var.get()
        if hasattr(self.persistent_settings, 'last_venue_type'):
            self.persistent_settings.last_venue_type = new_venue
            self.persistent_settings.save_to_file()

    def _on_event_change(self, event):
        """Handle event type change - save to persistent settings"""
        new_event = self.event_var.get()
        if hasattr(self.persistent_settings, 'last_event_type'):
            self.persistent_settings.last_event_type = new_event
            self.persistent_settings.save_to_file()

    def _check_system(self):
        """Controlla stato sistema con indicatori real-time"""
        requirements = check_system_requirements()

        # Update system status
        if requirements.get("python_version") and requirements.get("music_library"):
            self.system_status_var.set("✅ System: Ready")
            self.system_status_label.config(style='Success.TLabel')
        else:
            self.system_status_var.set("❌ System: Issues")
            self.system_status_label.config(style='Error.TLabel')

        # Update MIDI status
        if requirements.get("midi_system"):
            self.midi_connection_var.set("🟡 MIDI: Available")
            self.midi_connection_label.config(style='Warning.TLabel')
        else:
            self.midi_connection_var.set("❌ MIDI: Unavailable")
            self.midi_connection_label.config(style='Error.TLabel')

        # Update AI status based on API key
        if requirements.get("api_key"):
            self.ai_connection_var.set("🟡 AI: Key Ready")
            self.ai_connection_label.config(style='Warning.TLabel')
        else:
            self.ai_connection_var.set("❌ AI: No Key")
            self.ai_connection_label.config(style='Error.TLabel')

        # Update library status
        music_count = requirements.get("music_files_count", 0)
        if music_count > 0:
            self.library_status_var.set(f"✅ Library: {music_count} tracks")
            self.library_status_label.config(style='Success.TLabel')
        else:
            self.library_status_var.set("❌ Library: No tracks")
            self.library_status_label.config(style='Error.TLabel')

        # Abilita avvio se requisiti OK
        all_ok = all(requirements[k] for k in ["python_version", "music_library", "api_key"])
        self.start_button.config(state=tk.NORMAL if all_ok else tk.DISABLED)

    def _start_dj_system(self):
        """Avvia sistema DJ"""
        self._log_status("🚀 Avvio sistema DJ AI...")

        try:
            # Aggiorna config con valori GUI
            self.config.openrouter_api_key = self.api_key_var.get()

            # Aggiorna contesto DJ
            self.dj_context.venue_type = self.venue_var.get()
            self.dj_context.event_type = self.event_var.get()
            self.dj_context.energy_level = self.energy_var.get()

            # Avvia componenti in thread separato
            self.ai_thread = threading.Thread(target=self._init_system_thread, daemon=True)
            self.ai_thread.start()

            # Disabilita bottone
            self.start_button.config(state=tk.DISABLED, text="⏳ Avvio in corso...")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore avvio sistema: {e}")

    def _init_system_thread(self):
        """Inizializza sistema in thread separato"""
        try:
            # 1. OpenRouter client
            self._log_status("🤖 Connessione OpenRouter...")

            # Debug: Log della chiave API
            import os
            config_api_key = self.config.openrouter_api_key
            env_api_key = os.getenv('OPENROUTER_API_KEY')

            self._log_status(f"🔍 DEBUG: Config API key = {config_api_key[:20] if config_api_key else 'None'}...")
            self._log_status(f"🔍 DEBUG: Env API key = {env_api_key[:20] if env_api_key else 'None'}...")

            # Scegli API key (preferisci env se disponibile)
            api_key = env_api_key or config_api_key

            self._log_status(f"🔑 API Key scelta: {api_key[:20] if api_key else 'None'}...{api_key[-10:] if api_key else ''}")

            if not api_key:
                self._log_status("❌ ERRORE: API Key completamente mancante!")
                raise Exception("API Key OpenRouter mancante")

            self.ai_client = get_openrouter_client(api_key)

            # Test connessione AI
            self._test_ai_connection()

            # 2. Traktor controller
            self._log_status("🎛️ Connessione Traktor...")
            self.traktor_controller = get_traktor_controller(self.config)

            if not self.traktor_controller.connect():
                raise Exception("Impossibile connettersi a Traktor")

            # 3. Music scanner
            self._log_status("🎵 Scansione libreria musicale...")
            self.music_scanner = get_music_scanner(self.config)

            # Scan rapido
            self._scan_music_library()

            # 4. Avvia aggiornamenti
            self._log_status("✅ Sistema DJ AI avviato!")
            self.setup_complete = True
            self.session_active = True
            self.stats['session_start'] = time.time()

            # Aggiorna GUI
            self.root.after(0, self._on_system_ready)

            # Avvia loop aggiornamenti
            self._start_update_loop()

        except Exception as e:
            error_msg = str(e)
            self._log_status(f"❌ Errore: {error_msg}")
            self.root.after(0, lambda msg=error_msg: self._on_system_error(msg))

    def _test_ai_connection(self):
        """Test connessione AI"""
        response = self.ai_client.test_connection()
        if not response.success:
            raise Exception(f"Test AI fallito: {response.error}")

        # Aggiorna status bar con info modello
        model_name = response.model_used
        self.root.after(0, lambda: self.model_status_var.set(f"🤖 Modello: {model_name}"))
        self.root.after(0, lambda: self.connection_status_var.set("🟢 Connesso"))
        self.root.after(0, lambda: self.perf_status_var.set(f"⏱️ Latenza: {response.processing_time_ms:.0f}ms"))

        # Update real-time AI indicator
        self.root.after(0, lambda: self.ai_connection_var.set("✅ AI: Connected"))
        self.root.after(0, lambda: self.ai_connection_label.config(style='Success.TLabel'))

    def _scan_music_library(self):
        """Scansione libreria musicale"""
        import asyncio
        stats = asyncio.run(self.music_scanner.scan_library())
        self._log_status(f"📁 {stats['analyzed_files']} brani analizzati")

    def _on_system_ready(self):
        """Sistema pronto"""
        self.start_button.config(text="✅ Sistema Attivo", state=tk.DISABLED)
        self.ai_toggle_btn.config(text="🤖 AI: OFF", state=tk.NORMAL)

        # Inizializza timing sessione per Auto-Mix
        self.session_start_time = time.time()

        # Imposta focus sul campo chat
        self.chat_entry.focus_set()

        self._add_chat_message("Sistema", "🎧 DJ AI System pronto! Dimmi come vuoi procedere con il set.")

    def _on_system_error(self, error: str):
        """Errore sistema"""
        self.start_button.config(text="🚀 AVVIA DJ AI", state=tk.NORMAL)
        messagebox.showerror("Errore Sistema", error)

    def _start_update_loop(self):
        """Avvia loop di aggiornamento"""
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()

    def _update_loop(self):
        """Loop di aggiornamento continuo"""
        while self.running and self.session_active:
            try:
                if self.traktor_controller:
                    # Aggiorna status Traktor
                    status = self.traktor_controller.get_status()

                    # Aggiorna context
                    self.dj_context.current_bpm = status.deck_a_bpm
                    self.dj_context.time_in_set = int((time.time() - self.stats['session_start']) / 60)

                    # Aggiorna GUI
                    self.root.after(0, lambda: self._update_status_display(status))

                time.sleep(1)

            except Exception as e:
                logger.error(f"Errore update loop: {e}")
                time.sleep(5)

    def _update_status_display(self, status):
        """Aggiorna display status"""
        uptime = int((time.time() - self.stats['session_start']) / 60) if self.stats['session_start'] else 0

        status_info = f"""
🎛️ TRAKTOR STATUS
━━━━━━━━━━━━━━━━━
Deck A BPM: {status.deck_a_bpm:.1f}
Deck B BPM: {status.deck_b_bpm:.1f}
Posizione A: {status.deck_a_position:.2%}
Posizione B: {status.deck_b_position:.2%}
Crossfader: {status.crossfader_position}/127

📊 SESSIONE
━━━━━━━━━━━━━━━━━
Tempo: {uptime} min
Brani mixati: {self.stats['tracks_mixed']}
Decisioni AI: {self.stats['ai_decisions']}
Override manuali: {self.stats['manual_overrides']}

🎵 CONTESTO DJ
━━━━━━━━━━━━━━━━━
Venue: {self.dj_context.venue_type}
Evento: {self.dj_context.event_type}
Energia: {self.dj_context.energy_level}/10
Genere: {self.dj_context.current_genre}
AI Attivo: {'✅' if self.ai_enabled else '❌'}
"""

        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, status_info)

    def _deck_control(self, action: str, deck: str):
        """Controllo deck manuale"""
        if not self.traktor_controller:
            return

        self.stats['manual_overrides'] += 1
        deck_id = DeckID(deck)

        try:
            if action == "play":
                success = self.traktor_controller.play_deck(deck_id)
            elif action == "pause":
                success = self.traktor_controller.pause_deck(deck_id)
            elif action == "cue":
                success = self.traktor_controller.cue_deck(deck_id)
            else:
                return

            status = "✅" if success else "❌"
            self._log_status(f"{status} Deck {deck} {action}")

        except Exception as e:
            self._log_status(f"❌ Errore controllo deck: {e}")

    def _on_energy_change(self, value):
        """Cambio energia"""
        energy = int(float(value))
        self.dj_context.energy_level = energy

        # Save to persistent settings
        if hasattr(self.persistent_settings, 'default_energy_level'):
            self.persistent_settings.default_energy_level = energy
            self.persistent_settings.save_to_file()

        # Informa AI del cambio
        if self.ai_enabled and self.ai_client:
            threading.Thread(
                target=lambda: self._notify_ai_energy_change(energy),
                daemon=True
            ).start()

    def _notify_ai_energy_change(self, energy: int):
        """Notifica AI del cambio energia"""
        try:
            response = self.ai_client.get_dj_decision(
                self.dj_context,
                f"L'energia è stata cambiata a {energy}/10. Come adatti il mix?"
            )

            if response.success:
                self.root.after(0, lambda: self._add_chat_message("AI", response.response))
                # Aggiorna statistiche performance
                self.root.after(0, lambda: self.perf_status_var.set(f"⏱️ Latenza: {response.processing_time_ms:.0f}ms"))

        except Exception as e:
            logger.error(f"Errore notifica energia: {e}")

    def _on_crossfader_change(self, value):
        """Cambio crossfader"""
        if self.traktor_controller:
            position = float(value)
            self.traktor_controller.set_crossfader(position)
            self.stats['manual_overrides'] += 1

    def _test_midi_connection(self):
        """Test connessione MIDI con feedback visivo"""
        def run_test():
            test_controller = None
            try:
                self.root.after(0, lambda: self.midi_status_var.set("🟡 MIDI: Testing..."))
                self.root.after(0, lambda: self.midi_test_btn.config(state=tk.DISABLED))

                # Crea controller temporaneo per test se non esiste
                if self.traktor_controller:
                    test_controller = self.traktor_controller
                else:
                    # Crea controller temporaneo solo per il test
                    self.root.after(0, lambda: self.midi_status_var.set("🟡 MIDI: Inizializzando controller..."))
                    test_controller = get_traktor_controller(self.config)

                # Test connessione (modalità output-only per evitare conflitti)
                self.root.after(0, lambda: self.midi_status_var.set("🟡 MIDI: Connessione..."))
                success = test_controller.connect(output_only=True)
                if not success:
                    self.root.after(0, lambda: self.midi_status_var.set("❌ MIDI: Connessione fallita"))
                    self.root.after(0, lambda: self._log_status("❌ MIDI: Impossibile connettersi - verifica IAC Driver macOS"))
                    return

                # Test 5 segnali MIDI (ogni 3 secondi)
                self.root.after(0, lambda: self._log_status("🎛️ Avvio test MIDI - 5 segnali ogni 3 secondi"))
                for i in range(5):
                    self.root.after(0, lambda i=i: self.midi_status_var.set(f"🟡 MIDI: Test {i+1}/5"))

                    # Invia segnale test (volume deck A)
                    test_controller.set_deck_volume(DeckID.A, 0.5)
                    self.root.after(0, lambda i=i: self._log_status(f"📡 Segnale MIDI {i+1}/5 inviato"))
                    time.sleep(3)

                # Test completato
                self.root.after(0, lambda: self.midi_status_var.set("✅ MIDI: Test completato! Traktor dovrebbe lampeggiare"))
                self.root.after(0, lambda: self._log_status("✅ Test MIDI completato - verifica che l'icona MIDI di Traktor lampeggi"))

                # Se usiamo il controller principale, riconnettilo in modalità completa dopo il test
                if test_controller == self.traktor_controller and self.setup_complete:
                    try:
                        self.root.after(0, lambda: self._log_status("🔄 Riconnessione controller principale in modalità completa..."))
                        test_controller.disconnect()
                        # Riconnetti in modalità completa per ripristinare i controlli
                        if test_controller.connect():
                            self.root.after(0, lambda: self._log_status("✅ Controller principale riconnesso - controlli play/pause/cue ripristinati"))
                        else:
                            self.root.after(0, lambda: self._log_status("⚠️ Riconnessione controller principale fallita"))
                    except Exception as reconnect_error:
                        self.root.after(0, lambda: self._log_status(f"⚠️ Errore riconnessione controller: {reconnect_error}"))

                # Update real-time MIDI indicator
                self.root.after(0, lambda: self.midi_connection_var.set("✅ MIDI: Connected"))
                self.root.after(0, lambda: self.midi_connection_label.config(style='Success.TLabel'))

            except Exception as e:
                self.root.after(0, lambda: self.midi_status_var.set("❌ MIDI: Errore test"))
                self.root.after(0, lambda: self._log_status(f"❌ Errore test MIDI: {e}"))
            finally:
                # Disconnetti controller temporaneo se creato per il test
                if test_controller and test_controller != self.traktor_controller:
                    try:
                        test_controller.disconnect()
                    except:
                        pass
                self.root.after(0, lambda: self.midi_test_btn.config(state=tk.NORMAL))

        # Avvia test in thread separato
        test_thread = threading.Thread(target=run_test, daemon=True)
        test_thread.start()

    def _toggle_ai(self):
        """Toggle controllo AI"""
        self.ai_enabled = not self.ai_enabled

        if self.traktor_controller:
            self.traktor_controller.enable_ai(self.ai_enabled)

        status = "ON" if self.ai_enabled else "OFF"
        self.ai_toggle_btn.config(text=f"🤖 AI: {status}")
        self._log_status(f"🤖 AI controllo: {status}")

    def _emergency_stop(self):
        """Emergency stop"""
        if self.traktor_controller:
            self.traktor_controller.emergency_stop()

        self._log_status("🚨 EMERGENCY STOP attivato!")
        self._add_chat_message("Sistema", "🚨 EMERGENCY STOP! Tutti i volumi azzerati per sicurezza.")

    def _toggle_auto_mix(self):
        """Toggle modalità Auto-Mix autonoma"""
        self.auto_mix_active = not self.auto_mix_active

        if self.auto_mix_active:
            # Avvia auto-mix
            if not self.ai_client:
                self._add_chat_message("Sistema", "❌ Auto-Mix richiede connessione AI attiva")
                self.auto_mix_active = False
                return

            interval = self.auto_mix_interval_var.get() * 1000  # Convert to milliseconds
            self.auto_mix_btn.config(text="🎵 Auto-Mix: ON")
            self._log_status(f"🤖 Auto-Mix attivato (intervallo: {interval//1000}s)")
            self._add_chat_message("Sistema", f"🤖 Auto-Mix attivato! L'AI prenderà decisioni ogni {interval//1000} secondi.")

            # Avvia timer per decisioni autonome
            self._schedule_auto_mix_decision()
        else:
            # Disattiva auto-mix
            if self.auto_mix_timer:
                self.root.after_cancel(self.auto_mix_timer)
                self.auto_mix_timer = None
            self.auto_mix_btn.config(text="🎵 Auto-Mix: OFF")
            self._log_status("🤖 Auto-Mix disattivato")
            self._add_chat_message("Sistema", "🤖 Auto-Mix disattivato.")

    def _schedule_auto_mix_decision(self):
        """Programma prossima decisione autonoma"""
        if not self.auto_mix_active:
            return

        interval = self.auto_mix_interval_var.get() * 1000  # Convert to milliseconds
        self.auto_mix_timer = self.root.after(interval, self._make_autonomous_decision)

    def _make_autonomous_decision(self):
        """Prendi decisione autonoma basata su contesto attuale"""
        if not self.auto_mix_active or not self.ai_client:
            return

        try:
            # Construisci query contestuale per l'AI
            time_in_set = int((time.time() - self.session_start_time) / 60) if hasattr(self, 'session_start_time') else 0

            # Aggiorna contesto DJ con info attuali
            self.dj_context.time_in_set = time_in_set
            self.dj_context.energy_level = self.energy_var.get()

            # Query intelligente basata sul momento del set
            if time_in_set < 30:  # Primo 30 minuti - warm up
                query = "Siamo all'inizio del set. Come dovrei procedere per scaldare il crowd gradualmente?"
            elif time_in_set < 90:  # 30-90 min - buildup
                query = "Il set sta prendendo forma. Qual è la strategia migliore per aumentare l'energia?"
            elif time_in_set < 150:  # 90-150 min - peak time
                query = "Siamo nel momento di punta del set. Come mantengo l'energia al massimo?"
            else:  # Oltre 150 min - closing
                query = "Il set si sta avvicinando alla conclusione. Come gestisco il finale?"

            # Aggiungi info su energia attuale
            query += f" Energia attuale: {self.dj_context.energy_level}/10."

            # Richiedi decisione urgente
            threading.Thread(
                target=lambda: self._process_autonomous_decision(query),
                daemon=True
            ).start()

        except Exception as e:
            self._log_status(f"❌ Errore decisione autonoma: {e}")

        # Programma prossima decisione
        self._schedule_auto_mix_decision()

    def _process_autonomous_decision(self, query: str):
        """Processa decisione autonoma dell'AI"""
        try:
            response = self.ai_client.get_dj_decision(self.dj_context, query, urgent=True, autonomous_mode=True)

            if response.success:
                self.stats['ai_decisions'] += 1

                # Mostra decisione in chat
                self.root.after(0, lambda: self._add_chat_message("Auto-Mix AI", f"🤖 {response.response}"))

                # Aggiorna statistiche
                self.root.after(0, lambda: self.perf_status_var.set(f"⏱️ Auto-Mix: {response.processing_time_ms:.0f}ms"))

                # Esegui eventuali azioni automatiche
                if response.decision:
                    self.root.after(0, lambda: self._execute_autonomous_action(response.decision))

            else:
                self.root.after(0, lambda: self._add_chat_message("Sistema", f"❌ Errore Auto-Mix: {response.error}"))

        except Exception as e:
            self.root.after(0, lambda: self._add_chat_message("Sistema", f"❌ Errore Auto-Mix: {e}"))

    def _execute_autonomous_action(self, decision: Dict[str, Any]):
        """Esegui azioni autonome basate su decisioni AI"""
        try:
            # Aggiornamenti di energia
            if "energy_change" in decision:
                new_energy = self.dj_context.energy_level + int(decision["energy_change"])
                new_energy = max(1, min(10, new_energy))
                self.energy_var.set(new_energy)
                self.dj_context.energy_level = new_energy
                self._log_status(f"🎵 Auto-Mix: Energia aggiornata a {new_energy}/10")

            # Cambiamenti BPM suggeriti
            if "target_bpm" in decision and self.traktor_controller:
                target_bpm = float(decision["target_bpm"])
                self.dj_context.target_bpm = target_bpm
                self._log_status(f"🎵 Auto-Mix: BPM target → {target_bpm}")

            # Azioni MIDI automatiche (solo se sicure)
            if "action" in decision:
                action = decision["action"].lower()
                if action in ["fade_in", "fade_out", "eq_adjust"] and self.traktor_controller:
                    # Implementa azioni MIDI sicure
                    self._log_status(f"🎵 Auto-Mix: Eseguendo {action}")

            # Caricamento tracce automatico
            if "load_track" in decision and self.traktor_controller:
                from traktor_control import DeckID
                deck_letter = decision["load_track"].upper()
                if deck_letter in ["A", "B", "C", "D"]:
                    deck = DeckID(deck_letter)
                    direction = decision.get("browse_direction", "down")

                    # Carica nuova traccia nel deck specificato
                    success = self.traktor_controller.load_next_track_smart(deck, direction)
                    if success:
                        self._log_status(f"🎵 Auto-Mix: Traccia caricata nel Deck {deck_letter}")
                        self._add_chat_message("Auto-Mix AI", f"🎵 Nuova traccia caricata nel Deck {deck_letter}")
                    else:
                        self._log_status(f"❌ Auto-Mix: Errore caricamento Deck {deck_letter}")

            # Controlli di volume e crossfader automatici
            if "crossfader_move" in decision and self.traktor_controller:
                target_position = decision["crossfader_move"]  # 0-127
                if 0 <= target_position <= 127:
                    success = self.traktor_controller.set_crossfader(target_position / 127.0)
                    if success:
                        self._log_status(f"🎵 Auto-Mix: Crossfader → {target_position}")

            # Controlli EQ automatici
            if "eq_adjustment" in decision and self.traktor_controller:
                from traktor_control import DeckID
                eq_data = decision["eq_adjustment"]
                deck_letter = eq_data.get("deck", "A").upper()
                eq_type = eq_data.get("type", "mid")  # high, mid, low
                value = eq_data.get("value", 0.5)  # 0.0-1.0

                if deck_letter in ["A", "B", "C", "D"]:
                    deck = DeckID(deck_letter)
                    success = self.traktor_controller.set_eq(deck, eq_type, value)
                    if success:
                        self._log_status(f"🎵 Auto-Mix: Deck {deck_letter} EQ {eq_type} → {value:.2f}")

        except Exception as e:
            self._log_status(f"❌ Errore esecuzione azione autonoma: {e}")

    def _send_chat(self):
        """Invia messaggio chat"""
        message = self.chat_entry.get().strip()

        # Ignora il placeholder text
        if message == "Scrivi qui per comunicare con l'AI DJ..." or not message or not self.ai_client:
            return

        self.chat_entry.delete(0, tk.END)
        self._add_chat_message("Tu", message)

        # Ripristina focus sul campo input
        self.chat_entry.focus_set()

        # Invia ad AI in thread separato
        threading.Thread(
            target=lambda: self._process_ai_message(message),
            daemon=True
        ).start()

    def _quick_chat(self, command: str):
        """Comando rapido"""
        self.chat_entry.delete(0, tk.END)
        self.chat_entry.insert(0, command)
        self._send_chat()

    def _process_ai_message(self, message: str):
        """Processa messaggio AI"""
        try:
            # Verifica se Auto-Mix è attivo per modalità autonoma
            autonomous_mode = hasattr(self, 'auto_mix_active') and self.auto_mix_active
            response = self.ai_client.get_dj_decision(self.dj_context, message, urgent=True, autonomous_mode=autonomous_mode)

            if response.success:
                self.stats['ai_decisions'] += 1
                self.root.after(0, lambda: self._add_chat_message("AI", response.response))
                self.root.after(0, lambda: self.chat_entry.focus_set())  # Ripristina focus

                # Debug: Log decision status
                decision_status = "HAS DECISION" if response.decision else "NO DECISION"
                self._log_status(f"🔍 AI Response: {decision_status} | Autonomous: {autonomous_mode}")
                if response.decision:
                    self._log_status(f"📋 Decision JSON: {response.decision}")

                # Aggiorna statistiche performance
                self.root.after(0, lambda: self.perf_status_var.set(f"⏱️ Latenza: {response.processing_time_ms:.0f}ms"))

                # Esegui eventuali azioni
                if response.decision:
                    self._log_status(f"🎛️ Executing AI decision...")
                    self.root.after(0, lambda: self._execute_ai_decision(response.decision))
                elif autonomous_mode:
                    self._log_status(f"⚠️ Autonomous mode ON but NO decision JSON generated!")
            else:
                self.root.after(0, lambda: self._add_chat_message("Sistema", f"❌ Errore AI: {response.error}"))

        except Exception as e:
            self.root.after(0, lambda: self._add_chat_message("Sistema", f"❌ Errore: {e}"))

    def _execute_ai_decision(self, decision: Dict[str, Any]):
        """Esegui decisione AI con timing intelligente"""
        try:
            self._log_status(f"🎛️ Executing AI decision: {decision}")

            # Check for COMPLEX MIXING WORKFLOWS (highest priority)
            if "complex_workflow" in decision:
                self._log_status(f"🎛️ Detected COMPLEX MIXING workflow: {decision['complex_workflow']}")
                self._execute_mixing_workflow(decision)
                return

            # Check for MIXING MODE commands
            if "mixing_mode" in decision:
                self._log_status(f"🎚️ Detected MIXING MODE: {decision['mixing_mode']}")
                self._execute_simple_mixing(decision)
                return

            # Check for load+play combination (needs special timing)
            has_load = "load_track" in decision
            has_play = "play_deck" in decision or decision.get("play_track")

            if has_load and has_play:
                self._log_status(f"🔄 Detected LOAD+PLAY workflow - using intelligent timing")
                self._execute_load_and_play_workflow(decision)
                return

            # Implementa logica per eseguire decisioni AI singole
            if "energy_change" in decision:
                new_energy = self.dj_context.energy_level + int(decision["energy_change"])
                new_energy = max(1, min(10, new_energy))
                self.energy_var.set(new_energy)
                self._log_status(f"⚡ Energy changed to {new_energy}/10")

            if "target_bpm" in decision and self.traktor_controller:
                # Logica per BPM change
                self._log_status(f"🎵 AI suggerisce BPM: {decision['target_bpm']}")

            if "crossfader_move" in decision and self.traktor_controller:
                position = decision["crossfader_move"] / 127.0  # Convert to 0.0-1.0
                success = self.traktor_controller.set_crossfader(position)
                self._log_status(f"🎛️ Crossfader moved to {position:.2f}: {'✅' if success else '❌'}")

            # Load track only (no play)
            if "load_track" in decision and not has_play and self.traktor_controller:
                self._execute_load_command(decision)

            # Play only (no load)
            if has_play and not has_load and self.traktor_controller:
                self._execute_play_command(decision)

        except Exception as e:
            self._log_status(f"❌ Errore esecuzione decisione AI: {e}")
            import traceback
            traceback.print_exc()

    def _execute_load_and_play_workflow(self, decision: Dict[str, Any]):
        """Esegui workflow load+play con timing corretto"""
        try:
            from traktor_control import DeckID

            # Step 1: Load track
            deck_letter = decision["load_track"].upper()
            if deck_letter not in ["A", "B", "C", "D"]:
                self._log_status(f"❌ Invalid deck letter: {deck_letter}")
                return

            deck = DeckID(deck_letter)
            direction = decision.get("browse_direction", "down")

            self._log_status(f"🎵 STEP 1: Loading track to Deck {deck_letter}...")
            load_success = self.traktor_controller.load_next_track_smart(deck, direction)

            if not load_success:
                self._log_status(f"❌ Load failed - aborting workflow")
                return

            self._log_status(f"✅ Track loaded to Deck {deck_letter}")
            self._add_chat_message("Sistema", f"🎵 Traccia caricata nel Deck {deck_letter}")

            # Step 2: Wait for track to be ready
            self._log_status(f"⏱️ STEP 2: Waiting for track to be ready (2s delay)...")
            import time
            time.sleep(2.0)  # Give Traktor time to load the track

            # Step 3: Execute play command
            play_deck_letter = deck_letter
            if "play_deck" in decision:
                play_deck_letter = decision["play_deck"].upper()

            if play_deck_letter == deck_letter:
                self._log_status(f"▶️ STEP 3: Playing loaded track in Deck {deck_letter}...")
                play_success = self.traktor_controller.play_deck(deck)

                if play_success:
                    self._log_status(f"🎉 WORKFLOW SUCCESS: Deck {deck_letter} loaded and playing!")
                    self._add_chat_message("Sistema", f"🎉 Deck {deck_letter} caricato e in riproduzione!")
                else:
                    self._log_status(f"❌ Play failed after successful load")
                    self._add_chat_message("Sistema", f"⚠️ Traccia caricata ma play fallito in Deck {deck_letter}")
            else:
                self._log_status(f"⚠️ Play target ({play_deck_letter}) != Load target ({deck_letter})")

        except Exception as e:
            self._log_status(f"❌ Errore workflow load+play: {e}")
            import traceback
            traceback.print_exc()

    def _execute_load_command(self, decision: Dict[str, Any]):
        """Esegui solo comando load"""
        try:
            from traktor_control import DeckID
            deck_letter = decision["load_track"].upper()
            self._log_status(f"🎵 AI wants to load track in Deck {deck_letter}")

            if deck_letter in ["A", "B", "C", "D"]:
                deck = DeckID(deck_letter)
                direction = decision.get("browse_direction", "down")

                self._log_status(f"🎵 Loading track to Deck {deck_letter} via MIDI...")
                success = self.traktor_controller.load_next_track_smart(deck, direction)

                if success:
                    self._log_status(f"✅ Track loaded to Deck {deck_letter} successfully!")
                    self._add_chat_message("Sistema", f"🎵 Traccia caricata nel Deck {deck_letter}")
                else:
                    self._log_status(f"❌ Failed to load track to Deck {deck_letter}")
            else:
                self._log_status(f"❌ Invalid deck letter: {deck_letter}")
        except Exception as e:
            self._log_status(f"❌ Errore load command: {e}")

    def _execute_play_command(self, decision: Dict[str, Any]):
        """Esegui solo comando play"""
        try:
            from traktor_control import DeckID

            # Play specific deck
            if "play_deck" in decision:
                deck_letter = decision["play_deck"].upper()
                self._log_status(f"▶️ AI wants to play Deck {deck_letter}")

                if deck_letter in ["A", "B", "C", "D"]:
                    deck = DeckID(deck_letter)

                    # Check if deck has a track loaded (via internal state)
                    if hasattr(self.traktor_controller, 'deck_states'):
                        deck_state = self.traktor_controller.deck_states.get(deck, {})
                        if not deck_state.get('loaded', True):  # Assume loaded if no state
                            self._log_status(f"⚠️ Warning: Deck {deck_letter} may not have a track loaded")

                    self._log_status(f"▶️ Playing Deck {deck_letter} via MIDI...")
                    success = self.traktor_controller.play_deck(deck)

                    if success:
                        self._log_status(f"✅ Deck {deck_letter} playing successfully!")
                        self._add_chat_message("Sistema", f"▶️ Deck {deck_letter} sta suonando")
                    else:
                        self._log_status(f"❌ Failed to play Deck {deck_letter}")
                else:
                    self._log_status(f"❌ Invalid deck letter: {deck_letter}")

            # Generic play command - for "play_track": true
            elif decision.get("play_track"):
                self._log_status(f"▶️ AI wants to play current track (default Deck A)")
                deck = DeckID.A  # Default deck
                success = self.traktor_controller.play_deck(deck)

                if success:
                    self._log_status(f"✅ Track playing successfully!")
                    self._add_chat_message("Sistema", f"▶️ Traccia in riproduzione")
                else:
                    self._log_status(f"❌ Failed to play track")

        except Exception as e:
            self._log_status(f"❌ Errore play command: {e}")

    def _execute_mixing_workflow(self, decision: Dict[str, Any]):
        """Esegui workflow mixing complesso (es. load_B_and_mix)"""
        try:
            from traktor_control import DeckID
            import time

            workflow_type = decision.get("complex_workflow")
            self._log_status(f"🎛️ Starting complex mixing workflow: {workflow_type}")

            if workflow_type == "load_B_and_mix":
                # FASE 1: Load Track nel Deck B
                self._log_status(f"🎵 STEP 1: Loading track to Deck B...")
                load_success = self.traktor_controller.load_next_track_smart(DeckID.B, "down")

                if not load_success:
                    self._log_status(f"❌ Load B failed - aborting mixing workflow")
                    return

                self._log_status(f"✅ Track loaded to Deck B")
                self._add_chat_message("Sistema", f"🎵 Traccia caricata nel Deck B per mixing")

                # FASE 2: Wait per track ready
                self._log_status(f"⏱️ STEP 2: Waiting for Deck B track ready (2s)...")
                time.sleep(2.0)

                # FASE 3: Start playing Deck B
                self._log_status(f"▶️ STEP 3: Starting Deck B playback...")
                play_success = self.traktor_controller.play_deck(DeckID.B)

                if not play_success:
                    self._log_status(f"❌ Play B failed after load")
                    return

                self._log_status(f"✅ Deck B playing successfully")

                # FASE 4: Begin crossfade transition
                self._log_status(f"🎚️ STEP 4: Beginning crossfade transition A→B...")
                time.sleep(1.0)  # Let deck B stabilize

                # Start gradual crossfade
                self._execute_gradual_crossfade("A_to_B", decision.get("crossfader_target", 127))

            elif workflow_type == "load_A_and_mix":
                # Similar logic for A side
                self._log_status(f"🎵 STEP 1: Loading track to Deck A...")
                load_success = self.traktor_controller.load_next_track_smart(DeckID.A, "down")

                if load_success:
                    self._log_status(f"✅ Track loaded to Deck A")
                    time.sleep(2.0)
                    self.traktor_controller.play_deck(DeckID.A)
                    time.sleep(1.0)
                    self._execute_gradual_crossfade("B_to_A", decision.get("crossfader_target", 0))

            self._log_status(f"🎉 MIXING WORKFLOW COMPLETED!")
            self._add_chat_message("Sistema", f"🎛️ Mixing workflow completato con successo!")

        except Exception as e:
            self._log_status(f"❌ Errore mixing workflow: {e}")
            import traceback
            traceback.print_exc()

    def _execute_simple_mixing(self, decision: Dict[str, Any]):
        """Esegui semplice mixing tra deck già caricati"""
        try:
            mixing_mode = decision.get("mixing_mode")
            crossfader_target = decision.get("crossfader_target")

            self._log_status(f"🎚️ Starting simple mixing: {mixing_mode}")

            if crossfader_target is not None:
                # Execute gradual crossfade
                self._execute_gradual_crossfade(mixing_mode, crossfader_target)
            else:
                # Immediate crossfader move
                if "crossfader_move" in decision:
                    position = decision["crossfader_move"] / 127.0
                    success = self.traktor_controller.set_crossfader(position)
                    self._log_status(f"🎛️ Crossfader moved to {position:.2f}: {'✅' if success else '❌'}")

            # Handle volume adjustments
            if "volume_deck_a" in decision:
                volume = decision["volume_deck_a"] / 127.0
                success = self.traktor_controller.set_deck_volume(DeckID.A, volume)
                self._log_status(f"🔊 Deck A volume: {volume:.2f} {'✅' if success else '❌'}")

            if "volume_deck_b" in decision:
                volume = decision["volume_deck_b"] / 127.0
                success = self.traktor_controller.set_deck_volume(DeckID.B, volume)
                self._log_status(f"🔊 Deck B volume: {volume:.2f} {'✅' if success else '❌'}")

            self._add_chat_message("Sistema", f"🎚️ Mixing eseguito: {mixing_mode}")

        except Exception as e:
            self._log_status(f"❌ Errore simple mixing: {e}")

    def _execute_gradual_crossfade(self, mixing_mode: str, target_value: int):
        """Esegui crossfade graduale per transizioni smooth"""
        try:
            import time
            from traktor_control import DeckID

            self._log_status(f"🌀 Starting gradual crossfade: {mixing_mode} → {target_value}")

            # Get current crossfader position (assume center if unknown)
            start_position = 64  # Center position
            target_position = target_value

            # Calculate steps for smooth transition
            steps = 5
            step_size = (target_position - start_position) / steps
            step_delay = 0.8  # 800ms between steps

            for i in range(steps + 1):
                current_pos = int(start_position + (step_size * i))
                position_float = current_pos / 127.0

                success = self.traktor_controller.set_crossfader(position_float)
                self._log_status(f"🎚️ Crossfade step {i+1}/{steps+1}: {position_float:.2f} {'✅' if success else '❌'}")

                if i < steps:  # Don't wait after last step
                    time.sleep(step_delay)

            self._log_status(f"✅ Gradual crossfade completed: {target_position}/127")

            # Adjust volumes for better mix
            if mixing_mode == "A_to_B":
                # Boost B slightly, reduce A slightly
                self.traktor_controller.set_deck_volume(DeckID.B, 0.85)
                self.traktor_controller.set_deck_volume(DeckID.A, 0.75)
            elif mixing_mode == "B_to_A":
                # Boost A slightly, reduce B slightly
                self.traktor_controller.set_deck_volume(DeckID.A, 0.85)
                self.traktor_controller.set_deck_volume(DeckID.B, 0.75)

        except Exception as e:
            self._log_status(f"❌ Errore gradual crossfade: {e}")

    def _add_chat_message(self, sender: str, message: str):
        """Aggiungi messaggio alla chat"""
        timestamp = time.strftime("%H:%M")
        self.chat_text.insert(tk.END, f"[{timestamp}] {sender}: {message}\n")
        self.chat_text.see(tk.END)

    def _log_status(self, message: str):
        """Log messaggio status"""
        print(message)  # Console
        # Opzionale: aggiungi anche alla GUI se serve

    def _quit_application(self):
        """Chiudi applicazione"""
        self.running = False
        self.session_active = False

        # Save window size before closing
        try:
            geometry = self.root.geometry()
            if 'x' in geometry:
                size_part = geometry.split('+')[0]  # Get just the WIDTHxHEIGHT part
                width, height = map(int, size_part.split('x'))
                if hasattr(self.persistent_settings, 'window_width'):
                    self.persistent_settings.window_width = width
                    self.persistent_settings.window_height = height
                    self.persistent_settings.save_to_file()
        except Exception as e:
            print(f"⚠️  Error saving window size: {e}")

        if self.traktor_controller:
            self.traktor_controller.disconnect()

        if self.ai_client:
            self.ai_client.close()

        self.root.quit()
        self.root.destroy()

    def run(self):
        """Avvia interfaccia"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self._quit_application()

def main():
    """Main function"""
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    try:
        app = DJInterface()
        app.run()
    except Exception as e:
        messagebox.showerror("Errore Fatale", f"Errore avvio interfaccia: {e}")

if __name__ == "__main__":
    main()