#!/usr/bin/env python3
"""
🤖 Autonomous AI DJ Agent
Complete autonomous DJ system orchestrating all components
Executes mixing decisions without human intervention
"""

import asyncio
import time
import logging
import threading
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, asdict
import json
from enum import Enum

# Core configuration
from config import DJConfig, VENUE_TYPES, EVENT_TYPES, get_config

# Dependency manager for autonomous components
from core.dependency_manager import get_dependency_manager, is_autonomous_available

# Legacy components (enhanced)
from music_library import MusicLibraryScanner, TrackInfo, get_music_scanner
from traktor_control import TraktorController, DeckID

# AI integration
try:
    from core.openrouter_client import OpenRouterClient, DJContext, AIResponse
    OPENROUTER_AVAILABLE = True
except ImportError:
    OPENROUTER_AVAILABLE = False

logger = logging.getLogger(__name__)

class AutonomousMode(Enum):
    """Autonomous operation modes"""
    MANUAL = "manual"          # Human control
    ASSISTED = "assisted"      # AI suggestions + human execution
    AUTONOMOUS = "autonomous"  # Full AI control

class SessionPhase(Enum):
    """DJ session phases"""
    STARTUP = "startup"
    WARM_UP = "warm_up"
    BUILDING = "building"
    PEAK_TIME = "peak_time"
    WIND_DOWN = "wind_down"
    CLOSING = "closing"

@dataclass
class AutonomousSession:
    """Complete autonomous DJ session"""
    session_id: str
    venue_type: str
    event_type: str
    target_duration: int  # minutes

    # Session state
    start_time: float
    current_phase: SessionPhase = SessionPhase.STARTUP
    autonomous_mode: AutonomousMode = AutonomousMode.AUTONOMOUS

    # Track management
    current_track: Optional[TrackInfo] = None
    next_track: Optional[TrackInfo] = None
    queue: List[TrackInfo] = None
    played_tracks: List[str] = None

    # Performance metrics
    energy_curve: List[float] = None
    crowd_response: List[float] = None
    transition_quality: List[float] = None

    # Timing
    last_transition: Optional[float] = None
    next_transition_planned: Optional[float] = None

    def __post_init__(self):
        if self.queue is None:
            self.queue = []
        if self.played_tracks is None:
            self.played_tracks = []
        if self.energy_curve is None:
            self.energy_curve = []
        if self.crowd_response is None:
            self.crowd_response = []
        if self.transition_quality is None:
            self.transition_quality = []

@dataclass
class MixSession:
    """Sessione di mixing DJ"""
    venue_type: str
    event_type: str
    target_duration: int = 60  # minuti
    session_start: float = 0.0
    tracks_played: List[str] = None
    energy_progression: List[float] = None

    def __post_init__(self):
        if self.tracks_played is None:
            self.tracks_played = []
        if self.energy_progression is None:
            self.energy_progression = []
        if self.session_start == 0.0:
            self.session_start = time.time()

    def get_session_stats(self) -> Dict[str, Any]:
        """Statistiche sessione"""
        session_time = (time.time() - self.session_start) / 60 if self.session_start else 0

        return {
            'duration_minutes': round(session_time, 1),
            'tracks_played': len(self.tracks_played),
            'avg_energy': sum(self.energy_progression) / len(self.energy_progression) if self.energy_progression else 0,
            'venue_type': self.venue_type,
            'event_type': self.event_type,
        }

