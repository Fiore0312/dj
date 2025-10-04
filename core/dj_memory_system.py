#!/usr/bin/env python3
"""
🧠 DJ Memory System
Advanced memory management for autonomous DJ learning and pattern recognition
Integrates with Memory Agent MCP for persistent learning capabilities
"""

import json
import time
import sqlite3
import hashlib
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import threading

# Core components
from config import DJConfig, get_config
from autonomous_decision_engine import DJDecision, DecisionType
from music_library import TrackInfo

logger = logging.getLogger(__name__)

class MemoryType(Enum):
    """Types of DJ memories"""
    SUCCESSFUL_TRANSITION = "successful_transition"
    FAILED_TRANSITION = "failed_transition"
    CROWD_RESPONSE = "crowd_response"
    VENUE_PREFERENCE = "venue_preference"
    HARMONIC_PATTERN = "harmonic_pattern"
    ENERGY_CURVE = "energy_curve"
    MIXING_TECHNIQUE = "mixing_technique"

@dataclass
class DJMemory:
    """A specific DJ memory/learning experience"""
    memory_id: str
    memory_type: MemoryType
    timestamp: float

    # Context information
    venue_type: str
    event_type: str
    session_time: float  # Minutes into session

    # Musical context
    source_track: Optional[Dict] = None
    target_track: Optional[Dict] = None
    bpm_diff: Optional[float] = None
    key_compatibility: Optional[float] = None

    # Action taken
    decision_data: Dict = None
    technique_used: Optional[str] = None

    # Outcome
    success_score: float = 0.5  # 0-1
    crowd_response: Optional[float] = None
    technical_quality: Optional[float] = None

    # Learning data
    pattern_data: Dict = None
    confidence: float = 0.5

    # Usage tracking
    times_referenced: int = 0
    last_accessed: float = 0.0

@dataclass
class PatternRule:
    """A learned pattern/rule for DJ decisions"""
    rule_id: str
    pattern_type: str
    conditions: Dict  # When this rule applies
    action: Dict      # What action to take
    confidence: float # How confident we are in this rule
    success_rate: float # Historical success rate
    sample_size: int  # Number of times tested

