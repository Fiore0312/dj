#!/usr/bin/env python3
"""
🎛️ Autonomous Mixing Controller
Real-time MIDI control for autonomous DJ mixing operations
Handles beatmatching, crossfading, EQ automation, and effects
"""

import time
import math
import threading
import logging
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import queue
import json

# MIDI dependencies
try:
    import rtmidi
    import mido
    MIDI_AVAILABLE = True
except ImportError:
    MIDI_AVAILABLE = False
    print("⚠️ MIDI libraries not available. Install python-rtmidi and mido")

# Core components
from config import DJConfig, get_config
from autonomous_decision_engine import DJDecision, DecisionType, DecisionUrgency

logger = logging.getLogger(__name__)

class MixTransitionType(Enum):
    """Types of mixing transitions"""
    CUT = "cut"                    # Instant cut
    FADE = "fade"                  # Linear crossfade
    FILTER_FADE = "filter_fade"    # Fade with filter sweep
    ECHO_FADE = "echo_fade"        # Fade with echo/delay
    SCRATCH_MIX = "scratch_mix"    # Quick scratch transition
    LOOP_ROLL = "loop_roll"        # Loop roll transition
    AIR_HORN = "air_horn"          # Air horn effect transition

class MixingState(Enum):
    """Current mixing state"""
    IDLE = "idle"
    PREPARING = "preparing"
    MIXING = "mixing"
    FINALIZING = "finalizing"

@dataclass
class MixParameters:
    """Parameters for a mixing operation"""
    transition_type: MixTransitionType
    duration_seconds: float
    start_position: float  # Position in current track to start mix
    target_deck: str  # 'A' or 'B'

    # Beatmatching
    sync_bpm: bool = True
    bpm_adjustment: float = 0.0  # Manual BPM offset

    # Crossfader curve
    crossfader_curve: str = "linear"  # linear, log, exp

    # EQ settings
    eq_automation: bool = True
    low_cut_source: bool = True   # Cut lows on outgoing track
    high_boost_target: bool = True # Boost highs on incoming track

    # Effects
    use_effects: bool = True
    effect_type: Optional[str] = None
    effect_intensity: float = 0.5

@dataclass
class DeckState:
    """State of a virtual deck"""
    deck_id: str  # 'A' or 'B'
    is_playing: bool = False
    is_prepared: bool = False

    # Track info
    track_path: Optional[str] = None
    track_bpm: float = 120.0
    track_key: Optional[str] = None

    # Position and timing
    position_seconds: float = 0.0
    position_beats: float = 0.0

    # MIDI controls
    volume: float = 0.8
    eq_high: float = 0.5
    eq_mid: float = 0.5
    eq_low: float = 0.5
    gain: float = 0.5

    # Sync and effects
    sync_enabled: bool = False
    effect_1_on: bool = False
    effect_2_on: bool = False

