#!/usr/bin/env python3
"""
🖥️ DJ AI Interface REFACTORED - Con Feedback Real-Time
Interface completamente refactored con verifica esecuzione comandi e feedback visivo
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import time
import threading
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import json

# Imports del sistema DJ
from config import DJConfig, VENUE_TYPES, EVENT_TYPES, get_config
from core.openrouter_client import OpenRouterClient, DJContext
from core.persistent_config import get_persistent_settings
from traktor_control import TraktorController, DeckID
from gui.command_executor import CommandExecutor, CommandResult, CommandStatus

logger = logging.getLogger(__name__)

class DJInterfaceRefactored:
    """
    Interfaccia DJ AI refactored con sistema di verifica comandi
    """

    def __init__(self):
        """Inizializza interfaccia refactored"""
        self.persistent_settings = get_persistent_settings()

        self.root = tk.Tk()
        self.root.title("🎧 AI DJ System v2.0 - REFACTORED with Real-Time Feedback")

        window_size = f"{self.persistent_settings.window_width}x{self.persistent_settings.window_height}"
        self.root.geometry(window_size)
        self.root.configure(bg='#1a1a1a')

        # Configurazione
        self.config = get_config()
        self.setup_complete = False

        # Componenti sistema
        self.ai_client: Optional[OpenRouterClient] = None
        self.traktor_controller: Optional[TraktorController] = None
        self.command_executor: Optional[CommandExecutor] = None

        # Context DJ
        self.dj_context = DJContext()

        # Stati UI
        self.auto_mix_active = False
        self.verification_enabled = True  # NUOVO: abilita/disabilita verifica

        # Statistiche
        self.stats = {
            'ai_decisions': 0,
            'commands_sent': 0,
            'commands_verified': 0,
            'commands_failed': 0
        }

        # Setup UI
        self._setup_refactored_ui()

        # Status thread
        self.running = False
        self.status_thread: Optional[threading.Thread] = None

    def _setup_refactored_ui(self):
        """Setup UI refactored con feedback panels"""

        # Main container
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # === TOP: Setup Panel (se non setup) ===
        self.setup_frame = tk.LabelFrame(
            main_frame,
            text="⚙️ Setup Sistema",
            bg='#2a2a2a',
            fg='white',
            font=('Arial', 12, 'bold')
        )
        self.setup_frame.pack(fill=tk.X, pady=(0, 10))
        self._create_setup_panel()

        # === MIDDLE: Control Panels ===
        control_frame = tk.Frame(main_frame, bg='#1a1a1a')
        control_frame.pack(fill=tk.BOTH, expand=True)

        # LEFT: DJ Controls + Command Feedback
        left_panel = tk.Frame(control_frame, bg='#1a1a1a')
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # DJ Controls
        self._create_dj_controls(left_panel)

        # NUOVO: Command Feedback Panel
        self._create_command_feedback_panel(left_panel)

        # RIGHT: Chat + Status
        right_panel = tk.Frame(control_frame, bg='#1a1a1a')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self._create_chat_panel(right_panel)
        self._create_status_panel(right_panel)

        # === BOTTOM: Real-Time Verification Status ===
        self._create_verification_status_panel(main_frame)

    def _create_setup_panel(self):
        """Setup panel"""
        # API Key
        tk.Label(self.setup_frame, text="API Key:", bg='#2a2a2a', fg='white').grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.api_key_var = tk.StringVar(value="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")
        tk.Entry(self.setup_frame, textvariable=self.api_key_var, width=50, show="*").grid(row=0, column=1, padx=5, pady=5)

        # Venue + Event
        tk.Label(self.setup_frame, text="Venue:", bg='#2a2a2a', fg='white').grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.venue_var = tk.StringVar(value="club")
        ttk.Combobox(self.setup_frame, textvariable=self.venue_var, values=list(VENUE_TYPES.keys()), width=20).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        tk.Label(self.setup_frame, text="Event:", bg='#2a2a2a', fg='white').grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.event_var = tk.StringVar(value="prime_time")
        ttk.Combobox(self.setup_frame, textvariable=self.event_var, values=list(EVENT_TYPES.keys()), width=20).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        # Start button
        self.start_button = tk.Button(
            self.setup_frame,
            text="🚀 Avvia Sistema",
            command=self._start_system,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10
        )
        self.start_button.grid(row=3, column=0, columnspan=2, pady=10)

    def _create_dj_controls(self, parent):
        """DJ Controls panel"""
        control_frame = tk.LabelFrame(
            parent,
            text="🎛️ DJ Controls",
            bg='#2a2a2a',
            fg='white',
            font=('Arial', 11, 'bold')
        )
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Energy slider
        tk.Label(control_frame, text="Energy Level:", bg='#2a2a2a', fg='white').pack(anchor=tk.W, padx=5)
        self.energy_var = tk.IntVar(value=5)
        energy_slider = tk.Scale(
            control_frame,
            from_=1,
            to=10,
            orient=tk.HORIZONTAL,
            variable=self.energy_var,
            bg='#2a2a2a',
            fg='white',
            highlightthickness=0
        )
        energy_slider.pack(fill=tk.X, padx=5, pady=5)

        # Quick action buttons
        buttons_frame = tk.Frame(control_frame, bg='#2a2a2a')
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(
            buttons_frame,
            text="▶️ Play A",
            command=lambda: self._quick_action_verified("play_A"),
            bg='#4CAF50',
            fg='white'
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            buttons_frame,
            text="▶️ Play B",
            command=lambda: self._quick_action_verified("play_B"),
            bg='#4CAF50',
            fg='white'
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            buttons_frame,
            text="🎵 Load A",
            command=lambda: self._quick_action_verified("load_A"),
            bg='#2196F3',
            fg='white'
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            buttons_frame,
            text="🎵 Load B",
            command=lambda: self._quick_action_verified("load_B"),
            bg='#2196F3',
            fg='white'
        ).pack(side=tk.LEFT, padx=2)

    def _create_command_feedback_panel(self, parent):
        """NUOVO: Panel per feedback comandi in real-time"""
        feedback_frame = tk.LabelFrame(
            parent,
            text="📊 Command Feedback (Real-Time)",
            bg='#2a2a2a',
            fg='white',
            font=('Arial', 11, 'bold')
        )
        feedback_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Last command status
        status_frame = tk.Frame(feedback_frame, bg='#2a2a2a')
        status_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(status_frame, text="Last Command:", bg='#2a2a2a', fg='white').pack(side=tk.LEFT)
        self.last_command_var = tk.StringVar(value="-")
        tk.Label(status_frame, textvariable=self.last_command_var, bg='#2a2a2a', fg='#4CAF50', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        # Verification status
        verify_frame = tk.Frame(feedback_frame, bg='#2a2a2a')
        verify_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(verify_frame, text="Verification:", bg='#2a2a2a', fg='white').pack(side=tk.LEFT)
        self.verification_var = tk.StringVar(value="⏸️ Idle")
        self.verification_label = tk.Label(
            verify_frame,
            textvariable=self.verification_var,
            bg='#2a2a2a',
            fg='gray',
            font=('Arial', 10, 'bold')
        )
        self.verification_label.pack(side=tk.LEFT, padx=5)

        # Success rate
        stats_frame = tk.Frame(feedback_frame, bg='#2a2a2a')
        stats_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(stats_frame, text="Success Rate:", bg='#2a2a2a', fg='white').pack(side=tk.LEFT)
        self.success_rate_var = tk.StringVar(value="0%")
        tk.Label(stats_frame, textvariable=self.success_rate_var, bg='#2a2a2a', fg='white').pack(side=tk.LEFT, padx=5)

        # Command history text area
        tk.Label(feedback_frame, text="Command History:", bg='#2a2a2a', fg='white').pack(anchor=tk.W, padx=5)
        self.command_history_text = scrolledtext.ScrolledText(
            feedback_frame,
            height=8,
            bg='#1a1a1a',
            fg='white',
            font=('Courier', 9),
            wrap=tk.WORD
        )
        self.command_history_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _create_chat_panel(self, parent):
        """Chat panel"""
        chat_frame = tk.LabelFrame(
            parent,
            text="💬 AI Chat",
            bg='#2a2a2a',
            fg='white',
            font=('Arial', 11, 'bold')
        )
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            height=15,
            bg='#1a1a1a',
            fg='white',
            font=('Arial', 10),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Chat input
        input_frame = tk.Frame(chat_frame, bg='#2a2a2a')
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        self.chat_entry = tk.Entry(input_frame, bg='#333', fg='white', font=('Arial', 10))
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.chat_entry.bind('<Return>', lambda e: self._send_chat_verified())

        tk.Button(
            input_frame,
            text="Send",
            command=self._send_chat_verified,
            bg='#4CAF50',
            fg='white'
        ).pack(side=tk.RIGHT)

    def _create_status_panel(self, parent):
        """Status panel"""
        status_frame = tk.LabelFrame(
            parent,
            text="📊 System Status",
            bg='#2a2a2a',
            fg='white',
            font=('Arial', 11, 'bold')
        )
        status_frame.pack(fill=tk.X)

        self.status_text = scrolledtext.ScrolledText(
            status_frame,
            height=6,
            bg='#1a1a1a',
            fg='#00ff00',
            font=('Courier', 9),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _create_verification_status_panel(self, parent):
        """NUOVO: Panel status verifica in tempo reale"""
        verify_frame = tk.Frame(parent, bg='#2a2a2a', relief=tk.RIDGE, bd=2)
        verify_frame.pack(fill=tk.X, pady=(10, 0))

        # Left: Overall status
        left_frame = tk.Frame(verify_frame, bg='#2a2a2a')
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)

        tk.Label(left_frame, text="🔍 Real-Time Verification:", bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.realtime_status_var = tk.StringVar(value="⏸️ System Ready")
        tk.Label(left_frame, textvariable=self.realtime_status_var, bg='#2a2a2a', fg='gray', font=('Arial', 10)).pack(side=tk.LEFT, padx=10)

        # Right: Stats
        right_frame = tk.Frame(verify_frame, bg='#2a2a2a')
        right_frame.pack(side=tk.RIGHT, padx=10, pady=5)

        self.stats_label_var = tk.StringVar(value="Commands: 0 | Verified: 0 | Failed: 0")
        tk.Label(right_frame, textvariable=self.stats_label_var, bg='#2a2a2a', fg='white', font=('Courier', 9)).pack()

    def _start_system(self):
        """Avvia sistema con command executor"""
        try:
            self._log_status("🚀 Avvio sistema refactored...")

            # Initialize AI
            api_key = self.api_key_var.get()
            self.ai_client = OpenRouterClient(api_key, "z-ai/glm-4.5-air:free")
            self._log_status("✅ AI Client initialized (z-ai/glm-4.5-air:free)")

            # Initialize Traktor controller (but don't connect yet)
            self.traktor_controller = TraktorController(self.config)
            self._log_status("🔌 Connecting to Traktor MIDI (GIL-safe)...")

            # Defer MIDI connection to avoid GIL issues with Tkinter
            # Use after() to let Tkinter release control before MIDI init
            self.root.after(100, self._connect_midi_deferred)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start system: {e}")
            import traceback
            traceback.print_exc()

    def _connect_midi_deferred(self):
        """
        Connette MIDI in modo deferred per evitare GIL issues

        Chiamato via root.after() per permettere a Tkinter di rilasciare il controllo
        prima dell'inizializzazione MIDI (che ha problemi con GIL)
        """
        try:
            # Use GIL-safe connection method
            success = self.traktor_controller.connect_with_gil_safety()

            if not success:
                messagebox.showerror("Error", "Failed to connect to Traktor MIDI")
                return

            if self.traktor_controller.simulation_mode:
                self._log_status("⚠️ Traktor MIDI in SIMULATION MODE")
                self._add_chat_message("Sistema", "⚠️ MIDI non disponibile - modalità simulazione attiva")
            else:
                self._log_status("✅ Traktor MIDI connected")

            # Now initialize Command Executor (after MIDI ready)
            self.command_executor = CommandExecutor(self.traktor_controller)

            # Setup callbacks per feedback real-time
            self.command_executor.on_command_start = self._on_command_start
            self.command_executor.on_command_success = self._on_command_success
            self.command_executor.on_command_failed = self._on_command_failed
            self.command_executor.on_verification_status = self._on_verification_update

            self._log_status("✅ Command Executor initialized with verification")

            # Update context
            self.dj_context.venue_type = self.venue_var.get()
            self.dj_context.event_type = self.event_var.get()

            # Hide setup, show controls
            self.setup_frame.pack_forget()
            self.setup_complete = True

            self._log_status("🎉 Sistema pronto! Verifica comandi abilitata.")
            self._add_chat_message("Sistema", "🎉 Sistema refactored attivo! Tutti i comandi vengono verificati con Traktor.")

            # Start status monitoring
            self.running = True
            self.status_thread = threading.Thread(target=self._status_monitor_loop, daemon=True)
            self.status_thread.start()

        except Exception as e:
            messagebox.showerror("Error", f"MIDI connection failed: {e}")
            import traceback
            traceback.print_exc()

    # === CALLBACK HANDLERS per Command Executor ===

    def _on_command_start(self, command_name: str):
        """Callback quando comando inizia"""
        self.root.after(0, lambda: self.last_command_var.set(command_name))
        self.root.after(0, lambda: self.verification_var.set("⏳ Executing..."))
        self.root.after(0, lambda: self.verification_label.config(fg='yellow'))
        self.root.after(0, lambda: self.realtime_status_var.set(f"⏳ Executing: {command_name}"))

    def _on_command_success(self, result: CommandResult):
        """Callback quando comando ha successo"""
        status_text = f"✅ VERIFIED" if result.verified else "✅ Sent"
        self.root.after(0, lambda: self.verification_var.set(status_text))
        self.root.after(0, lambda: self.verification_label.config(fg='#4CAF50'))
        self.root.after(0, lambda: self.realtime_status_var.set(f"✅ {result.command_name} - Success"))

        self.stats['commands_sent'] += 1
        if result.verified:
            self.stats['commands_verified'] += 1

        self._update_stats_display()
        self._add_to_command_history(result)

    def _on_command_failed(self, result: CommandResult):
        """Callback quando comando fallisce"""
        self.root.after(0, lambda: self.verification_var.set("❌ FAILED"))
        self.root.after(0, lambda: self.verification_label.config(fg='red'))
        self.root.after(0, lambda: self.realtime_status_var.set(f"❌ {result.command_name} - Failed"))

        self.stats['commands_sent'] += 1
        self.stats['commands_failed'] += 1

        self._update_stats_display()
        self._add_to_command_history(result)

    def _on_verification_update(self, message: str):
        """Callback per update status verifica"""
        self.root.after(0, lambda: self.realtime_status_var.set(f"🔍 {message}"))

    # === QUICK ACTIONS con Verifica ===

    def _quick_action_verified(self, action: str):
        """Esegui quick action con verifica"""
        if not self.command_executor:
            messagebox.showwarning("Warning", "Sistema non inizializzato")
            return

        def execute():
            try:
                if action == "play_A":
                    result = self.command_executor.execute_play_deck(DeckID.A)
                elif action == "play_B":
                    result = self.command_executor.execute_play_deck(DeckID.B)
                elif action == "load_A":
                    result = self.command_executor.execute_load_track(DeckID.A, "down")
                elif action == "load_B":
                    result = self.command_executor.execute_load_track(DeckID.B, "down")
                else:
                    return

                # Log result
                if result.verified:
                    self._log_status(f"✅ {action}: Comando eseguito e verificato con Traktor")
                else:
                    self._log_status(f"⚠️ {action}: Comando inviato ma verifica fallita")

            except Exception as e:
                self._log_status(f"❌ {action} error: {e}")

        threading.Thread(target=execute, daemon=True).start()

    def _send_chat_verified(self):
        """Send chat con esecuzione verificata"""
        message = self.chat_entry.get().strip()
        if not message or not self.ai_client:
            return

        self.chat_entry.delete(0, tk.END)
        self._add_chat_message("Tu", message)

        # Process in thread
        threading.Thread(
            target=lambda: self._process_ai_with_verification(message),
            daemon=True
        ).start()

    def _process_ai_with_verification(self, message: str):
        """Process AI message con command executor"""
        try:
            response = self.ai_client.get_dj_decision(
                self.dj_context,
                message,
                urgent=True,
                autonomous_mode=True
            )

            if response.success:
                self.root.after(0, lambda: self._add_chat_message("AI", response.response))

                # Esegui decision con verifica
                if response.decision and self.command_executor:
                    self._execute_decision_verified(response.decision)

            else:
                self.root.after(0, lambda: self._add_chat_message("Sistema", f"❌ AI Error: {response.error}"))

        except Exception as e:
            self.root.after(0, lambda: self._add_chat_message("Sistema", f"❌ Error: {e}"))

    def _execute_decision_verified(self, decision: Dict[str, Any]):
        """Esegui AI decision usando command executor"""
        try:
            self._log_status(f"🎛️ Executing AI decision with verification: {decision}")

            # Load track
            if "load_track" in decision:
                deck_letter = decision["load_track"].upper()
                if deck_letter in ["A", "B", "C", "D"]:
                    deck = DeckID(deck_letter)
                    direction = decision.get("browse_direction", "down")

                    result = self.command_executor.execute_load_track(deck, direction)

                    if result.verified:
                        self._add_chat_message("Sistema", f"✅ Traccia caricata e verificata in Deck {deck_letter}")
                    else:
                        self._add_chat_message("Sistema", f"⚠️ Comando load inviato ma verifica fallita")

                    # Se c'è anche play, aspetta e poi esegui
                    if decision.get("play_track") or "play_deck" in decision:
                        time.sleep(2.0)  # Aspetta che traccia sia pronta

            # Play deck
            if decision.get("play_track") or "play_deck" in decision:
                play_deck_letter = decision.get("play_deck", decision.get("load_track", "A")).upper()
                if play_deck_letter in ["A", "B", "C", "D"]:
                    deck = DeckID(play_deck_letter)

                    result = self.command_executor.execute_play_deck(deck)

                    if result.verified:
                        self._add_chat_message("Sistema", f"✅ Deck {play_deck_letter} in riproduzione verificata")
                    else:
                        self._add_chat_message("Sistema", f"⚠️ Comando play inviato ma verifica fallita")

            # Crossfader
            if "crossfader_move" in decision:
                position = decision["crossfader_move"] / 127.0
                result = self.command_executor.execute_crossfader(position)

        except Exception as e:
            self._log_status(f"❌ Error executing decision: {e}")

    # === UI HELPERS ===

    def _add_chat_message(self, sender: str, message: str):
        """Add message to chat"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"[{sender}] {message}\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def _log_status(self, message: str):
        """Log to status panel"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)

    def _add_to_command_history(self, result: CommandResult):
        """Add command result to history display"""
        status_icon = "✅" if result.status == CommandStatus.SUCCESS and result.verified else "❌"
        verify_text = "VERIFIED" if result.verified else "NOT VERIFIED"

        history_line = f"{status_icon} {result.command_name} | {result.execution_time_ms:.0f}ms | {verify_text}\n"

        self.command_history_text.config(state=tk.NORMAL)
        self.command_history_text.insert(tk.END, history_line)
        self.command_history_text.see(tk.END)
        self.command_history_text.config(state=tk.NORMAL)

    def _update_stats_display(self):
        """Update statistics display"""
        if self.command_executor:
            success_rate = self.command_executor.get_success_rate() * 100
            self.success_rate_var.set(f"{success_rate:.0f}%")

            # Add MIDI monitor stats if available
            midi_stats = self.command_executor.get_midi_monitor_stats()
            if midi_stats:
                stats_text = (
                    f"Commands: {self.stats['commands_sent']} | "
                    f"Verified: {self.stats['commands_verified']} | "
                    f"Failed: {self.stats['commands_failed']} | "
                    f"MIDI Success: {midi_stats['success_rate']:.0f}%"
                )
            else:
                stats_text = (
                    f"Commands: {self.stats['commands_sent']} | "
                    f"Verified: {self.stats['commands_verified']} | "
                    f"Failed: {self.stats['commands_failed']}"
                )

            self.stats_label_var.set(stats_text)
        else:
            self.stats_label_var.set(
                f"Commands: {self.stats['commands_sent']} | "
                f"Verified: {self.stats['commands_verified']} | "
                f"Failed: {self.stats['commands_failed']}"
            )

    def _status_monitor_loop(self):
        """Monitor status in background"""
        while self.running:
            try:
                # Periodic update
                time.sleep(2.0)
            except Exception as e:
                logger.error(f"Status monitor error: {e}")

    def run(self):
        """Run GUI"""
        self.root.mainloop()

    def cleanup(self):
        """Cleanup on exit"""
        self.running = False
        if self.traktor_controller:
            self.traktor_controller.disconnect()

def main():
    """Main entry point"""
    logging.basicConfig(level=logging.INFO)
    interface = DJInterfaceRefactored()

    try:
        interface.run()
    finally:
        interface.cleanup()

if __name__ == "__main__":
    main()