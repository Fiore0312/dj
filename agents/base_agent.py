#!/usr/bin/env python3
"""
🤖 Base Agent Architecture - Foundation for 16 Specialized DJ Agents
Provides common functionality, communication protocols, and shared interfaces
"""

import time
import json
import logging
import asyncio
import threading
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

class AgentType(Enum):
    """Types of specialized agents"""
    # Hardware Controls (5 agents)
    DECK_CONTROL = "deck_control"
    MIXER_CONTROL = "mixer_control"
    HOTCUE_CONTROL = "hotcue_control"
    TRANSPORT_CONTROL = "transport_control"
    LOOP_CONTROL = "loop_control"

    # Effects (2 agents)
    FX_CREATIVE = "fx_creative"
    FX_TECHNICAL = "fx_technical"

    # Musical Intelligence (4 agents)
    BPM_SYNC = "bpm_sync"
    KEY_HARMONIC = "key_harmonic"
    ENERGY_FLOW = "energy_flow"
    TRANSITION_TIMING = "transition_timing"

    # Browser/Library (2 agents)
    MUSIC_DISCOVERY = "music_discovery"
    LIBRARY_MANAGEMENT = "library_management"

    # Web Research (2 agents)
    TRACK_RESEARCH = "track_research"
    TREND_ANALYSIS = "trend_analysis"

    # Coordination (1 agent)
    MASTER_COORDINATOR = "master_coordinator"

