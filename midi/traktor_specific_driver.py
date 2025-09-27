#!/usr/bin/env python3
"""
🎛️ Traktor-Specific MIDI Driver - Enhanced Communication
Implements Traktor Pro specific MIDI communication patterns based on Steinberg MIDI Remote API research
"""

import mido
import rtmidi
import time
import threading
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import platform

logger = logging.getLogger(__name__)

class TraktorMIDIMode(Enum):
    """Traktor MIDI communication modes"""
    DIRECT_PORT = "direct_port"           # Direct connection to Traktor MIDI port
    VIRTUAL_BRIDGE = "virtual_bridge"     # Virtual port bridge method
    BIDIRECTIONAL = "bidirectional"       # Two-way communication
    REAL_TIME = "real_time"              # Ultra-low latency mode

@dataclass
class TraktorDevice:
    """Traktor device configuration"""
    name: str
    input_port: Optional[str] = None
    output_port: Optional[str] = None
    device_id: int = 0
    channel: int = 0
    active: bool = False
    last_ping: float = 0.0

class TraktorMIDIDriver:
    """
    Enhanced MIDI driver specifically designed for Traktor Pro communication
    Based on Steinberg MIDI Remote API patterns and professional audio software integration
    """

    def __init__(self, device_name: str = "TraktorPy_Enhanced"):
        """Initialize Traktor-specific MIDI driver"""
        self.device_name = device_name
        self.running = False
        self.traktor_devices: Dict[str, TraktorDevice] = {}

        # MIDI objects
        self.midi_in = None
        self.midi_out = None
        self.virtual_in = None
        self.virtual_out = None

        # Traktor communication state
        self.traktor_detected = False
        self.communication_active = False
        self.last_traktor_response = 0.0

        # Performance monitoring
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'traktor_pings': 0,
            'communication_errors': 0,
            'start_time': 0.0
        }

        # Threading
        self.heartbeat_thread = None
        self.listener_thread = None
        self._stop_event = threading.Event()

        logger.info(f"🎛️ Traktor MIDI Driver initialized: {device_name}")

    def scan_traktor_devices(self) -> List[TraktorDevice]:
        """Scan for available Traktor MIDI devices"""
        devices = []

        try:
            # Scan input ports
            midi_in = rtmidi.MidiIn()
            input_ports = midi_in.get_ports()

            # Scan output ports
            midi_out = rtmidi.MidiOut()
            output_ports = midi_out.get_ports()

            # Look for Traktor-specific port names
            traktor_patterns = [
                'traktor', 'TRAKTOR', 'Traktor',
                'Native Instruments', 'NI', 'DJ',
                'Controller', 'S2', 'S4', 'Z2'
            ]

            # Find Traktor input ports
            traktor_inputs = []
            for i, port in enumerate(input_ports):
                for pattern in traktor_patterns:
                    if pattern.lower() in port.lower():
                        traktor_inputs.append((i, port))
                        logger.info(f"📥 Found Traktor input port: {port}")
                        break

            # Find Traktor output ports
            traktor_outputs = []
            for i, port in enumerate(output_ports):
                for pattern in traktor_patterns:
                    if pattern.lower() in port.lower():
                        traktor_outputs.append((i, port))
                        logger.info(f"📤 Found Traktor output port: {port}")
                        break

            # Create device mappings
            for i, (port_idx, port_name) in enumerate(traktor_inputs):
                device = TraktorDevice(
                    name=f"Traktor_Input_{i}",
                    input_port=port_name,
                    device_id=i
                )
                devices.append(device)
                self.traktor_devices[device.name] = device

            for i, (port_idx, port_name) in enumerate(traktor_outputs):
                device_name = f"Traktor_Output_{i}"
                if device_name in self.traktor_devices:
                    self.traktor_devices[device_name].output_port = port_name
                else:
                    device = TraktorDevice(
                        name=device_name,
                        output_port=port_name,
                        device_id=i + 100  # Offset for outputs
                    )
                    devices.append(device)
                    self.traktor_devices[device.name] = device

            if devices:
                logger.info(f"✅ Found {len(devices)} Traktor MIDI devices")
                self.traktor_detected = True
            else:
                logger.warning("⚠️ No Traktor MIDI devices detected")
                logger.info("💡 Make sure Traktor Pro is running and MIDI is enabled")

            return devices

        except Exception as e:
            logger.error(f"❌ Error scanning Traktor devices: {e}")
            return []

    def create_enhanced_virtual_ports(self) -> bool:
        """Create virtual MIDI ports with enhanced Traktor compatibility"""
        try:
            logger.info("🔧 Creating enhanced virtual MIDI ports for Traktor...")

            # Create virtual output port (we send TO Traktor)
            try:
                self.virtual_out = rtmidi.MidiOut()
                virtual_out_name = f"{self.device_name}_TO_Traktor"

                if platform.system() == "Darwin":  # macOS
                    # Use IAC Driver for better compatibility
                    self.virtual_out.open_virtual_port(virtual_out_name)
                elif platform.system() == "Windows":
                    # Windows virtual port creation
                    self.virtual_out.open_virtual_port(virtual_out_name)
                else:  # Linux
                    # ALSA virtual port
                    self.virtual_out.open_virtual_port(virtual_out_name)

                logger.info(f"✅ Created virtual output port: {virtual_out_name}")

            except Exception as e:
                logger.error(f"❌ Failed to create virtual output port: {e}")
                return False

            # Create virtual input port (we receive FROM Traktor)
            try:
                self.virtual_in = rtmidi.MidiIn()
                virtual_in_name = f"{self.device_name}_FROM_Traktor"

                self.virtual_in.open_virtual_port(virtual_in_name)
                self.virtual_in.set_callback(self._midi_input_callback)

                logger.info(f"✅ Created virtual input port: {virtual_in_name}")

            except Exception as e:
                logger.error(f"❌ Failed to create virtual input port: {e}")
                return False

            # Small delay to ensure ports are registered
            time.sleep(0.5)

            return True

        except Exception as e:
            logger.error(f"❌ Enhanced virtual port creation failed: {e}")
            return False

    def connect_to_traktor_direct(self) -> bool:
        """Attempt direct connection to Traktor MIDI ports"""
        try:
            logger.info("🔗 Attempting direct connection to Traktor...")

            # Try to connect to first available Traktor output port
            midi_out = rtmidi.MidiOut()
            output_ports = midi_out.get_ports()

            traktor_port_idx = None
            for i, port in enumerate(output_ports):
                if any(pattern.lower() in port.lower()
                      for pattern in ['traktor', 'native', 'controller']):
                    traktor_port_idx = i
                    logger.info(f"🎯 Found Traktor port: {port}")
                    break

            if traktor_port_idx is not None:
                self.midi_out = rtmidi.MidiOut()
                self.midi_out.open_port(traktor_port_idx)
                logger.info(f"✅ Connected directly to Traktor port {traktor_port_idx}")
                return True
            else:
                logger.warning("⚠️ No direct Traktor ports found")
                return False

        except Exception as e:
            logger.error(f"❌ Direct Traktor connection failed: {e}")
            return False

    def start_traktor_communication(self) -> bool:
        """Start enhanced Traktor MIDI communication"""
        try:
            logger.info("🚀 Starting Traktor MIDI communication...")
            self.stats['start_time'] = time.time()
            self._stop_event.clear()

            # Step 1: Scan for Traktor devices
            devices = self.scan_traktor_devices()

            # Step 2: Try direct connection first
            direct_success = self.connect_to_traktor_direct()

            # Step 3: Create virtual ports if direct connection fails
            if not direct_success:
                logger.info("📡 Direct connection failed, creating virtual ports...")
                virtual_success = self.create_enhanced_virtual_ports()
                if not virtual_success:
                    logger.error("❌ Both direct and virtual connection methods failed")
                    return False

            # Step 4: Start heartbeat thread for Traktor detection
            self.heartbeat_thread = threading.Thread(
                target=self._traktor_heartbeat,
                daemon=True
            )
            self.heartbeat_thread.start()

            # Step 5: Start MIDI listener thread
            self.listener_thread = threading.Thread(
                target=self._midi_listener,
                daemon=True
            )
            self.listener_thread.start()

            self.running = True
            self.communication_active = True

            # Step 6: Send initial ping to Traktor
            self.ping_traktor()

            logger.info("✅ Traktor MIDI communication started successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start Traktor communication: {e}")
            return False

    def ping_traktor(self) -> bool:
        """Send ping signal to Traktor to test communication"""
        try:
            # Send a safe MIDI CC message that won't interfere with mixing
            # CC 127 is often unused and safe for testing
            ping_message = [0xB0, 127, 64]  # Control Change, CC 127, value 64

            success = self._send_midi_message(ping_message)

            if success:
                self.stats['traktor_pings'] += 1
                self.last_traktor_response = time.time()
                logger.debug("📡 Ping sent to Traktor")

                # Immediately send another message to make MIDI icon blink
                time.sleep(0.1)
                ping_off = [0xB0, 127, 0]  # Turn off the CC
                self._send_midi_message(ping_off)

            return success

        except Exception as e:
            logger.error(f"❌ Traktor ping failed: {e}")
            self.stats['communication_errors'] += 1
            return False

    def send_traktor_control(self, cc_number: int, value: int, channel: int = 0) -> bool:
        """Send control change message to Traktor with enhanced error handling"""
        try:
            # Validate parameters
            if not (0 <= cc_number <= 127):
                logger.error(f"❌ Invalid CC number: {cc_number} (must be 0-127)")
                return False

            if not (0 <= value <= 127):
                logger.error(f"❌ Invalid CC value: {value} (must be 0-127)")
                return False

            if not (0 <= channel <= 15):
                logger.error(f"❌ Invalid MIDI channel: {channel} (must be 0-15)")
                return False

            # Create MIDI Control Change message
            midi_message = [0xB0 + channel, cc_number, value]

            success = self._send_midi_message(midi_message)

            if success:
                logger.debug(f"🎛️ Sent to Traktor: CC {cc_number}={value} (Ch {channel})")
            else:
                logger.warning(f"⚠️ Failed to send CC {cc_number}={value}")

            return success

        except Exception as e:
            logger.error(f"❌ Traktor control send error: {e}")
            self.stats['communication_errors'] += 1
            return False

    def _send_midi_message(self, message: List[int]) -> bool:
        """Internal method to send MIDI message with fallback options"""
        try:
            # Try direct connection first
            if self.midi_out:
                self.midi_out.send_message(message)
                self.stats['messages_sent'] += 1
                return True

            # Fall back to virtual port
            if self.virtual_out:
                self.virtual_out.send_message(message)
                self.stats['messages_sent'] += 1
                return True

            logger.error("❌ No MIDI output available")
            return False

        except Exception as e:
            logger.error(f"❌ MIDI message send error: {e}")
            self.stats['communication_errors'] += 1
            return False

    def _midi_input_callback(self, message, data):
        """Handle incoming MIDI messages from Traktor"""
        try:
            midi_message, timestamp = message
            self.stats['messages_received'] += 1

            # Update last response time
            self.last_traktor_response = time.time()

            logger.debug(f"📥 Received from Traktor: {midi_message}")

            # Here you can add specific response handling for Traktor

        except Exception as e:
            logger.error(f"❌ MIDI input callback error: {e}")

    def _traktor_heartbeat(self):
        """Background thread to maintain Traktor communication"""
        while not self._stop_event.is_set():
            try:
                if self.running:
                    # Send heartbeat ping every 3 seconds (as mentioned by user)
                    self.ping_traktor()

                    # Check communication health
                    time_since_response = time.time() - self.last_traktor_response
                    if time_since_response > 10:  # 10 seconds timeout
                        logger.warning("⚠️ No response from Traktor in 10 seconds")

                # Wait 3 seconds before next heartbeat
                self._stop_event.wait(3.0)

            except Exception as e:
                logger.error(f"❌ Heartbeat error: {e}")
                self._stop_event.wait(1.0)

    def _midi_listener(self):
        """Background thread to listen for MIDI events"""
        while not self._stop_event.is_set():
            try:
                # Keep the listener alive
                self._stop_event.wait(0.1)

            except Exception as e:
                logger.error(f"❌ MIDI listener error: {e}")
                self._stop_event.wait(1.0)

    def get_traktor_status(self) -> Dict[str, Any]:
        """Get comprehensive Traktor communication status"""
        uptime = time.time() - self.stats['start_time'] if self.stats['start_time'] else 0

        return {
            'traktor_detected': self.traktor_detected,
            'communication_active': self.communication_active,
            'direct_connection': self.midi_out is not None,
            'virtual_ports_active': self.virtual_out is not None,
            'last_response_ago': time.time() - self.last_traktor_response if self.last_traktor_response else None,
            'devices_found': len(self.traktor_devices),
            'uptime_seconds': round(uptime, 1),
            'stats': self.stats.copy()
        }

    def stop(self):
        """Stop Traktor MIDI communication"""
        logger.info("🛑 Stopping Traktor MIDI communication...")

        self.running = False
        self.communication_active = False
        self._stop_event.set()

        # Wait for threads to finish
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=2.0)

        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=2.0)

        # Close MIDI connections
        try:
            if self.midi_out:
                self.midi_out.close()
            if self.midi_in:
                self.midi_in.close()
            if self.virtual_out:
                self.virtual_out.close()
            if self.virtual_in:
                self.virtual_in.close()
        except:
            pass

        logger.info("✅ Traktor MIDI communication stopped")

# Global instance
_traktor_driver = None

def get_traktor_driver() -> TraktorMIDIDriver:
    """Get the global Traktor MIDI driver instance"""
    global _traktor_driver
    if _traktor_driver is None:
        _traktor_driver = TraktorMIDIDriver()
    return _traktor_driver