class DJMemorySystem:
    """Advanced memory system for DJ learning and pattern recognition"""

    def __init__(self, config: DJConfig = None):
        self.config = config or get_config()

        # Database setup
        self.db_path = Path.home() / '.config' / 'dj_ai' / 'dj_memory.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Memory storage
        self.active_memories: List[DJMemory] = []
        self.learned_patterns: List[PatternRule] = []

        # Learning parameters
        self.min_confidence_threshold = 0.6
        self.pattern_recognition_window = 100  # Look at last N memories
        self.memory_retention_days = 365

        # Threading for background processing
        self.learning_queue = []
        self.learning_thread = None
        self.is_learning = False

        self._init_database()
        self._load_existing_memories()
        print("🧠 DJ Memory System initialized")

    def _init_database(self):
        """Initialize memory database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Memories table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS memories (
                        memory_id TEXT PRIMARY KEY,
                        memory_type TEXT,
                        timestamp REAL,
                        venue_type TEXT,
                        event_type TEXT,
                        session_time REAL,
                        source_track TEXT,
                        target_track TEXT,
                        bpm_diff REAL,
                        key_compatibility REAL,
                        decision_data TEXT,
                        technique_used TEXT,
                        success_score REAL,
                        crowd_response REAL,
                        technical_quality REAL,
                        pattern_data TEXT,
                        confidence REAL,
                        times_referenced INTEGER DEFAULT 0,
                        last_accessed REAL,
                        created_at REAL
                    )
                ''')

                # Patterns table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS learned_patterns (
                        rule_id TEXT PRIMARY KEY,
                        pattern_type TEXT,
                        conditions TEXT,
                        action TEXT,
                        confidence REAL,
                        success_rate REAL,
                        sample_size INTEGER,
                        created_at REAL,
                        updated_at REAL
                    )
                ''')

                # Performance tracking
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS session_performance (
                        session_id TEXT PRIMARY KEY,
                        venue_type TEXT,
                        event_type TEXT,
                        duration_minutes REAL,
                        total_transitions INTEGER,
                        successful_transitions INTEGER,
                        avg_crowd_response REAL,
                        techniques_used TEXT,
                        timestamp REAL
                    )
                ''')

                # Indexes for performance
                conn.execute('CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_venue_type ON memories(venue_type)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_success_score ON memories(success_score)')

                conn.commit()

        except Exception as e:
            logger.error(f"Error initializing memory database: {e}")

    def _load_existing_memories(self):
        """Load existing memories from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Load recent memories (last 30 days)
                cutoff_time = time.time() - (30 * 24 * 3600)
                cursor = conn.execute('''
                    SELECT * FROM memories
                    WHERE timestamp > ?
                    ORDER BY timestamp DESC
                    LIMIT 1000
                ''', (cutoff_time,))

                for row in cursor:
                    memory = self._row_to_memory(row)
                    if memory:
                        self.active_memories.append(memory)

                # Load learned patterns
                cursor = conn.execute('SELECT * FROM learned_patterns')
                for row in cursor:
                    pattern = self._row_to_pattern(row)
                    if pattern:
                        self.learned_patterns.append(pattern)

                print(f"📚 Loaded {len(self.active_memories)} memories and {len(self.learned_patterns)} patterns")

        except Exception as e:
            logger.error(f"Error loading memories: {e}")

    def store_memory(self, memory_type: MemoryType, context: Dict,
                    decision: DJDecision = None, outcome: Dict = None):
        """Store a new memory from DJ experience"""
        try:
            # Create unique memory ID
            memory_id = hashlib.md5(
                f"{time.time()}_{memory_type.value}_{context}".encode()
            ).hexdigest()[:16]

            # Extract context information
            venue_type = context.get('venue_type', 'unknown')
            event_type = context.get('event_type', 'unknown')
            session_time = context.get('session_time', 0.0)

            # Create memory object
            memory = DJMemory(
                memory_id=memory_id,
                memory_type=memory_type,
                timestamp=time.time(),
                venue_type=venue_type,
                event_type=event_type,
                session_time=session_time,
                decision_data=asdict(decision) if decision else {},
                success_score=outcome.get('success_score', 0.5) if outcome else 0.5,
                crowd_response=outcome.get('crowd_response') if outcome else None,
                technical_quality=outcome.get('technical_quality') if outcome else None,
                confidence=0.5
            )

            # Add musical context if available
            if 'source_track' in context:
                memory.source_track = context['source_track']
            if 'target_track' in context:
                memory.target_track = context['target_track']
            if 'bpm_diff' in context:
                memory.bpm_diff = context['bpm_diff']
            if 'key_compatibility' in context:
                memory.key_compatibility = context['key_compatibility']

            # Store in active memory
            self.active_memories.append(memory)

            # Save to database
            self._save_memory_to_db(memory)

            # Queue for pattern learning
            self.learning_queue.append(memory)

            print(f"💾 Stored {memory_type.value} memory: {memory_id}")

            return memory_id

        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            return None

    def query_similar_situations(self, context: Dict, limit: int = 10) -> List[DJMemory]:
        """Find memories from similar situations"""
        try:
            similar_memories = []

            # Calculate similarity scores
            for memory in self.active_memories:
                similarity = self._calculate_context_similarity(context, memory)
                if similarity > 0.5:  # Threshold for relevance
                    memory.last_accessed = time.time()
                    memory.times_referenced += 1
                    similar_memories.append((similarity, memory))

            # Sort by similarity and return top matches
            similar_memories.sort(key=lambda x: x[0], reverse=True)
            return [memory for _, memory in similar_memories[:limit]]

        except Exception as e:
            logger.error(f"Error querying similar situations: {e}")
            return []

    def get_recommendation(self, context: Dict) -> Optional[Dict]:
        """Get AI recommendation based on learned patterns"""
        try:
            # Find similar successful experiences
            similar_memories = self.query_similar_situations(context, limit=5)
            successful_memories = [
                m for m in similar_memories
                if m.success_score > 0.7 and m.memory_type == MemoryType.SUCCESSFUL_TRANSITION
            ]

            if not successful_memories:
                return None

            # Analyze successful patterns
            recommendations = {}
            confidence_scores = []

            for memory in successful_memories:
                if memory.decision_data:
                    # Extract technique used
                    technique = memory.technique_used or memory.decision_data.get('technique', 'fade')

                    if technique not in recommendations:
                        recommendations[technique] = {
                            'technique': technique,
                            'success_rate': 0.0,
                            'confidence': 0.0,
                            'sample_size': 0,
                            'avg_crowd_response': 0.0
                        }

                    # Aggregate data
                    rec = recommendations[technique]
                    rec['sample_size'] += 1
                    rec['success_rate'] = (rec['success_rate'] * (rec['sample_size'] - 1) + memory.success_score) / rec['sample_size']
                    rec['confidence'] = (rec['confidence'] * (rec['sample_size'] - 1) + memory.confidence) / rec['sample_size']

                    if memory.crowd_response:
                        rec['avg_crowd_response'] = (rec['avg_crowd_response'] * (rec['sample_size'] - 1) + memory.crowd_response) / rec['sample_size']

            # Return best recommendation
            if recommendations:
                best_technique = max(recommendations.values(), key=lambda x: x['success_rate'] * x['confidence'])
                return best_technique

            return None

        except Exception as e:
            logger.error(f"Error getting recommendation: {e}")
            return None

    def learn_patterns(self):
        """Analyze memories to learn new patterns"""
        try:
            if len(self.active_memories) < 10:
                return  # Need minimum data for pattern recognition

            # Group memories by context similarity
            pattern_groups = self._group_memories_by_pattern()

            # Analyze each group for patterns
            for pattern_type, memories in pattern_groups.items():
                if len(memories) >= 5:  # Minimum sample size
                    pattern_rule = self._extract_pattern_rule(pattern_type, memories)
                    if pattern_rule and pattern_rule.confidence > self.min_confidence_threshold:
                        self._store_learned_pattern(pattern_rule)

            print(f"📈 Pattern learning complete. Total patterns: {len(self.learned_patterns)}")

        except Exception as e:
            logger.error(f"Error learning patterns: {e}")

    def _calculate_context_similarity(self, context: Dict, memory: DJMemory) -> float:
        """Calculate similarity between current context and stored memory"""
        try:
            similarity_score = 0.0
            factors = 0

            # Venue type similarity
            if context.get('venue_type') == memory.venue_type:
                similarity_score += 0.3
            factors += 1

            # Event type similarity
            if context.get('event_type') == memory.event_type:
                similarity_score += 0.2
            factors += 1

            # BPM similarity
            if context.get('current_bpm') and memory.source_track:
                source_bpm = memory.source_track.get('bpm', 120)
                bpm_diff = abs(context['current_bpm'] - source_bpm)
                if bpm_diff < 10:
                    similarity_score += 0.2 * (1 - bpm_diff / 10)
                factors += 1

            # Key compatibility
            if context.get('current_key') and memory.key_compatibility:
                similarity_score += 0.1 * memory.key_compatibility
                factors += 1

            # Energy level similarity
            if context.get('energy_level') and memory.source_track:
                source_energy = memory.source_track.get('energy', 5)
                energy_diff = abs(context['energy_level'] - source_energy)
                if energy_diff < 3:
                    similarity_score += 0.2 * (1 - energy_diff / 3)
                factors += 1

            return similarity_score / max(1, factors) if factors > 0 else 0.0

        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    def _group_memories_by_pattern(self) -> Dict[str, List[DJMemory]]:
        """Group memories by similar patterns"""
        groups = {
            'venue_based': [],
            'energy_transitions': [],
            'harmonic_progressions': [],
            'timing_patterns': []
        }

        try:
            for memory in self.active_memories:
                # Group by venue type
                groups['venue_based'].append(memory)

                # Group energy transitions
                if memory.source_track and memory.target_track:
                    source_energy = memory.source_track.get('energy', 5)
                    target_energy = memory.target_track.get('energy', 5)
                    if abs(source_energy - target_energy) > 1:
                        groups['energy_transitions'].append(memory)

                # Group harmonic progressions
                if memory.key_compatibility and memory.key_compatibility > 0.7:
                    groups['harmonic_progressions'].append(memory)

                # Group timing patterns
                if memory.session_time:
                    groups['timing_patterns'].append(memory)

            return groups

        except Exception as e:
            logger.error(f"Error grouping memories: {e}")
            return groups

    def _extract_pattern_rule(self, pattern_type: str, memories: List[DJMemory]) -> Optional[PatternRule]:
        """Extract a pattern rule from grouped memories"""
        try:
            successful_memories = [m for m in memories if m.success_score > 0.7]

            if len(successful_memories) < 3:
                return None

            # Calculate success rate
            success_rate = len(successful_memories) / len(memories)

            if success_rate < 0.6:
                return None

            # Extract common conditions
            conditions = {}
            actions = {}

            for memory in successful_memories:
                # Extract conditions
                if memory.venue_type not in conditions:
                    conditions[memory.venue_type] = 0
                conditions[memory.venue_type] += 1

                # Extract actions
                technique = memory.technique_used or 'fade'
                if technique not in actions:
                    actions[technique] = 0
                actions[technique] += 1

            # Find most common patterns
            most_common_venue = max(conditions.items(), key=lambda x: x[1])[0]
            most_common_action = max(actions.items(), key=lambda x: x[1])[0]

            # Create rule
            rule_id = hashlib.md5(f"{pattern_type}_{most_common_venue}_{most_common_action}".encode()).hexdigest()[:16]

            rule = PatternRule(
                rule_id=rule_id,
                pattern_type=pattern_type,
                conditions={'venue_type': most_common_venue},
                action={'technique': most_common_action},
                confidence=success_rate,
                success_rate=success_rate,
                sample_size=len(memories)
            )

            return rule

        except Exception as e:
            logger.error(f"Error extracting pattern rule: {e}")
            return None

    def _store_learned_pattern(self, pattern: PatternRule):
        """Store a learned pattern"""
        try:
            # Check if pattern already exists
            existing = next((p for p in self.learned_patterns if p.rule_id == pattern.rule_id), None)

            if existing:
                # Update existing pattern
                existing.confidence = (existing.confidence + pattern.confidence) / 2
                existing.success_rate = pattern.success_rate
                existing.sample_size = pattern.sample_size
            else:
                # Add new pattern
                self.learned_patterns.append(pattern)

            # Save to database
            self._save_pattern_to_db(pattern)

            print(f"📚 Learned pattern: {pattern.pattern_type} (confidence: {pattern.confidence:.2f})")

        except Exception as e:
            logger.error(f"Error storing learned pattern: {e}")

    def _save_memory_to_db(self, memory: DJMemory):
        """Save memory to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO memories (
                        memory_id, memory_type, timestamp, venue_type, event_type,
                        session_time, source_track, target_track, bpm_diff,
                        key_compatibility, decision_data, technique_used,
                        success_score, crowd_response, technical_quality,
                        pattern_data, confidence, times_referenced,
                        last_accessed, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    memory.memory_id, memory.memory_type.value, memory.timestamp,
                    memory.venue_type, memory.event_type, memory.session_time,
                    json.dumps(memory.source_track) if memory.source_track else None,
                    json.dumps(memory.target_track) if memory.target_track else None,
                    memory.bpm_diff, memory.key_compatibility,
                    json.dumps(memory.decision_data) if memory.decision_data else None,
                    memory.technique_used, memory.success_score,
                    memory.crowd_response, memory.technical_quality,
                    json.dumps(memory.pattern_data) if memory.pattern_data else None,
                    memory.confidence, memory.times_referenced,
                    memory.last_accessed, time.time()
                ))
                conn.commit()

        except Exception as e:
            logger.error(f"Error saving memory to database: {e}")

    def _save_pattern_to_db(self, pattern: PatternRule):
        """Save learned pattern to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO learned_patterns (
                        rule_id, pattern_type, conditions, action,
                        confidence, success_rate, sample_size,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pattern.rule_id, pattern.pattern_type,
                    json.dumps(pattern.conditions), json.dumps(pattern.action),
                    pattern.confidence, pattern.success_rate, pattern.sample_size,
                    time.time(), time.time()
                ))
                conn.commit()

        except Exception as e:
            logger.error(f"Error saving pattern to database: {e}")

    def _row_to_memory(self, row) -> Optional[DJMemory]:
        """Convert database row to DJMemory object"""
        try:
            return DJMemory(
                memory_id=row['memory_id'],
                memory_type=MemoryType(row['memory_type']),
                timestamp=row['timestamp'],
                venue_type=row['venue_type'],
                event_type=row['event_type'],
                session_time=row['session_time'],
                source_track=json.loads(row['source_track']) if row['source_track'] else None,
                target_track=json.loads(row['target_track']) if row['target_track'] else None,
                bpm_diff=row['bpm_diff'],
                key_compatibility=row['key_compatibility'],
                decision_data=json.loads(row['decision_data']) if row['decision_data'] else {},
                technique_used=row['technique_used'],
                success_score=row['success_score'],
                crowd_response=row['crowd_response'],
                technical_quality=row['technical_quality'],
                pattern_data=json.loads(row['pattern_data']) if row['pattern_data'] else None,
                confidence=row['confidence'],
                times_referenced=row['times_referenced'],
                last_accessed=row['last_accessed']
            )
        except Exception as e:
            logger.error(f"Error converting row to memory: {e}")
            return None

    def _row_to_pattern(self, row) -> Optional[PatternRule]:
        """Convert database row to PatternRule object"""
        try:
            return PatternRule(
                rule_id=row['rule_id'],
                pattern_type=row['pattern_type'],
                conditions=json.loads(row['conditions']),
                action=json.loads(row['action']),
                confidence=row['confidence'],
                success_rate=row['success_rate'],
                sample_size=row['sample_size']
            )
        except Exception as e:
            logger.error(f"Error converting row to pattern: {e}")
            return None

    def get_memory_stats(self) -> Dict:
        """Get memory system statistics"""
        return {
            'total_memories': len(self.active_memories),
            'learned_patterns': len(self.learned_patterns),
            'avg_success_rate': sum(m.success_score for m in self.active_memories) / len(self.active_memories) if self.active_memories else 0,
            'memory_types': {mt.value: sum(1 for m in self.active_memories if m.memory_type == mt) for mt in MemoryType},
            'venues_learned': len(set(m.venue_type for m in self.active_memories)),
            'queue_size': len(self.learning_queue)
        }

