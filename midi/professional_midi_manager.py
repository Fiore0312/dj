#!/usr/bin/env python3
"""
🎛️ Professional MIDI Manager
Robust cross-platform MIDI virtual port management with guaranteed reliability
"""

import time
import threading
import platform
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
import queue

try:
    import mido
    from mido import Message
    MIDO_AVAILABLE = True
except ImportError:
    print("❌ mido not available. Install with: pip install mido python-rtmidi")
    MIDO_AVAILABLE = False

try:
    import rtmidi
    RTMIDI_AVAILABLE = True
except ImportError:
    print("❌ rtmidi not available. Install with: pip install python-rtmidi")
    RTMIDI_AVAILABLE = False

# Import Traktor-specific driver
from .traktor_specific_driver import get_traktor_driver

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MIDIPortStatus(Enum):
    """MIDI port status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RECONNECTING = "reconnecting"

class MIDIMessageType(Enum):
    """MIDI message types for DJ operations"""
    NOTE_ON = "note_on"
    NOTE_OFF = "note_off"
    CONTROL_CHANGE = "control_change"
    PROGRAM_CHANGE = "program_change"
    PITCH_BEND = "pitchwheel"

@dataclass
class MIDIPortConfig:
    """Configuration for MIDI ports"""
    name: str
    port_type: str  # "input" or "output"
    virtual: bool = True
    auto_reconnect: bool = True
    latency_mode: str = "ultra_low"  # ultra_low, low, normal
    buffer_size: int = 1
    callback: Optional[Callable] = None

@dataclass
class MIDIEvent:
    """Standardized MIDI event"""
    timestamp: float
    message_type: MIDIMessageType
    channel: int
    note_or_cc: int
    velocity_or_value: int
    port_name: str
    raw_message: Any = None

class ProfessionalMIDIManager:
    """
    Professional MIDI manager with guaranteed virtual port creation and management
    """

    def __init__(self):
        """Initialize the Professional MIDI Manager"""
        self.platform = platform.system()
        self.input_ports: Dict[str, Any] = {}
        self.output_ports: Dict[str, Any] = {}
        self.port_status: Dict[str, MIDIPortStatus] = {}
        self.callbacks: Dict[str, List[Callable]] = {}
        self.message_queue = queue.Queue()
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Traktor-specific integration
        self.traktor_driver = None
        self.traktor_mode = False

        # Performance monitoring
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'latency_samples': [],
            'errors': 0,
            'reconnections': 0,
            'uptime_start': time.time(),
            'traktor_pings': 0,
            'traktor_errors': 0
        }

        # Port configurations
        self.default_ports = {
            'TraktorPy_Virtual': MIDIPortConfig(
                name='TraktorPy_Virtual',
                port_type='output',
                virtual=True,
                auto_reconnect=True,
                latency_mode='ultra_low'
            ),
            'TraktorPy_Virtual_In': MIDIPortConfig(
                name='TraktorPy_Virtual_In',
                port_type='input',
                virtual=True,
                auto_reconnect=True,
                latency_mode='ultra_low',
                callback=self._default_input_callback
            )
        }

        logger.info(f"🎛️ Professional MIDI Manager initialized on {self.platform}")

    def start(self, enable_traktor: bool = True) -> bool:
        """Start the MIDI manager and create virtual ports"""
        if not MIDO_AVAILABLE:
            logger.error("❌ mido library not available")
            return False

        try:
            logger.info("🚀 Starting Professional MIDI Manager...")

            # Create default virtual ports
            success = self._create_all_virtual_ports()

            if success:
                # Initialize Traktor-specific driver if requested
                if enable_traktor and RTMIDI_AVAILABLE:
                    logger.info("🎛️ Enabling Traktor-specific communication...")
                    try:
                        self.traktor_driver = get_traktor_driver()
                        traktor_success = self.traktor_driver.start_traktor_communication()
                        if traktor_success:
                            self.traktor_mode = True
                            logger.info("✅ Traktor MIDI communication enabled")
                        else:
                            logger.warning("⚠️ Traktor communication failed, continuing with standard MIDI")
                    except Exception as e:
                        logger.warning(f"⚠️ Traktor driver initialization failed: {e}")

                # Start monitoring thread
                self.running = True
                self.monitor_thread = threading.Thread(
                    target=self._port_monitor_loop,
                    daemon=True
                )
                self.monitor_thread.start()

                logger.info("✅ Professional MIDI Manager started successfully")
                self._print_port_summary()
                return True
            else:
                logger.error("❌ Failed to create virtual ports")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to start MIDI manager: {e}")
            return False

    def _create_all_virtual_ports(self) -> bool:
        """Create all configured virtual ports with platform optimization"""
        success_count = 0

        for port_name, config in self.default_ports.items():
            try:
                if config.port_type == "output":
                    success = self._create_virtual_output_port(config)
                else:
                    success = self._create_virtual_input_port(config)

                if success:
                    success_count += 1
                    self.port_status[port_name] = MIDIPortStatus.CONNECTED
                    logger.info(f"✅ Created {config.port_type} port: {port_name}")
                else:
                    self.port_status[port_name] = MIDIPortStatus.ERROR
                    logger.error(f"❌ Failed to create {config.port_type} port: {port_name}")

            except Exception as e:
                logger.error(f"❌ Exception creating port {port_name}: {e}")
                self.port_status[port_name] = MIDIPortStatus.ERROR

        return success_count == len(self.default_ports)

    def _create_virtual_output_port(self, config: MIDIPortConfig) -> bool:
        """Create a virtual output port with platform-specific optimization"""
        try:
            # Platform-specific port creation
            if self.platform == "Darwin":  # macOS
                port = mido.open_output(
                    config.name,
                    virtual=True,
                    autoreset=True
                )
            elif self.platform == "Windows":
                port = mido.open_output(
                    config.name,
                    virtual=True
                )
            else:  # Linux
                port = mido.open_output(
                    config.name,
                    virtual=True
                )

            # Configure for ultra-low latency
            if hasattr(port, '_port'):
                if hasattr(port._port, 'ignore_types'):
                    port._port.ignore_types(timing=False, active_sensing=False)

            self.output_ports[config.name] = port
            return True

        except Exception as e:
            logger.error(f"❌ Failed to create output port {config.name}: {e}")
            return False

    def _create_virtual_input_port(self, config: MIDIPortConfig) -> bool:
        """Create a virtual input port with callback handling"""
        try:
            # Create input port with callback
            if config.callback:
                port = mido.open_input(
                    config.name,
                    virtual=True,
                    callback=config.callback
                )
            else:
                port = mido.open_input(
                    config.name,
                    virtual=True
                )

            self.input_ports[config.name] = port
            self.callbacks[config.name] = []

            if config.callback:
                self.callbacks[config.name].append(config.callback)

            return True

        except Exception as e:
            logger.error(f"❌ Failed to create input port {config.name}: {e}")
            return False

    def _default_input_callback(self, message):
        """Default callback for MIDI input messages"""
        try:
            midi_event = self._parse_midi_message(message, "TraktorPy_Virtual_In")
            self.message_queue.put(midi_event)
            self.stats['messages_received'] += 1

            logger.debug(f"📨 Received: {message}")

        except Exception as e:
            logger.error(f"❌ Error processing input message: {e}")
            self.stats['errors'] += 1

    def _parse_midi_message(self, message, port_name: str) -> MIDIEvent:
        """Parse mido message into standardized MIDIEvent"""
        timestamp = time.time()

        if message.type == 'note_on':
            return MIDIEvent(
                timestamp=timestamp,
                message_type=MIDIMessageType.NOTE_ON,
                channel=message.channel,
                note_or_cc=message.note,
                velocity_or_value=message.velocity,
                port_name=port_name,
                raw_message=message
            )
        elif message.type == 'note_off':
            return MIDIEvent(
                timestamp=timestamp,
                message_type=MIDIMessageType.NOTE_OFF,
                channel=message.channel,
                note_or_cc=message.note,
                velocity_or_value=message.velocity,
                port_name=port_name,
                raw_message=message
            )
        elif message.type == 'control_change':
            return MIDIEvent(
                timestamp=timestamp,
                message_type=MIDIMessageType.CONTROL_CHANGE,
                channel=message.channel,
                note_or_cc=message.control,
                velocity_or_value=message.value,
                port_name=port_name,
                raw_message=message
            )
        else:
            # Generic event for other message types
            return MIDIEvent(
                timestamp=timestamp,
                message_type=MIDIMessageType.CONTROL_CHANGE,  # Default
                channel=getattr(message, 'channel', 0),
                note_or_cc=0,
                velocity_or_value=0,
                port_name=port_name,
                raw_message=message
            )

    def send_control_change(self, cc_number: int, value: int, channel: int = 0,
                           port_name: str = "TraktorPy_Virtual") -> bool:
        """Send a control change message with Traktor optimization"""
        try:
            # Use Traktor-specific driver if available and active
            if self.traktor_mode and self.traktor_driver:
                start_time = time.perf_counter()
                success = self.traktor_driver.send_traktor_control(cc_number, value, channel)
                latency = (time.perf_counter() - start_time) * 1000

                if success:
                    self.stats['messages_sent'] += 1
                    self.stats['traktor_pings'] += 1
                    self.stats['latency_samples'].append(latency)
                    logger.debug(f"🎛️ Sent to Traktor: CC {cc_number}={value} Ch{channel} ({latency:.2f}ms)")
                else:
                    self.stats['traktor_errors'] += 1
                    logger.warning(f"⚠️ Traktor send failed, falling back to standard MIDI")

                # If Traktor communication successful, also send via standard MIDI for compatibility
                if success:
                    self._send_standard_midi_cc(cc_number, value, channel, port_name)

                return success

            # Fall back to standard MIDI
            return self._send_standard_midi_cc(cc_number, value, channel, port_name)

        except Exception as e:
            logger.error(f"❌ Enhanced CC send error: {e}")
            self.stats['errors'] += 1
            return False

    def _send_standard_midi_cc(self, cc_number: int, value: int, channel: int = 0,
                              port_name: str = "TraktorPy_Virtual") -> bool:
        """Send standard MIDI control change message"""
        try:
            if port_name not in self.output_ports:
                logger.error(f"❌ Output port {port_name} not available")
                return False

            port = self.output_ports[port_name]
            message = Message('control_change',
                            channel=channel,
                            control=cc_number,
                            value=value)

            start_time = time.perf_counter()
            port.send(message)
            latency = (time.perf_counter() - start_time) * 1000

            self.stats['messages_sent'] += 1
            self.stats['latency_samples'].append(latency)

            # Keep only last 100 latency samples
            if len(self.stats['latency_samples']) > 100:
                self.stats['latency_samples'] = self.stats['latency_samples'][-100:]

            logger.debug(f"📤 Standard MIDI CC {cc_number}={value} Ch{channel} ({latency:.2f}ms)")
            return True

        except Exception as e:
            logger.error(f"❌ Standard MIDI CC send error: {e}")
            self.stats['errors'] += 1
            return False

    def send_note(self, note: int, velocity: int, channel: int = 0,
                  note_on: bool = True, port_name: str = "TraktorPy_Virtual") -> bool:
        """Send a note on/off message"""
        try:
            if port_name not in self.output_ports:
                logger.error(f"❌ Output port {port_name} not available")
                return False

            port = self.output_ports[port_name]
            message_type = 'note_on' if note_on else 'note_off'
            message = Message(message_type,
                            channel=channel,
                            note=note,
                            velocity=velocity)

            start_time = time.perf_counter()
            port.send(message)
            latency = (time.perf_counter() - start_time) * 1000

            self.stats['messages_sent'] += 1
            self.stats['latency_samples'].append(latency)

            logger.debug(f"📤 Sent {message_type} {note} vel={velocity} ch={channel}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send note message: {e}")
            self.stats['errors'] += 1
            return False

    def _port_monitor_loop(self):
        """Monitor port health and reconnect if needed"""
        while self.running:
            try:
                # Check port status
                for port_name, status in self.port_status.items():
                    if status == MIDIPortStatus.ERROR:
                        logger.info(f"🔄 Attempting to reconnect port: {port_name}")
                        self._attempt_port_reconnection(port_name)

                # Process message queue
                try:
                    while not self.message_queue.empty():
                        event = self.message_queue.get_nowait()
                        self._process_incoming_event(event)
                except queue.Empty:
                    pass

                time.sleep(1.0)  # Monitor every second

            except Exception as e:
                logger.error(f"❌ Error in port monitor: {e}")
                time.sleep(5.0)

    def _attempt_port_reconnection(self, port_name: str) -> bool:
        """Attempt to reconnect a failed port"""
        try:
            self.port_status[port_name] = MIDIPortStatus.RECONNECTING

            # Close existing port if it exists
            if port_name in self.output_ports:
                try:
                    self.output_ports[port_name].close()
                    del self.output_ports[port_name]
                except:
                    pass

            if port_name in self.input_ports:
                try:
                    self.input_ports[port_name].close()
                    del self.input_ports[port_name]
                except:
                    pass

            # Recreate port
            config = self.default_ports.get(port_name)
            if config:
                if config.port_type == "output":
                    success = self._create_virtual_output_port(config)
                else:
                    success = self._create_virtual_input_port(config)

                if success:
                    self.port_status[port_name] = MIDIPortStatus.CONNECTED
                    self.stats['reconnections'] += 1
                    logger.info(f"✅ Reconnected port: {port_name}")
                    return True
                else:
                    self.port_status[port_name] = MIDIPortStatus.ERROR
                    return False

        except Exception as e:
            logger.error(f"❌ Failed to reconnect port {port_name}: {e}")
            self.port_status[port_name] = MIDIPortStatus.ERROR
            return False

    def _process_incoming_event(self, event: MIDIEvent):
        """Process incoming MIDI events"""
        # Notify registered callbacks
        if event.port_name in self.callbacks:
            for callback in self.callbacks[event.port_name]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"❌ Error in callback: {e}")

    def add_input_callback(self, port_name: str, callback: Callable[[MIDIEvent], None]):
        """Add a callback for incoming MIDI events"""
        if port_name not in self.callbacks:
            self.callbacks[port_name] = []

        self.callbacks[port_name].append(callback)
        logger.info(f"📝 Added callback for port: {port_name}")

    def get_available_ports(self) -> Dict[str, List[str]]:
        """Get all available MIDI ports"""
        try:
            return {
                'input_ports': mido.get_input_names(),
                'output_ports': mido.get_output_names(),
                'virtual_inputs': list(self.input_ports.keys()),
                'virtual_outputs': list(self.output_ports.keys())
            }
        except Exception as e:
            logger.error(f"❌ Failed to get available ports: {e}")
            return {'input_ports': [], 'output_ports': [], 'virtual_inputs': [], 'virtual_outputs': []}

    def _print_port_summary(self):
        """Print summary of created ports"""
        print("\n🎛️ MIDI Port Summary")
        print("=" * 40)

        ports = self.get_available_ports()

        print(f"📥 Virtual Input Ports ({len(ports['virtual_inputs'])}):")
        for port in ports['virtual_inputs']:
            status = self.port_status.get(port, MIDIPortStatus.DISCONNECTED)
            print(f"   ✅ {port} ({status.value})")

        print(f"\n📤 Virtual Output Ports ({len(ports['virtual_outputs'])}):")
        for port in ports['virtual_outputs']:
            status = self.port_status.get(port, MIDIPortStatus.DISCONNECTED)
            print(f"   ✅ {port} ({status.value})")

        print(f"\n🔍 System MIDI Ports:")
        print(f"   Input: {ports['input_ports']}")
        print(f"   Output: {ports['output_ports']}")

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics with Traktor integration"""
        uptime = time.time() - self.stats['uptime_start']
        avg_latency = (sum(self.stats['latency_samples']) / len(self.stats['latency_samples'])
                      if self.stats['latency_samples'] else 0.0)

        stats = {
            'uptime_seconds': round(uptime, 1),
            'messages_sent': self.stats['messages_sent'],
            'messages_received': self.stats['messages_received'],
            'average_latency_ms': round(avg_latency, 3),
            'max_latency_ms': max(self.stats['latency_samples']) if self.stats['latency_samples'] else 0,
            'min_latency_ms': min(self.stats['latency_samples']) if self.stats['latency_samples'] else 0,
            'errors': self.stats['errors'],
            'reconnections': self.stats['reconnections'],
            'active_ports': len([s for s in self.port_status.values() if s == MIDIPortStatus.CONNECTED]),
            'port_status': {name: status.value for name, status in self.port_status.items()},
            'traktor_mode': self.traktor_mode,
            'traktor_pings': self.stats.get('traktor_pings', 0),
            'traktor_errors': self.stats.get('traktor_errors', 0)
        }

        # Add Traktor-specific stats if available
        if self.traktor_driver:
            traktor_status = self.traktor_driver.get_traktor_status()
            stats['traktor_status'] = traktor_status

        return stats

    def test_latency(self, iterations: int = 10) -> Dict[str, float]:
        """Test MIDI latency with multiple iterations"""
        print(f"⏱️ Testing MIDI latency ({iterations} iterations)...")

        latencies = []
        for i in range(iterations):
            start_time = time.perf_counter()
            success = self.send_control_change(1, i % 128)
            if success:
                latency = (time.perf_counter() - start_time) * 1000
                latencies.append(latency)
            time.sleep(0.01)

        if latencies:
            results = {
                'average_ms': sum(latencies) / len(latencies),
                'min_ms': min(latencies),
                'max_ms': max(latencies),
                'success_rate': len(latencies) / iterations * 100
            }

            print(f"📊 Latency Results:")
            print(f"   Average: {results['average_ms']:.3f}ms")
            print(f"   Min: {results['min_ms']:.3f}ms")
            print(f"   Max: {results['max_ms']:.3f}ms")
            print(f"   Success Rate: {results['success_rate']:.1f}%")

            return results
        else:
            print("❌ No successful latency measurements")
            return {}

    def stop(self):
        """Stop the MIDI manager and close all ports"""
        logger.info("🛑 Stopping Professional MIDI Manager...")

        self.running = False

        # Stop Traktor driver first
        if self.traktor_driver:
            try:
                self.traktor_driver.stop()
                logger.info("🎛️ Traktor MIDI driver stopped")
            except Exception as e:
                logger.error(f"❌ Error stopping Traktor driver: {e}")

        # Wait for monitor thread to finish
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)

        # Close all ports
        for name, port in self.output_ports.items():
            try:
                port.close()
                logger.info(f"🔌 Closed output port: {name}")
            except Exception as e:
                logger.error(f"❌ Error closing output port {name}: {e}")

        for name, port in self.input_ports.items():
            try:
                port.close()
                logger.info(f"🔌 Closed input port: {name}")
            except Exception as e:
                logger.error(f"❌ Error closing input port {name}: {e}")

        self.output_ports.clear()
        self.input_ports.clear()
        self.port_status.clear()

        logger.info("✅ Professional MIDI Manager stopped")