class SimpleDJAgent:
    """Agente DJ AI semplificato"""

    def __init__(self, ai_client: OpenRouterClient, traktor_controller: TraktorController,
                 music_scanner: MusicLibraryScanner):
        """Inizializza agente DJ"""
        self.ai_client = ai_client
        self.traktor = traktor_controller
        self.music = music_scanner

        # Stato sessione
        self.current_session: Optional[MixSession] = None
        self.dj_context = DJContext()
        self.active = False

        # Configurazione mixing
        self.config = {
            'transition_time': 30,  # secondi
            'energy_change_threshold': 2,  # livelli
            'bpm_tolerance': 0.1,  # 10%
            'min_track_play_time': 60,  # secondi minimo
            'auto_sync_enabled': True,
            'auto_effects_enabled': True
        }

        # Cache tracks
        self.available_tracks: List[TrackInfo] = []
        self.track_history: List[str] = []

        logger.info("🤖 AI DJ Agent inizializzato")

    async def start_session(self, venue_type: str, event_type: str, duration: int = 120) -> bool:
        """Avvia sessione DJ"""
        try:
            logger.info(f"🎵 Avvio sessione DJ: {venue_type} - {event_type} ({duration}min)")

            # Crea sessione
            self.current_session = MixSession(
                venue_type=venue_type,
                event_type=event_type,
                target_duration=duration,
                session_start=time.time()
            )

            # Aggiorna contesto
            self.dj_context.venue_type = venue_type
            self.dj_context.event_type = event_type

            # Carica tracks disponibili
            await self._load_available_tracks()

            # Strategia iniziale
            await self._plan_session_strategy()

            self.active = True
            logger.info("✅ Sessione DJ avviata")

            return True

        except Exception as e:
            logger.error(f"❌ Errore avvio sessione: {e}")
            return False

    async def _load_available_tracks(self):
        """Carica tracks disponibili per la sessione"""
        try:
            # Ottieni venue info
            venue_info = VENUE_TYPES.get(self.current_session.venue_type, {})
            preferred_genres = venue_info.get('typical_genres', [])
            bpm_range = venue_info.get('bpm_range', (120, 140))

            # Cerca tracks compatibili
            all_tracks = []
            for genre in preferred_genres:
                tracks = self.music.search_tracks(
                    genre=genre,
                    bpm_range=bpm_range,
                    limit=50
                )
                all_tracks.extend(tracks)

            # Rimuovi duplicati e tracks senza BPM
            seen = set()
            self.available_tracks = []

            for track in all_tracks:
                if track.filepath not in seen and track.bpm:
                    seen.add(track.filepath)
                    self.available_tracks.append(track)

            logger.info(f"📁 Caricati {len(self.available_tracks)} tracks per la sessione")

            # Se pochi tracks, aggiungi tracks generici
            if len(self.available_tracks) < 20:
                generic_tracks = self.music.search_tracks(limit=100)
                for track in generic_tracks:
                    if track.filepath not in seen and track.bpm:
                        self.available_tracks.append(track)

            logger.info(f"📁 Totale tracks disponibili: {len(self.available_tracks)}")

        except Exception as e:
            logger.error(f"❌ Errore caricamento tracks: {e}")

    async def _plan_session_strategy(self):
        """Pianifica strategia sessione con AI"""
        try:
            venue_info = VENUE_TYPES.get(self.current_session.venue_type, {})
            event_info = EVENT_TYPES.get(self.current_session.event_type, "Evento standard")

            query = f"""
Pianifica una strategia DJ per:
- Venue: {self.current_session.venue_type} ({venue_info.get('description', '')})
- Evento: {self.current_session.event_type} ({event_info})
- Durata: {self.current_session.target_duration} minuti
- Generi disponibili: {list(set(t.genre for t in self.available_tracks[:20]))}
- BPM range: {min(t.bpm for t in self.available_tracks if t.bpm):.0f}-{max(t.bpm for t in self.available_tracks if t.bpm):.0f}

Suggerisci:
1. Progressione energia (1-10) nel tempo
2. Struttura del set (apertura, sviluppo, climax, chiusura)
3. Strategie di mixing specifiche
"""

            response = await self.ai_client.get_dj_decision(self.dj_context, query)

            if response.success:
                logger.info(f"🧠 Strategia AI: {response.response[:200]}...")
                # Qui puoi parsare la risposta per impostare parametri automatici
            else:
                logger.warning("⚠️ Pianificazione AI fallita, uso strategia default")

        except Exception as e:
            logger.error(f"❌ Errore pianificazione: {e}")

    async def suggest_next_track(self, current_context: DJContext) -> Optional[TrackInfo]:
        """Suggerisci prossimo track basato su AI e compatibilità"""
        try:
            if not self.available_tracks:
                return None

            # Ottieni tracks compatibili con BPM corrente
            if current_context.current_bpm > 0:
                compatible_tracks = self.music.get_compatible_tracks(
                    current_context.current_bpm,
                    current_context.current_genre,
                    limit=10
                )
            else:
                # Primo track della sessione
                compatible_tracks = self.available_tracks[:20]

            # Rimuovi tracks già suonati
            available_compatible = [
                t for t in compatible_tracks
                if t.filepath not in self.track_history
            ]

            if not available_compatible:
                available_compatible = compatible_tracks[:5]  # Fallback

            # Chiedi consiglio all'AI
            track_summaries = []
            for track in available_compatible[:5]:
                summary = f"'{track.title}' - {track.artist} ({track.genre}, {track.bpm} BPM)"
                track_summaries.append(summary)

            query = f"""
Suggerisci il miglior prossimo track per il mixing:

CONTESTO ATTUALE:
- BPM corrente: {current_context.current_bpm}
- Genere corrente: {current_context.current_genre}
- Energia target: {current_context.energy_level}/10
- Tempo nel set: {current_context.time_in_set} min
- Venue: {current_context.venue_type}
- Tipo evento: {current_context.event_type}

TRACKS DISPONIBILI:
{chr(10).join(f"{i+1}. {summary}" for i, summary in enumerate(track_summaries))}

Scegli il numero del track migliore (1-{len(track_summaries)}) e spiega il motivo della scelta considerando:
- Progressione energetica
- Compatibilità BPM
- Flow del set
- Momento della serata
"""

            response = await self.ai_client.get_dj_decision(current_context, query)

            if response.success:
                # Estrai numero del track dalla risposta
                choice = self._extract_track_choice(response.response, len(track_summaries))
                if choice is not None:
                    selected_track = available_compatible[choice]
                    logger.info(f"🎵 AI suggerisce: {selected_track.title} - {selected_track.artist}")
                    return selected_track

            # Fallback: selezione intelligente automatica
            return self._smart_track_selection(available_compatible, current_context)

        except Exception as e:
            logger.error(f"❌ Errore suggerimento track: {e}")
            return None

    def _extract_track_choice(self, ai_response: str, max_choice: int) -> Optional[int]:
        """Estrai scelta track dalla risposta AI"""
        try:
            # Cerca numeri nella risposta
            import re
            numbers = re.findall(r'\b([1-9])\b', ai_response)

            for num_str in numbers:
                num = int(num_str)
                if 1 <= num <= max_choice:
                    return num - 1  # Convert to 0-based index

            return None

        except:
            return None

    def _smart_track_selection(self, tracks: List[TrackInfo], context: DJContext) -> Optional[TrackInfo]:
        """Selezione intelligente automatica"""
        if not tracks:
            return None

        # Score tracks based on compatibility
        scored_tracks = []

        for track in tracks:
            score = 0

            # BPM compatibility
            if track.bpm and context.current_bpm:
                bpm_compat = track.calculate_compatibility(context.current_bpm)
                score += bpm_compat * 40

            # Energy compatibility
            if track.energy and context.energy_level:
                energy_diff = abs(track.energy - context.energy_level)
                score += max(0, 20 - energy_diff * 3)

            # Genre continuity
            if track.genre and context.current_genre:
                if track.genre.lower() == context.current_genre.lower():
                    score += 20

            # Novelty (prefer unplayed tracks)
            if track.filepath not in self.track_history:
                score += 15

            # Random factor for creativity
            score += random.randint(0, 10)

            scored_tracks.append((score, track))

        # Sort by score and return best
        scored_tracks.sort(reverse=True)
        return scored_tracks[0][1] if scored_tracks else None

    async def perform_transition(self, from_deck: DeckID, to_deck: DeckID,
                                next_track: TrackInfo) -> bool:
        """Esegui transizione AI tra tracks"""
        try:
            logger.info(f"🔄 Transizione AI: {from_deck.value} → {to_deck.value}")

            # Chiedi strategia di transizione all'AI
            query = f"""
Pianifica transizione DJ da Deck {from_deck.value} a Deck {to_deck.value}:

TRACK CORRENTE (Deck {from_deck.value}):
- {self.dj_context.last_track or "Unknown"}
- BPM: {self.dj_context.current_bpm}

NUOVO TRACK (Deck {to_deck.value}):
- {next_track.title} - {next_track.artist}
- BPM: {next_track.bpm}
- Genere: {next_track.genre}

Suggerisci:
1. Tipo di transizione (cut, blend, effect)
2. Durata transizione (15-60 secondi)
3. Uso di EQ/filtri
4. Effetti da applicare
5. Posizione crossfader finale

Rispondi con azioni specifiche per un mixing professionale.
"""

            response = await self.ai_client.get_dj_decision(self.dj_context, query, urgent=True)

            # Esegui transizione
            success = await self._execute_transition(from_deck, to_deck, next_track, response)

            if success:
                # Aggiorna contesto
                self.dj_context.last_track = f"{next_track.title} - {next_track.artist}"
                self.dj_context.current_bpm = next_track.bpm or self.dj_context.current_bpm
                self.dj_context.current_genre = next_track.genre

                # Aggiungi alla sessione
                if self.current_session:
                    self.current_session.add_track_played(next_track, self.dj_context.energy_level)

                self.track_history.append(next_track.filepath)

                logger.info(f"✅ Transizione completata: {next_track.title}")

            return success

        except Exception as e:
            logger.error(f"❌ Errore transizione: {e}")
            return False

    async def _execute_transition(self, from_deck: DeckID, to_deck: DeckID,
                                 next_track: TrackInfo, ai_response: AIResponse) -> bool:
        """Esegui fisicamente la transizione"""
        try:
            # 1. Prepara nuovo deck
            logger.info(f"🎵 Caricamento track su Deck {to_deck.value}")

            # Sync BPM se abilitato
            if self.config['auto_sync_enabled'] and next_track.bpm:
                self.traktor.sync_deck(to_deck)
                await asyncio.sleep(1)

            # 2. Imposta volumi iniziali
            self.traktor.set_deck_volume(from_deck, 1.0)  # Corrente al massimo
            self.traktor.set_deck_volume(to_deck, 0.0)    # Nuovo a zero

            # 3. Play nuovo track
            self.traktor.play_deck(to_deck)
            await asyncio.sleep(1)

            # 4. Transizione crossfader graduale
            transition_steps = 20
            transition_time = self.config['transition_time']
            step_delay = transition_time / transition_steps

            for step in range(transition_steps + 1):
                progress = step / transition_steps

                # Crossfader progression
                if from_deck == DeckID.A:
                    crossfader_pos = progress  # A→B
                else:
                    crossfader_pos = 1.0 - progress  # B→A

                self.traktor.set_crossfader(crossfader_pos)

                # Volume fade per sicurezza
                from_volume = 1.0 - (progress * 0.2)  # Calo graduale
                to_volume = min(1.0, progress * 1.2)   # Crescita graduale

                self.traktor.set_deck_volume(from_deck, from_volume)
                self.traktor.set_deck_volume(to_deck, to_volume)

                await asyncio.sleep(step_delay)

            # 5. Finalizza transizione
            self.traktor.set_deck_volume(from_deck, 0.0)
            self.traktor.set_deck_volume(to_deck, 1.0)

            # Stop deck precedente
            self.traktor.pause_deck(from_deck)

            logger.info(f"✅ Transizione fisica completata")
            return True

        except Exception as e:
            logger.error(f"❌ Errore esecuzione transizione: {e}")
            return False

    async def auto_dj_loop(self):
        """Loop principale AI DJ automatico"""
        logger.info("🤖 Avvio loop AI DJ automatico")

        try:
            while self.active and self.current_session:

                # Ottieni stato attuale
                status = self.traktor.get_status()
                self.dj_context.current_bpm = status.deck_a_bpm or status.deck_b_bpm
                self.dj_context.time_in_set = int((time.time() - self.current_session.session_start) / 60)

                # Determina se è ora di una transizione
                # (logica semplificata - in un sistema reale analizzaresti la posizione del brano)
                if await self._should_transition():
                    next_track = await self.suggest_next_track(self.dj_context)

                    if next_track:
                        # Determina deck target
                        target_deck = DeckID.B if status.deck_a_bpm > 0 else DeckID.A
                        current_deck = DeckID.A if target_deck == DeckID.B else DeckID.B

                        await self.perform_transition(current_deck, target_deck, next_track)

                # Aggiorna ogni 10 secondi
                await asyncio.sleep(10)

        except Exception as e:
            logger.error(f"❌ Errore loop AI DJ: {e}")

    async def _should_transition(self) -> bool:
        """Determina se è ora di fare una transizione"""
        # Logica semplificata - in realtà controlleresti posizione track, beat phase, etc.
        if not self.current_session or not self.current_session.mixing_log:
            return True  # Prima transizione

        # Controlla tempo dall'ultimo cambio
        last_mix = self.current_session.mixing_log[-1]
        time_since_last = time.time() - last_mix['timestamp']

        # Transizione ogni 3-5 minuti (semplificato)
        min_time = 180  # 3 minuti
        max_time = 300  # 5 minuti

        return time_since_last > random.randint(min_time, max_time)

    def stop_session(self):
        """Ferma sessione DJ"""
        logger.info("🛑 Fermando sessione DJ...")
        self.active = False

        if self.current_session:
            stats = self.current_session.get_session_stats()
            logger.info(f"📊 Sessione terminata: {stats}")

    def get_session_stats(self) -> Dict[str, Any]:
        """Ottieni statistiche sessione corrente"""
        if self.current_session:
            return self.current_session.get_session_stats()
        return {}