def test_memory_system():
    """Test the DJ memory system"""
    print("🧪 Testing DJ Memory System")
    print("=" * 50)

    # Initialize memory system
    config = get_config()
    memory_system = DJMemorySystem(config)

    # Test storing memories
    print("\n💾 Testing memory storage...")

    # Simulate successful transition
    context = {
        'venue_type': 'club',
        'event_type': 'prime_time',
        'session_time': 45.0,
        'current_bpm': 128.0,
        'current_key': 'A minor',
        'energy_level': 7,
        'source_track': {'title': 'Track A', 'bpm': 128, 'energy': 7},
        'target_track': {'title': 'Track B', 'bpm': 130, 'energy': 8},
        'bpm_diff': 2.0,
        'key_compatibility': 0.9
    }

    outcome = {
        'success_score': 0.85,
        'crowd_response': 0.9,
        'technical_quality': 0.8
    }

    memory_id = memory_system.store_memory(
        MemoryType.SUCCESSFUL_TRANSITION,
        context,
        outcome=outcome
    )

    print(f"✅ Stored memory: {memory_id}")

    # Test querying similar situations
    print("\n🔍 Testing similarity search...")
    similar_context = {
        'venue_type': 'club',
        'event_type': 'prime_time',
        'current_bpm': 127.0,
        'energy_level': 7
    }

    similar_memories = memory_system.query_similar_situations(similar_context, limit=3)
    print(f"Found {len(similar_memories)} similar memories")

    # Test getting recommendations
    print("\n💡 Testing recommendations...")
    recommendation = memory_system.get_recommendation(similar_context)
    if recommendation:
        print(f"Recommendation: {recommendation}")
    else:
        print("No recommendations available yet")

    # Test pattern learning
    print("\n📚 Testing pattern learning...")
    memory_system.learn_patterns()

    # Get stats
    stats = memory_system.get_memory_stats()
    print(f"\n📊 Memory System Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n✅ Memory system test complete!")

if __name__ == "__main__":
    test_memory_system()