class MessageType(Enum):
    """Inter-agent message types"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    COMMAND = "command"
    STATUS_UPDATE = "status_update"
    ERROR = "error"
    HEARTBEAT = "heartbeat"

class Priority(Enum):
    """Message priority levels"""
    CRITICAL = 1  # Emergency stops, safety
    HIGH = 2      # Real-time mixing operations
    MEDIUM = 3    # Track loading, FX changes
    LOW = 4       # Background tasks, analysis

@dataclass
class AgentMessage:
    """Standard message format for inter-agent communication"""
    id: str
    sender_id: str
    recipient_id: str
    message_type: MessageType
    priority: Priority
    content: Dict[str, Any]
    timestamp: float
    requires_response: bool = False
    timeout_seconds: float = 5.0
    correlation_id: Optional[str] = None

@dataclass
class AgentCapability:
    """Agent capability definition"""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    dependencies: List[str]
    execution_time_ms: float
    reliability_score: float

@dataclass
class AgentStatus:
    """Agent status information"""
    agent_id: str
    agent_type: AgentType
    is_active: bool
    is_busy: bool
    last_heartbeat: float
    performance_metrics: Dict[str, float]
    current_task: Optional[str]
    error_count: int
    uptime_seconds: float

class BaseAgent(ABC):
    """
    Base class for all specialized DJ agents

    Provides:
    - Message handling and routing
    - Status monitoring and reporting
    - Common utilities and interfaces
    - Error handling and recovery
    - Performance metrics
    """

    def __init__(self, agent_type: AgentType, agent_id: Optional[str] = None):
        self.agent_type = agent_type
        self.agent_id = agent_id or f"{agent_type.value}_{uuid.uuid4().hex[:8]}"

        # Core state
        self.is_active = False
        self.is_busy = False
        self.start_time = time.time()
        self.last_heartbeat = time.time()

        # Message handling
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.response_handlers: Dict[str, Callable] = {}
        self.subscriptions: List[str] = []

        # Performance tracking
        self.performance_metrics = {
            'messages_processed': 0,
            'total_execution_time': 0.0,
            'average_response_time': 0.0,
            'error_count': 0,
            'success_rate': 1.0
        }

        # Configuration and capabilities
        self.capabilities: List[AgentCapability] = []
        self.dependencies: List[str] = []
        self.config: Dict[str, Any] = {}

        # Communication bus (will be injected)
        self.message_bus: Optional['MessageBus'] = None

        # Logging
        self.logger = logging.getLogger(f"Agent.{self.agent_type.value}")

        # Human override system
        self.human_override_enabled = True
        self.override_active = False

        # Initialize agent-specific setup
        self._initialize_agent()

    @abstractmethod
    def _initialize_agent(self):
        """Initialize agent-specific configuration and capabilities"""
        pass

    @abstractmethod
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming message and return response if needed"""
        pass

    @abstractmethod
    def get_status_info(self) -> Dict[str, Any]:
        """Get agent-specific status information"""
        pass

    async def start(self):
        """Start the agent"""
        self.is_active = True
        self.logger.info(f"🤖 Agent {self.agent_id} starting...")

        # Start message processing loop
        asyncio.create_task(self._message_processing_loop())
        asyncio.create_task(self._heartbeat_loop())

        await self._on_start()
        self.logger.info(f"✅ Agent {self.agent_id} started successfully")

    async def stop(self):
        """Stop the agent"""
        self.logger.info(f"🛑 Agent {self.agent_id} stopping...")
        self.is_active = False

        await self._on_stop()
        self.logger.info(f"✅ Agent {self.agent_id} stopped")

    async def _on_start(self):
        """Called when agent starts (override in subclasses)"""
        pass

    async def _on_stop(self):
        """Called when agent stops (override in subclasses)"""
        pass

    async def _message_processing_loop(self):
        """Main message processing loop"""
        while self.is_active:
            try:
                # Get message with timeout
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )

                await self._handle_message(message)

            except asyncio.TimeoutError:
                # No message received, continue loop
                continue
            except Exception as e:
                self.logger.error(f"❌ Message processing error: {e}")
                self.performance_metrics['error_count'] += 1

    async def _handle_message(self, message: AgentMessage):
        """Handle a single message"""
        start_time = time.time()

        try:
            self.is_busy = True

            # Check for human override
            if self.override_active and message.priority != Priority.CRITICAL:
                self.logger.warning(f"⚠️ Message blocked by human override: {message.id}")
                return

            # Process the message
            response = await self.process_message(message)

            # Send response if needed
            if response and self.message_bus:
                await self.message_bus.send_message(response)

            # Update metrics
            execution_time = time.time() - start_time
            self._update_performance_metrics(execution_time, success=True)

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"❌ Error handling message {message.id}: {e}")
            self._update_performance_metrics(execution_time, success=False)

        finally:
            self.is_busy = False

    def _update_performance_metrics(self, execution_time: float, success: bool):
        """Update performance metrics"""
        self.performance_metrics['messages_processed'] += 1
        self.performance_metrics['total_execution_time'] += execution_time

        if not success:
            self.performance_metrics['error_count'] += 1

        # Calculate averages
        total_messages = self.performance_metrics['messages_processed']
        self.performance_metrics['average_response_time'] = (
            self.performance_metrics['total_execution_time'] / total_messages
        )

        error_count = self.performance_metrics['error_count']
        self.performance_metrics['success_rate'] = (
            (total_messages - error_count) / total_messages
        )

    async def _heartbeat_loop(self):
        """Send periodic heartbeat"""
        while self.is_active:
            try:
                self.last_heartbeat = time.time()

                if self.message_bus:
                    heartbeat_msg = AgentMessage(
                        id=f"heartbeat_{uuid.uuid4().hex[:8]}",
                        sender_id=self.agent_id,
                        recipient_id="master_coordinator",
                        message_type=MessageType.HEARTBEAT,
                        priority=Priority.LOW,
                        content={'timestamp': self.last_heartbeat},
                        timestamp=self.last_heartbeat
                    )
                    await self.message_bus.send_message(heartbeat_msg)

                await asyncio.sleep(5.0)  # Heartbeat every 5 seconds

            except Exception as e:
                self.logger.error(f"❌ Heartbeat error: {e}")
                await asyncio.sleep(1.0)

    async def send_message(self, recipient_id: str, message_type: MessageType,
                          content: Dict[str, Any], priority: Priority = Priority.MEDIUM,
                          requires_response: bool = False) -> Optional[AgentMessage]:
        """Send message to another agent"""
        if not self.message_bus:
            self.logger.error("❌ Message bus not available")
            return None

        message = AgentMessage(
            id=f"msg_{uuid.uuid4().hex[:8]}",
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            message_type=message_type,
            priority=priority,
            content=content,
            timestamp=time.time(),
            requires_response=requires_response
        )

        return await self.message_bus.send_message(message)

    def register_capability(self, capability: AgentCapability):
        """Register a capability"""
        self.capabilities.append(capability)
        self.logger.info(f"📋 Registered capability: {capability.name}")

    def get_status(self) -> AgentStatus:
        """Get current agent status"""
        return AgentStatus(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            is_active=self.is_active,
            is_busy=self.is_busy,
            last_heartbeat=self.last_heartbeat,
            performance_metrics=self.performance_metrics.copy(),
            current_task=self._get_current_task(),
            error_count=self.performance_metrics['error_count'],
            uptime_seconds=time.time() - self.start_time
        )

    def _get_current_task(self) -> Optional[str]:
        """Get description of current task (override in subclasses)"""
        return "idle" if not self.is_busy else "processing"

    def enable_human_override(self, enabled: bool = True):
        """Enable/disable human override mode"""
        self.override_active = enabled
        status = "ENABLED" if enabled else "DISABLED"
        self.logger.info(f"🔒 Human override {status}")

    def emergency_stop(self):
        """Emergency stop - highest priority"""
        self.logger.warning("🚨 EMERGENCY STOP activated")
        self.override_active = True
        # Clear message queue
        while not self.message_queue.empty():
            try:
                self.message_queue.get_nowait()
            except:
                break

    def get_capabilities_summary(self) -> Dict[str, Any]:
        """Get summary of agent capabilities"""
        return {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type.value,
            'capabilities': [asdict(cap) for cap in self.capabilities],
            'dependencies': self.dependencies,
            'total_capabilities': len(self.capabilities)
        }