# Global MIDI manager instance
_midi_manager = None

def get_midi_manager() -> ProfessionalMIDIManager:
    """Get the global MIDI manager instance"""
    global _midi_manager
    if _midi_manager is None:
        _midi_manager = ProfessionalMIDIManager()
    return _midi_manager

# Example usage and testing
def test_professional_midi():
    """Test the Professional MIDI Manager"""
    print("🎛️ Testing Professional MIDI Manager")
    print("=" * 50)

    if not MIDO_AVAILABLE:
        print("❌ mido library not available for testing")
        return

    # Initialize and start MIDI manager
    midi_mgr = get_midi_manager()

    if midi_mgr.start():
        print("\n✅ MIDI Manager started successfully")

        # Test latency
        midi_mgr.test_latency(5)

        # Test control change messages
        print("\n🎛️ Testing control change messages...")
        for cc in [1, 2, 3]:
            success = midi_mgr.send_control_change(cc, 64)
            print(f"   CC {cc}: {'✅' if success else '❌'}")

        # Test note messages
        print("\n🎵 Testing note messages...")
        for note in [60, 64, 67]:  # C, E, G
            success = midi_mgr.send_note(note, 100, note_on=True)
            time.sleep(0.1)
            success &= midi_mgr.send_note(note, 0, note_on=False)
            print(f"   Note {note}: {'✅' if success else '❌'}")

        # Show performance stats
        print("\n📊 Performance Statistics:")
        stats = midi_mgr.get_performance_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")

        # Keep running for a few seconds to show monitoring
        print("\n⏳ Running for 3 seconds to demonstrate monitoring...")
        time.sleep(3)

        # Stop the manager
        midi_mgr.stop()

    else:
        print("❌ Failed to start MIDI Manager")

if __name__ == "__main__":
    test_professional_midi()