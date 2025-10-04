#!/usr/bin/env python3
"""
🎛️ Deck Control Agent - Specialized Hardware Control
Expert in individual deck operations: play/pause, volume, loading, deck state management
"""

import time
import asyncio
import logging
from typing import Dict, List, Any, Optional
from enum import Enum

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from agents.base_agent import BaseAgent, AgentType, AgentMessage, MessageType, Priority, AgentCapability
from core.traktor_control import DeckID, get_traktor_controller
from core.config import get_config

class DeckOperation(Enum):
    """Types of deck operations"""
    PLAY = "play"
    PAUSE = "pause"
    STOP = "stop"
    LOAD_TRACK = "load_track"
    SET_VOLUME = "set_volume"
    FORCE_PLAY = "force_play"
    CUE = "cue"
    SYNC = "sync"

class DeckControlAgent(BaseAgent):
    """
    Specialized agent for deck control operations

    Responsibilities:
    - Individual deck play/pause/stop control
    - Track loading and deck state management
    - Volume control per deck
    - Cue and sync operations
    - Real-time deck status monitoring
    """

    def _initialize_agent(self):
        """Initialize deck control specific setup"""
        self.logger = logging.getLogger("Agent.DeckControl")

        # Initialize Traktor controller
        try:
            config = get_config()
            self.traktor = get_traktor_controller(config)
            self.controller_connected = False
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Traktor controller: {e}")
            self.traktor = None

        # Deck state tracking
        self.deck_states = {
            DeckID.A: {'playing': False, 'loaded': False, 'volume': 0.8, 'last_update': 0},
            DeckID.B: {'playing': False, 'loaded': False, 'volume': 0.8, 'last_update': 0},
            DeckID.C: {'playing': False, 'loaded': False, 'volume': 0.8, 'last_update': 0},
            DeckID.D: {'playing': False, 'loaded': False, 'volume': 0.8, 'last_update': 0}
        }

        # Performance tracking
        self.operation_stats = {
            'play_commands': 0,
            'load_commands': 0,
            'volume_changes': 0,
            'successful_operations': 0,
            'failed_operations': 0
        }

        # Register capabilities
        self._register_capabilities()

        self.logger.info("🎛️ Deck Control Agent initialized")

    def _register_capabilities(self):
        """Register deck control capabilities"""
        capabilities = [
            AgentCapability(
                name="deck_play_control",
                description="Play/pause/stop individual decks with anti-blinking logic",
                input_types=["deck_id", "operation"],
                output_types=["success_status", "deck_state"],
                dependencies=["traktor_controller"],
                execution_time_ms=50.0,
                reliability_score=0.95
            ),
            AgentCapability(
                name="deck_volume_control",
                description="Precise volume control for individual decks",
                input_types=["deck_id", "volume_level"],
                output_types=["success_status", "actual_volume"],
                dependencies=["traktor_controller"],
                execution_time_ms=20.0,
                reliability_score=0.98
            ),
            AgentCapability(
                name="track_loading",
                description="Load tracks to specific decks with state tracking",
                input_types=["deck_id", "track_info"],
                output_types=["load_status", "deck_state"],
                dependencies=["traktor_controller", "browser_control"],
                execution_time_ms=200.0,
                reliability_score=0.90
            ),
            AgentCapability(
                name="deck_sync_operations",
                description="Sync operations and cue control",
                input_types=["deck_id", "sync_target"],
                output_types=["sync_status"],
                dependencies=["traktor_controller"],
                execution_time_ms=100.0,
                reliability_score=0.92
            ),
            AgentCapability(
                name="deck_state_monitoring",
                description="Real-time deck state monitoring and reporting",
                input_types=["monitoring_interval"],
                output_types=["deck_states", "status_updates"],
                dependencies=["traktor_controller"],
                execution_time_ms=10.0,
                reliability_score=0.99
            )
        ]

        for cap in capabilities:
            self.register_capability(cap)

    async def _on_start(self):
        """Connect to Traktor when starting"""
        if self.traktor:
            try:
                self.controller_connected = await asyncio.to_thread(
                    self.traktor.connect_with_gil_safety,
                    output_only=True,
                    timeout=10.0
                )

                if self.controller_connected:
                    self.logger.info("✅ Traktor controller connected")
                    # Start deck monitoring
                    asyncio.create_task(self._deck_monitoring_loop())
                else:
                    self.logger.warning("⚠️ Traktor controller in simulation mode")

            except Exception as e:
                self.logger.error(f"❌ Traktor connection failed: {e}")

    async def _on_stop(self):
        """Disconnect from Traktor when stopping"""
        if self.traktor and self.controller_connected:
            try:
                await asyncio.to_thread(self.traktor.disconnect)
                self.logger.info("✅ Traktor controller disconnected")
            except Exception as e:
                self.logger.error(f"❌ Traktor disconnection error: {e}")

    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process deck control messages"""
        try:
            content = message.content
            operation = content.get('operation')

            if operation == DeckOperation.PLAY.value:
                return await self._handle_play_operation(message)
            elif operation == DeckOperation.PAUSE.value:
                return await self._handle_pause_operation(message)
            elif operation == DeckOperation.FORCE_PLAY.value:
                return await self._handle_force_play_operation(message)
            elif operation == DeckOperation.LOAD_TRACK.value:
                return await self._handle_load_track_operation(message)
            elif operation == DeckOperation.SET_VOLUME.value:
                return await self._handle_volume_operation(message)
            elif operation == DeckOperation.CUE.value:
                return await self._handle_cue_operation(message)
            elif operation == DeckOperation.SYNC.value:
                return await self._handle_sync_operation(message)
            elif operation == "get_deck_state":
                return await self._handle_get_deck_state(message)
            elif operation == "get_all_deck_states":
                return await self._handle_get_all_deck_states(message)
            else:
                return self._create_error_response(message, f"Unknown operation: {operation}")

        except Exception as e:
            self.logger.error(f"❌ Error processing message: {e}")
            return self._create_error_response(message, str(e))

    async def _handle_play_operation(self, message: AgentMessage) -> AgentMessage:
        """Handle deck play operation"""
        deck_id_str = message.content.get('deck_id')
        deck = self._parse_deck_id(deck_id_str)

        if not deck:
            return self._create_error_response(message, f"Invalid deck_id: {deck_id_str}")

        try:
            success = await asyncio.to_thread(self.traktor.play_deck, deck)

            if success:
                self.deck_states[deck]['playing'] = True
                self.deck_states[deck]['last_update'] = time.time()
                self.operation_stats['play_commands'] += 1
                self.operation_stats['successful_operations'] += 1

                # Notify other agents about deck state change
                await self._notify_deck_state_change(deck, 'playing', True)

                return self._create_success_response(message, {
                    'deck_id': deck_id_str,
                    'operation': 'play',
                    'success': True,
                    'deck_state': self.deck_states[deck].copy()
                })
            else:
                self.operation_stats['failed_operations'] += 1
                return self._create_error_response(message, f"Failed to play deck {deck_id_str}")

        except Exception as e:
            self.operation_stats['failed_operations'] += 1
            return self._create_error_response(message, f"Play operation error: {e}")

    async def _handle_force_play_operation(self, message: AgentMessage) -> AgentMessage:
        """Handle force play operation (anti-blinking)"""
        deck_id_str = message.content.get('deck_id')
        deck = self._parse_deck_id(deck_id_str)

        if not deck:
            return self._create_error_response(message, f"Invalid deck_id: {deck_id_str}")

        try:
            wait_if_recent = message.content.get('wait_if_recent_load', True)
            success = await asyncio.to_thread(
                self.traktor.force_play_deck,
                deck,
                wait_if_recent_load=wait_if_recent
            )

            if success:
                self.deck_states[deck]['playing'] = True
                self.deck_states[deck]['last_update'] = time.time()
                self.operation_stats['successful_operations'] += 1

                return self._create_success_response(message, {
                    'deck_id': deck_id_str,
                    'operation': 'force_play',
                    'success': True,
                    'anti_blinking': True,
                    'deck_state': self.deck_states[deck].copy()
                })
            else:
                self.operation_stats['failed_operations'] += 1
                return self._create_error_response(message, f"Failed to force play deck {deck_id_str}")

        except Exception as e:
            self.operation_stats['failed_operations'] += 1
            return self._create_error_response(message, f"Force play operation error: {e}")

    async def _handle_pause_operation(self, message: AgentMessage) -> AgentMessage:
        """Handle deck pause operation"""
        deck_id_str = message.content.get('deck_id')
        deck = self._parse_deck_id(deck_id_str)

        if not deck:
            return self._create_error_response(message, f"Invalid deck_id: {deck_id_str}")

        try:
            success = await asyncio.to_thread(self.traktor.pause_deck, deck)

            if success:
                self.deck_states[deck]['playing'] = False
                self.deck_states[deck]['last_update'] = time.time()
                self.operation_stats['successful_operations'] += 1

                return self._create_success_response(message, {
                    'deck_id': deck_id_str,
                    'operation': 'pause',
                    'success': True,
                    'deck_state': self.deck_states[deck].copy()
                })
            else:
                self.operation_stats['failed_operations'] += 1
                return self._create_error_response(message, f"Failed to pause deck {deck_id_str}")

        except Exception as e:
            self.operation_stats['failed_operations'] += 1
            return self._create_error_response(message, f"Pause operation error: {e}")

    async def _handle_load_track_operation(self, message: AgentMessage) -> AgentMessage:
        """Handle track loading operation"""
        deck_id_str = message.content.get('deck_id')
        deck = self._parse_deck_id(deck_id_str)

        if not deck:
            return self._create_error_response(message, f"Invalid deck_id: {deck_id_str}")

        try:
            success = await asyncio.to_thread(self.traktor.load_track_to_deck, deck)

            if success:
                self.deck_states[deck]['loaded'] = True
                self.deck_states[deck]['playing'] = False  # Reset play state
                self.deck_states[deck]['last_update'] = time.time()
                self.operation_stats['load_commands'] += 1
                self.operation_stats['successful_operations'] += 1

                # Notify other agents about track loading
                await self._notify_deck_state_change(deck, 'loaded', True)

                return self._create_success_response(message, {
                    'deck_id': deck_id_str,
                    'operation': 'load_track',
                    'success': True,
                    'deck_state': self.deck_states[deck].copy()
                })
            else:
                self.operation_stats['failed_operations'] += 1
                return self._create_error_response(message, f"Failed to load track to deck {deck_id_str}")

        except Exception as e:
            self.operation_stats['failed_operations'] += 1
            return self._create_error_response(message, f"Load track operation error: {e}")

    async def _handle_volume_operation(self, message: AgentMessage) -> AgentMessage:
        """Handle volume control operation"""
        deck_id_str = message.content.get('deck_id')
        volume = message.content.get('volume')
        deck = self._parse_deck_id(deck_id_str)

        if not deck:
            return self._create_error_response(message, f"Invalid deck_id: {deck_id_str}")

        if volume is None or not (0.0 <= volume <= 1.0):
            return self._create_error_response(message, f"Invalid volume: {volume} (must be 0.0-1.0)")

        try:
            success = await asyncio.to_thread(self.traktor.set_deck_volume, deck, volume)

            if success:
                self.deck_states[deck]['volume'] = volume
                self.deck_states[deck]['last_update'] = time.time()
                self.operation_stats['volume_changes'] += 1
                self.operation_stats['successful_operations'] += 1

                return self._create_success_response(message, {
                    'deck_id': deck_id_str,
                    'operation': 'set_volume',
                    'success': True,
                    'volume': volume,
                    'deck_state': self.deck_states[deck].copy()
                })
            else:
                self.operation_stats['failed_operations'] += 1
                return self._create_error_response(message, f"Failed to set volume for deck {deck_id_str}")

        except Exception as e:
            self.operation_stats['failed_operations'] += 1
            return self._create_error_response(message, f"Volume operation error: {e}")

    async def _handle_cue_operation(self, message: AgentMessage) -> AgentMessage:
        """Handle cue operation"""
        deck_id_str = message.content.get('deck_id')
        deck = self._parse_deck_id(deck_id_str)

        if not deck:
            return self._create_error_response(message, f"Invalid deck_id: {deck_id_str}")

        try:
            success = await asyncio.to_thread(self.traktor.cue_deck, deck)

            if success:
                self.deck_states[deck]['playing'] = False  # Cue stops playback
                self.deck_states[deck]['last_update'] = time.time()
                self.operation_stats['successful_operations'] += 1

                return self._create_success_response(message, {
                    'deck_id': deck_id_str,
                    'operation': 'cue',
                    'success': True,
                    'deck_state': self.deck_states[deck].copy()
                })
            else:
                self.operation_stats['failed_operations'] += 1
                return self._create_error_response(message, f"Failed to cue deck {deck_id_str}")

        except Exception as e:
            self.operation_stats['failed_operations'] += 1
            return self._create_error_response(message, f"Cue operation error: {e}")

    async def _handle_sync_operation(self, message: AgentMessage) -> AgentMessage:
        """Handle sync operation"""
        deck_id_str = message.content.get('deck_id')
        deck = self._parse_deck_id(deck_id_str)

        if not deck:
            return self._create_error_response(message, f"Invalid deck_id: {deck_id_str}")

        try:
            success = await asyncio.to_thread(self.traktor.sync_deck, deck)

            if success:
                self.deck_states[deck]['last_update'] = time.time()
                self.operation_stats['successful_operations'] += 1

                return self._create_success_response(message, {
                    'deck_id': deck_id_str,
                    'operation': 'sync',
                    'success': True,
                    'deck_state': self.deck_states[deck].copy()
                })
            else:
                self.operation_stats['failed_operations'] += 1
                return self._create_error_response(message, f"Failed to sync deck {deck_id_str}")

        except Exception as e:
            self.operation_stats['failed_operations'] += 1
            return self._create_error_response(message, f"Sync operation error: {e}")

    async def _handle_get_deck_state(self, message: AgentMessage) -> AgentMessage:
        """Handle get deck state request"""
        deck_id_str = message.content.get('deck_id')
        deck = self._parse_deck_id(deck_id_str)

        if not deck:
            return self._create_error_response(message, f"Invalid deck_id: {deck_id_str}")

        return self._create_success_response(message, {
            'deck_id': deck_id_str,
            'deck_state': self.deck_states[deck].copy()
        })

    async def _handle_get_all_deck_states(self, message: AgentMessage) -> AgentMessage:
        """Handle get all deck states request"""
        return self._create_success_response(message, {
            'all_deck_states': {
                deck.value: state.copy()
                for deck, state in self.deck_states.items()
            },
            'operation_stats': self.operation_stats.copy()
        })

    async def _notify_deck_state_change(self, deck: DeckID, property_name: str, value: Any):
        """Notify other agents about deck state changes"""
        if self.message_bus:
            notification = {
                'deck_id': deck.value,
                'property': property_name,
                'value': value,
                'timestamp': time.time(),
                'full_state': self.deck_states[deck].copy()
            }

            # Notify specific agents that care about deck state
            interested_agents = ['master_coordinator', 'bpm_sync', 'transition_timing']

            for agent_id in interested_agents:
                await self.send_message(
                    recipient_id=agent_id,
                    message_type=MessageType.NOTIFICATION,
                    content=notification,
                    priority=Priority.HIGH
                )

    async def _deck_monitoring_loop(self):
        """Continuous deck state monitoring"""
        while self.is_active:
            try:
                if self.traktor and self.controller_connected:
                    # Get current states from Traktor
                    for deck in [DeckID.A, DeckID.B, DeckID.C, DeckID.D]:
                        current_playing = await asyncio.to_thread(
                            self.traktor.is_deck_playing, deck
                        )

                        # Check for state changes
                        if current_playing != self.deck_states[deck]['playing']:
                            self.logger.info(f"🎵 Deck {deck.value} state changed: playing={current_playing}")
                            self.deck_states[deck]['playing'] = current_playing
                            self.deck_states[deck]['last_update'] = time.time()

                            # Notify other agents
                            await self._notify_deck_state_change(deck, 'playing', current_playing)

                await asyncio.sleep(1.0)  # Monitor every second

            except Exception as e:
                self.logger.error(f"❌ Deck monitoring error: {e}")
                await asyncio.sleep(5.0)  # Wait longer on error

    def _parse_deck_id(self, deck_id_str: str) -> Optional[DeckID]:
        """Parse deck ID string to DeckID enum"""
        if not deck_id_str:
            return None

        deck_id_upper = deck_id_str.upper()
        for deck in DeckID:
            if deck.value == deck_id_upper:
                return deck
        return None

    def _create_success_response(self, original_message: AgentMessage, content: Dict[str, Any]) -> AgentMessage:
        """Create success response message"""
        return AgentMessage(
            id=f"resp_{original_message.id}",
            sender_id=self.agent_id,
            recipient_id=original_message.sender_id,
            message_type=MessageType.RESPONSE,
            priority=original_message.priority,
            content={'success': True, **content},
            timestamp=time.time(),
            correlation_id=original_message.id
        )

    def _create_error_response(self, original_message: AgentMessage, error_message: str) -> AgentMessage:
        """Create error response message"""
        return AgentMessage(
            id=f"err_{original_message.id}",
            sender_id=self.agent_id,
            recipient_id=original_message.sender_id,
            message_type=MessageType.ERROR,
            priority=original_message.priority,
            content={'success': False, 'error': error_message},
            timestamp=time.time(),
            correlation_id=original_message.id
        )

    def get_status_info(self) -> Dict[str, Any]:
        """Get deck control specific status"""
        return {
            'controller_connected': self.controller_connected,
            'deck_states': {deck.value: state.copy() for deck, state in self.deck_states.items()},
            'operation_stats': self.operation_stats.copy(),
            'capabilities': len(self.capabilities),
            'simulation_mode': getattr(self.traktor, 'simulation_mode', False) if self.traktor else True
        }

    def _get_current_task(self) -> Optional[str]:
        """Get description of current task"""
        if not self.is_busy:
            return "monitoring_deck_states"

        # Check which decks are currently playing
        playing_decks = [deck.value for deck, state in self.deck_states.items() if state['playing']]
        if playing_decks:
            return f"managing_active_decks: {', '.join(playing_decks)}"

        return "processing_deck_operation"