class AutonomousMixingController:
    """Autonomous MIDI mixing controller for Traktor Pro"""

    def __init__(self, config: DJConfig = None):
        self.config = config or get_config()

        # MIDI setup
        self.midi_out = None
        self.midi_in = None
        self.is_connected = False

        # Deck states
        self.deck_a = DeckState('A')
        self.deck_b = DeckState('B')
        self.active_deck = 'A'

        # Mixing state
        self.mixing_state = MixingState.IDLE
        self.current_mix_params: Optional[MixParameters] = None
        self.mix_start_time: Optional[float] = None

        # Crossfader and master controls
        self.crossfader_position = 0.0  # -1 (A) to 1 (B)
        self.master_volume = 0.8

        # Real-time processing
        self.control_queue = queue.Queue()
        self.is_processing = False
        self.processing_thread = None

        # Callbacks for feedback
        self.status_callback: Optional[Callable] = None
        self.error_callback: Optional[Callable] = None

        # Performance tracking
        self.mix_history: List[Dict] = []
        self.timing_precision_ms = 10  # Target precision

        print("🎛️ Autonomous Mixing Controller initialized")

    def connect_midi(self) -> bool:
        """Connect to MIDI devices"""
        if not MIDI_AVAILABLE:
            print("❌ MIDI not available")
            return False

        try:
            # Initialize MIDI output
            self.midi_out = rtmidi.MidiOut()

            # Find IAC Driver or virtual MIDI port
            available_ports = self.midi_out.get_ports()
            print(f"🎹 Available MIDI ports: {available_ports}")

            # Look for IAC Driver (macOS) or virtual port
            target_port = None
            for i, port_name in enumerate(available_ports):
                if any(name in port_name.lower() for name in ['iac', 'bus', 'virtual', 'traktor']):
                    target_port = i
                    break

            if target_port is not None:
                self.midi_out.open_port(target_port)
                print(f"✅ Connected to MIDI port: {available_ports[target_port]}")

                # Also setup MIDI input for feedback
                self.midi_in = rtmidi.MidiIn()
                if len(self.midi_in.get_ports()) > target_port:
                    self.midi_in.open_port(target_port)
                    self.midi_in.set_callback(self._midi_callback)
                    print("🎧 MIDI input callback setup")

                self.is_connected = True
                return True
            else:
                print("⚠️ No suitable MIDI port found")
                return False

        except Exception as e:
            print(f"❌ MIDI connection failed: {e}")
            return False

    def start_processing(self):
        """Start real-time processing thread"""
        if self.is_processing:
            return

        self.is_processing = True
        self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.processing_thread.start()
        print("🔄 Mixing controller processing started")

    def stop_processing(self):
        """Stop processing and disconnect MIDI"""
        self.is_processing = False

        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2.0)

        if self.midi_out:
            self.midi_out.close_port()
        if self.midi_in:
            self.midi_in.close_port()

        print("⏹️ Mixing controller stopped")

    def _processing_loop(self):
        """Main real-time processing loop"""
        while self.is_processing:
            try:
                # Process control commands
                while not self.control_queue.empty():
                    command = self.control_queue.get_nowait()
                    self._execute_control_command(command)

                # Update mixing automation
                if self.mixing_state == MixingState.MIXING:
                    self._update_mix_automation()

                # Send status updates
                self._send_status_update()

                # Precise timing
                time.sleep(self.timing_precision_ms / 1000.0)

            except Exception as e:
                logger.error(f"Error in mixing controller loop: {e}")
                time.sleep(0.1)

    def execute_mix_decision(self, decision: DJDecision):
        """Execute a mixing decision from the decision engine"""
        try:
            if decision.decision_type == DecisionType.MIX_TIMING:
                action = decision.decision_data.get('action')

                if action == 'start_transition':
                    self._start_autonomous_mix()
                elif action == 'prepare_next_track':
                    self._prepare_next_track(decision.decision_data)

            elif decision.decision_type == DecisionType.TRANSITION_TYPE:
                transition_type = decision.decision_data.get('transition_type', 'fade')
                self._set_transition_type(transition_type)

            elif decision.decision_type == DecisionType.ENERGY_MANAGEMENT:
                adjustment = decision.decision_data.get('adjustment')
                self._adjust_energy_level(adjustment)

        except Exception as e:
            logger.error(f"Error executing mix decision: {e}")

    def _start_autonomous_mix(self):
        """Start an autonomous mix transition"""
        if self.mixing_state != MixingState.IDLE:
            print("⚠️ Already mixing, cannot start new mix")
            return

        try:
            # Determine target deck
            target_deck = 'B' if self.active_deck == 'A' else 'A'

            # Create default mix parameters
            mix_params = MixParameters(
                transition_type=MixTransitionType.FADE,
                duration_seconds=16.0,  # 16 beats at 120 BPM = 8 seconds
                start_position=0.0,
                target_deck=target_deck,
                sync_bpm=True,
                eq_automation=True,
                use_effects=True
            )

            self._execute_mix_transition(mix_params)

        except Exception as e:
            logger.error(f"Error starting autonomous mix: {e}")

    def _execute_mix_transition(self, params: MixParameters):
        """Execute a complete mix transition"""
        try:
            print(f"🎵 Starting {params.transition_type.value} transition to deck {params.target_deck}")

            self.current_mix_params = params
            self.mixing_state = MixingState.PREPARING
            self.mix_start_time = time.time()

            # Phase 1: Preparation
            self._prepare_mix_transition(params)

            # Phase 2: Execute transition
            self.mixing_state = MixingState.MIXING

            # Queue the transition steps
            self._queue_transition_steps(params)

        except Exception as e:
            logger.error(f"Error executing mix transition: {e}")
            self.mixing_state = MixingState.IDLE

    def _prepare_mix_transition(self, params: MixParameters):
        """Prepare for mix transition"""
        try:
            target_deck = self.deck_b if params.target_deck == 'B' else self.deck_a

            # Ensure target deck is prepared
            if not target_deck.is_prepared:
                print(f"⚠️ Deck {params.target_deck} not prepared")
                return

            # Sync BPMs if requested
            if params.sync_bpm:
                self._enable_sync(params.target_deck)

            # Set initial EQ positions for smooth transition
            if params.eq_automation:
                self._setup_transition_eq(params)

            # Prepare effects if needed
            if params.use_effects and params.effect_type:
                self._setup_transition_effects(params)

            print(f"✅ Mix preparation complete for deck {params.target_deck}")

        except Exception as e:
            logger.error(f"Error preparing mix transition: {e}")

    def _queue_transition_steps(self, params: MixParameters):
        """Queue the automation steps for transition"""
        try:
            duration = params.duration_seconds
            steps = int(duration / (self.timing_precision_ms / 1000.0))

            for step in range(steps):
                progress = step / steps  # 0.0 to 1.0

                # Calculate automation values
                automation_command = {
                    'type': 'automation_step',
                    'progress': progress,
                    'params': params,
                    'execute_time': time.time() + (step * self.timing_precision_ms / 1000.0)
                }

                self.control_queue.put(automation_command)

            # Final step: complete transition
            final_command = {
                'type': 'complete_transition',
                'params': params,
                'execute_time': time.time() + duration
            }
            self.control_queue.put(final_command)

        except Exception as e:
            logger.error(f"Error queuing transition steps: {e}")

    def _update_mix_automation(self):
        """Update ongoing mix automation"""
        if not self.current_mix_params or not self.mix_start_time:
            return

        try:
            elapsed = time.time() - self.mix_start_time
            progress = elapsed / self.current_mix_params.duration_seconds

            if progress >= 1.0:
                self._complete_mix_transition()
                return

            # Update crossfader position
            new_crossfader = self._calculate_crossfader_position(progress)
            self._set_crossfader(new_crossfader)

            # Update EQ automation
            if self.current_mix_params.eq_automation:
                self._update_eq_automation(progress)

        except Exception as e:
            logger.error(f"Error updating mix automation: {e}")

    def _calculate_crossfader_position(self, progress: float) -> float:
        """Calculate crossfader position based on progress and curve"""
        if not self.current_mix_params:
            return self.crossfader_position

        curve = self.current_mix_params.crossfader_curve

        if curve == "linear":
            # Linear fade from current position to opposite
            start_pos = -1.0 if self.active_deck == 'A' else 1.0
            end_pos = 1.0 if self.active_deck == 'A' else -1.0
            return start_pos + (end_pos - start_pos) * progress

        elif curve == "log":
            # Logarithmic curve for smoother perception
            if progress < 0.5:
                return -1.0 + (2.0 * progress * progress)
            else:
                return 2.0 * progress - 1.0

        elif curve == "exp":
            # Exponential curve for quick cuts
            return -1.0 + 2.0 * (progress ** 2)

        else:
            return -1.0 + 2.0 * progress  # Default linear

    def _set_crossfader(self, position: float):
        """Set crossfader position via MIDI"""
        position = max(-1.0, min(1.0, position))  # Clamp to valid range
        self.crossfader_position = position

        if self.is_connected and self.midi_out:
            # Convert -1..1 to 0..127 MIDI range
            midi_value = int((position + 1.0) * 63.5)
            midi_value = max(0, min(127, midi_value))

            # Send MIDI CC for crossfader (typically CC 8)
            self._send_midi_cc(8, midi_value)

    def _update_eq_automation(self, progress: float):
        """Update EQ automation during transition"""
        try:
            if not self.current_mix_params:
                return

            # Source deck (fading out) - gradually cut lows
            if self.current_mix_params.low_cut_source:
                source_low = 0.5 * (1.0 - progress)  # Fade from 0.5 to 0
                self._set_deck_eq(self.active_deck, 'low', source_low)

            # Target deck (fading in) - gradually boost highs
            if self.current_mix_params.high_boost_target:
                target_high = 0.5 + 0.3 * progress  # Boost from 0.5 to 0.8
                target_deck = self.current_mix_params.target_deck
                self._set_deck_eq(target_deck, 'high', target_high)

        except Exception as e:
            logger.error(f"Error updating EQ automation: {e}")

    def _set_deck_eq(self, deck: str, band: str, value: float):
        """Set EQ value for specific deck and band"""
        value = max(0.0, min(1.0, value))

        if deck == 'A':
            deck_state = self.deck_a
            base_cc = 20  # Base CC for deck A
        else:
            deck_state = self.deck_b
            base_cc = 30  # Base CC for deck B

        # Update state
        if band == 'high':
            deck_state.eq_high = value
            cc_num = base_cc + 0
        elif band == 'mid':
            deck_state.eq_mid = value
            cc_num = base_cc + 1
        elif band == 'low':
            deck_state.eq_low = value
            cc_num = base_cc + 2
        else:
            return

        # Send MIDI
        if self.is_connected and self.midi_out:
            midi_value = int(value * 127)
            self._send_midi_cc(cc_num, midi_value)

    def _complete_mix_transition(self):
        """Complete the current mix transition"""
        try:
            if self.current_mix_params:
                # Switch active deck
                self.active_deck = self.current_mix_params.target_deck

                # Reset EQ to neutral on source deck
                old_deck = 'A' if self.active_deck == 'B' else 'B'
                self._reset_deck_eq(old_deck)

                # Record mix history
                mix_record = {
                    'timestamp': time.time(),
                    'transition_type': self.current_mix_params.transition_type.value,
                    'duration': self.current_mix_params.duration_seconds,
                    'success': True
                }
                self.mix_history.append(mix_record)

            self.mixing_state = MixingState.IDLE
            self.current_mix_params = None
            self.mix_start_time = None

            print(f"✅ Mix transition complete - active deck: {self.active_deck}")

        except Exception as e:
            logger.error(f"Error completing mix transition: {e}")

    def _reset_deck_eq(self, deck: str):
        """Reset deck EQ to neutral"""
        self._set_deck_eq(deck, 'high', 0.5)
        self._set_deck_eq(deck, 'mid', 0.5)
        self._set_deck_eq(deck, 'low', 0.5)

    def _enable_sync(self, deck: str):
        """Enable BPM sync for specified deck"""
        try:
            deck_state = self.deck_b if deck == 'B' else self.deck_a
            deck_state.sync_enabled = True

            if self.is_connected and self.midi_out:
                # Send sync enable MIDI command
                cc_num = 40 if deck == 'A' else 50  # Sync CC
                self._send_midi_cc(cc_num, 127)  # Enable sync

            print(f"🔄 Sync enabled for deck {deck}")

        except Exception as e:
            logger.error(f"Error enabling sync: {e}")

    def _setup_transition_eq(self, params: MixParameters):
        """Setup EQ for transition"""
        # Pre-position EQ for smooth transition
        source_deck = self.active_deck
        target_deck = params.target_deck

        # Source starts neutral, target starts with low cut
        self._set_deck_eq(target_deck, 'low', 0.2)  # Cut lows on incoming track

    def _setup_transition_effects(self, params: MixParameters):
        """Setup effects for transition"""
        if params.effect_type == "filter":
            # Setup filter sweep effect
            pass
        elif params.effect_type == "echo":
            # Setup echo/delay effect
            pass

    def _execute_control_command(self, command: Dict):
        """Execute a queued control command"""
        try:
            command_type = command.get('type')

            if command_type == 'automation_step':
                # Check if it's time to execute
                execute_time = command.get('execute_time', 0)
                if time.time() >= execute_time:
                    progress = command['progress']
                    params = command['params']

                    # Update crossfader
                    new_position = self._calculate_crossfader_position(progress)
                    self._set_crossfader(new_position)

                    # Update EQ
                    if params.eq_automation:
                        self._update_eq_automation(progress)
                else:
                    # Re-queue for later
                    self.control_queue.put(command)

            elif command_type == 'complete_transition':
                execute_time = command.get('execute_time', 0)
                if time.time() >= execute_time:
                    self._complete_mix_transition()
                else:
                    self.control_queue.put(command)

        except Exception as e:
            logger.error(f"Error executing control command: {e}")

    def _send_midi_cc(self, cc_number: int, value: int):
        """Send MIDI CC message"""
        try:
            if self.midi_out and self.is_connected:
                # Create MIDI CC message
                message = [0xB0, cc_number, value]  # Control Change on channel 1
                self.midi_out.send_message(message)

        except Exception as e:
            logger.error(f"Error sending MIDI CC: {e}")

    def _midi_callback(self, message, data=None):
        """Handle incoming MIDI messages"""
        try:
            # Process feedback from Traktor
            if message[0] and len(message[0]) >= 3:
                status, cc, value = message[0][:3]

                # Update internal state based on feedback
                if cc == 8:  # Crossfader feedback
                    self.crossfader_position = (value / 127.0) * 2.0 - 1.0

        except Exception as e:
            logger.error(f"Error in MIDI callback: {e}")

    def _send_status_update(self):
        """Send status update to callback"""
        if self.status_callback:
            try:
                status = {
                    'mixing_state': self.mixing_state.value,
                    'active_deck': self.active_deck,
                    'crossfader_position': self.crossfader_position,
                    'deck_a': {
                        'playing': self.deck_a.is_playing,
                        'volume': self.deck_a.volume,
                        'eq_high': self.deck_a.eq_high,
                        'eq_mid': self.deck_a.eq_mid,
                        'eq_low': self.deck_a.eq_low
                    },
                    'deck_b': {
                        'playing': self.deck_b.is_playing,
                        'volume': self.deck_b.volume,
                        'eq_high': self.deck_b.eq_high,
                        'eq_mid': self.deck_b.eq_mid,
                        'eq_low': self.deck_b.eq_low
                    }
                }
                self.status_callback(status)
            except Exception as e:
                logger.error(f"Error sending status update: {e}")

    def set_status_callback(self, callback: Callable):
        """Set callback for status updates"""
        self.status_callback = callback

    def set_error_callback(self, callback: Callable):
        """Set callback for error notifications"""
        self.error_callback = callback

    def get_mixing_stats(self) -> Dict:
        """Get mixing performance statistics"""
        return {
            'total_mixes': len(self.mix_history),
            'successful_mixes': sum(1 for mix in self.mix_history if mix.get('success')),
            'current_state': self.mixing_state.value,
            'active_deck': self.active_deck,
            'crossfader_position': self.crossfader_position,
            'is_connected': self.is_connected
        }

def test_mixing_controller():
    """Test the autonomous mixing controller"""
    print("🧪 Testing Autonomous Mixing Controller")
    print("=" * 50)

    # Initialize controller
    config = get_config()
    controller = AutonomousMixingController(config)

    # Test MIDI connection
    print("\n🎹 Testing MIDI connection...")
    if controller.connect_midi():
        print("✅ MIDI connected successfully")
    else:
        print("⚠️ MIDI not connected, using simulation mode")

    # Start processing
    controller.start_processing()

    # Test status callback
    def status_callback(status):
        print(f"📊 Status: {status['mixing_state']} - Active: Deck {status['active_deck']}")

    controller.set_status_callback(status_callback)

    # Simulate autonomous mix
    print("\n🎵 Testing autonomous mix transition...")
    controller._start_autonomous_mix()

    # Wait for mix to complete
    time.sleep(5)

    # Get stats
    stats = controller.get_mixing_stats()
    print(f"\n📈 Mixing Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Stop controller
    controller.stop_processing()

    print("\n✅ Mixing controller test complete!")

if __name__ == "__main__":
    test_mixing_controller()