class MessageBus:
    """
    Central message bus for inter-agent communication

    Handles:
    - Message routing and delivery
    - Priority-based queuing
    - Broadcast and subscription patterns
    - Message persistence and replay
    """

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.message_history: List[AgentMessage] = []
        self.subscriptions: Dict[str, List[str]] = {}  # topic -> agent_ids
        self.logger = logging.getLogger("MessageBus")

        # Performance tracking
        self.stats = {
            'total_messages': 0,
            'messages_per_second': 0.0,
            'average_delivery_time': 0.0,
            'failed_deliveries': 0
        }

    def register_agent(self, agent: BaseAgent):
        """Register an agent with the message bus"""
        self.agents[agent.agent_id] = agent
        agent.message_bus = self
        self.logger.info(f"📡 Registered agent: {agent.agent_id}")

    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.logger.info(f"📡 Unregistered agent: {agent_id}")

    async def send_message(self, message: AgentMessage) -> bool:
        """Send message to target agent"""
        start_time = time.time()

        try:
            # Check if recipient exists
            if message.recipient_id not in self.agents:
                self.logger.error(f"❌ Recipient not found: {message.recipient_id}")
                self.stats['failed_deliveries'] += 1
                return False

            # Get target agent
            target_agent = self.agents[message.recipient_id]

            # Add to message history
            self.message_history.append(message)

            # Deliver message
            await target_agent.message_queue.put(message)

            # Update stats
            delivery_time = time.time() - start_time
            self.stats['total_messages'] += 1
            self._update_delivery_stats(delivery_time)

            self.logger.debug(f"📤 Message delivered: {message.id} -> {message.recipient_id}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Message delivery failed: {e}")
            self.stats['failed_deliveries'] += 1
            return False

    async def broadcast_message(self, message: AgentMessage, agent_types: Optional[List[AgentType]] = None):
        """Broadcast message to multiple agents"""
        target_agents = self.agents.values()

        if agent_types:
            target_agents = [a for a in target_agents if a.agent_type in agent_types]

        for agent in target_agents:
            if agent.agent_id != message.sender_id:  # Don't send to sender
                message.recipient_id = agent.agent_id
                await self.send_message(message)

    def _update_delivery_stats(self, delivery_time: float):
        """Update delivery statistics"""
        total = self.stats['total_messages']
        current_avg = self.stats['average_delivery_time']
        self.stats['average_delivery_time'] = (current_avg * (total - 1) + delivery_time) / total

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            'registered_agents': len(self.agents),
            'active_agents': sum(1 for a in self.agents.values() if a.is_active),
            'message_stats': self.stats,
            'agents': {
                agent_id: agent.get_status()
                for agent_id, agent in self.agents.items()
            }
        }

# Utility functions for agent system
def create_agent_message(sender_id: str, recipient_id: str, content: Dict[str, Any],
                        message_type: MessageType = MessageType.REQUEST,
                        priority: Priority = Priority.MEDIUM) -> AgentMessage:
    """Utility to create agent messages"""
    return AgentMessage(
        id=f"msg_{uuid.uuid4().hex[:8]}",
        sender_id=sender_id,
        recipient_id=recipient_id,
        message_type=message_type,
        priority=priority,
        content=content,
        timestamp=time.time()
    )

def serialize_message(message: AgentMessage) -> str:
    """Serialize message to JSON"""
    return json.dumps(asdict(message), default=str)

def deserialize_message(data: str) -> AgentMessage:
    """Deserialize message from JSON"""
    return AgentMessage(**json.loads(data))