# Factory function
def get_dj_agent(ai_client: OpenRouterClient, traktor_controller: TraktorController,
                music_scanner: MusicLibraryScanner) -> SimpleDJAgent:
    """Ottieni agente DJ configurato"""
    return SimpleDJAgent(ai_client, traktor_controller, music_scanner)

# Test function
async def test_dj_agent():
    """Test agente DJ"""
    from config import get_config
    from core.openrouter_client import get_openrouter_client
    from traktor_control import get_traktor_controller
    from music_library import get_music_scanner

    config = get_config()

    # Setup componenti
    ai_client = get_openrouter_client(config.openrouter_api_key)
    traktor = get_traktor_controller(config)
    music = get_music_scanner(config)

    # Setup sistema
    await music.scan_library()
    traktor.connect()

    # Test agente
    agent = get_dj_agent(ai_client, traktor, music)

    print("🤖 Test AI DJ Agent")
    print("=" * 50)

    # Test sessione
    success = await agent.start_session("club", "prime_time", 30)
    print(f"Avvio sessione: {'✅' if success else '❌'}")

    if success:
        # Test suggerimento
        context = DJContext(venue_type="club", current_bpm=128)
        track = await agent.suggest_next_track(context)

        if track:
            print(f"Suggerimento: {track.title} - {track.artist} ({track.bpm} BPM)")
        else:
            print("Nessun suggerimento disponibile")

        # Stats
        stats = agent.get_session_stats()
        print(f"Stats: {stats}")

        agent.stop_session()

    # Cleanup
    traktor.disconnect()
    await ai_client.close()

if __name__ == "__main__":
    asyncio.run(test_dj_agent())