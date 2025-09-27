#!/usr/bin/env python3
"""
🎵 Music Library Scanner
Scansione e gestione intelligente della libreria musicale
"""

import os
import json
import sqlite3
import time
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import hashlib

# Import con fallback
try:
    import mutagen
    from mutagen.id3 import ID3NoHeaderError
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False
    print("⚠️ mutagen non disponibile. Installa con: pip install mutagen")

from config import DJConfig

logger = logging.getLogger(__name__)

@dataclass
class TrackInfo:
    """Informazioni complete di un brano"""
    # Metadata base
    filepath: str
    filename: str
    title: str = "Unknown"
    artist: str = "Unknown"
    album: str = "Unknown"
    genre: str = "Unknown"
    year: Optional[int] = None

    # Metadata DJ
    bpm: Optional[float] = None
    key: Optional[str] = None
    duration: Optional[float] = None
    energy: Optional[int] = None  # 1-10
    danceability: Optional[int] = None  # 1-10

    # Metadata tecnici
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    file_size: int = 0
    last_modified: float = 0.0

    # Metadati calcolati
    file_hash: Optional[str] = None
    analyzed: bool = False
    compatible_bpm_range: Optional[Tuple[float, float]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converti a dizionario"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrackInfo':
        """Crea da dizionario"""
        return cls(**data)

    def calculate_compatibility(self, target_bpm: float, tolerance: float = 0.1) -> float:
        """Calcola compatibilità BPM (0.0-1.0)"""
        if not self.bpm:
            return 0.5  # Neutrale se BPM sconosciuto

        # BPM identici
        if abs(self.bpm - target_bpm) < 1:
            return 1.0

        # BPM compatibili (doppio/metà)
        ratios = [0.5, 2.0, 1.5, 0.75, 1.33, 0.67]  # Rapporti musicali comuni
        for ratio in ratios:
            scaled_bpm = target_bpm * ratio
            if abs(self.bpm - scaled_bpm) / target_bpm < tolerance:
                return 0.8

        # BPM vicini (+/- 10%)
        if abs(self.bpm - target_bpm) / target_bpm < 0.1:
            return 0.6

        # BPM lontani
        return 0.2

class MusicLibraryScanner:
    """Scanner intelligente per libreria musicale"""

    def __init__(self, config: DJConfig):
        self.config = config
        self.db_path = Path(config.music_library_path).parent / ".dj_library.db"
        self.cache_file = Path(config.music_library_path).parent / ".dj_cache.json"

        # Statistiche
        self.stats = {
            'total_files': 0,
            'analyzed_files': 0,
            'skipped_files': 0,
            'new_files': 0,
            'updated_files': 0,
            'scan_time': 0.0
        }

        self._init_database()

    def _init_database(self):
        """Inizializza database SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS tracks (
                        filepath TEXT PRIMARY KEY,
                        filename TEXT,
                        title TEXT,
                        artist TEXT,
                        album TEXT,
                        genre TEXT,
                        year INTEGER,
                        bpm REAL,
                        key TEXT,
                        duration REAL,
                        energy INTEGER,
                        danceability INTEGER,
                        bitrate INTEGER,
                        sample_rate INTEGER,
                        file_size INTEGER,
                        last_modified REAL,
                        file_hash TEXT,
                        analyzed BOOLEAN,
                        created_at REAL,
                        updated_at REAL
                    )
                ''')

                # Indici per performance
                conn.execute('CREATE INDEX IF NOT EXISTS idx_genre ON tracks(genre)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_bpm ON tracks(bpm)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_key ON tracks(key)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_energy ON tracks(energy)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_artist ON tracks(artist)')

                conn.commit()
        except Exception as e:
            logger.error(f"Errore inizializzazione database: {e}")

    def _calculate_file_hash(self, filepath: Path) -> str:
        """Calcola hash veloce del file per rilevare modifiche"""
        try:
            stat = filepath.stat()
            # Hash basato su dimensione + data modifica (veloce)
            hash_input = f"{stat.st_size}_{stat.st_mtime}_{filepath.name}"
            return hashlib.md5(hash_input.encode()).hexdigest()
        except:
            return ""

    def _extract_metadata(self, filepath: Path) -> TrackInfo:
        """Estrai metadata da file musicale"""
        track = TrackInfo(
            filepath=str(filepath),
            filename=filepath.name,
            file_size=filepath.stat().st_size,
            last_modified=filepath.stat().st_mtime,
            file_hash=self._calculate_file_hash(filepath)
        )

        if not MUTAGEN_AVAILABLE:
            return track

        try:
            # Usa mutagen per leggere metadata
            file = mutagen.File(filepath)
            if file is None:
                return track

            # Metadata base
            track.title = self._get_tag(file, ['TIT2', 'TITLE', '\xa9nam']) or filepath.stem
            track.artist = self._get_tag(file, ['TPE1', 'ARTIST', '\xa9ART']) or "Unknown"
            track.album = self._get_tag(file, ['TALB', 'ALBUM', '\xa9alb']) or "Unknown"
            track.genre = self._get_tag(file, ['TCON', 'GENRE', '\xa9gen']) or "Unknown"

            # Anno
            year_str = self._get_tag(file, ['TDRC', 'DATE', 'YEAR', '\xa9day'])
            if year_str:
                try:
                    track.year = int(str(year_str)[:4])
                except:
                    pass

            # Metadata DJ
            track.bpm = self._get_numeric_tag(file, ['TBPM', 'BPM'])
            track.key = self._get_tag(file, ['TKEY', 'KEY', 'INITIALKEY'])

            # Durata
            if hasattr(file, 'info') and hasattr(file.info, 'length'):
                track.duration = file.info.length

            # Qualità audio
            if hasattr(file, 'info'):
                if hasattr(file.info, 'bitrate'):
                    track.bitrate = file.info.bitrate
                if hasattr(file.info, 'sample_rate'):
                    track.sample_rate = file.info.sample_rate

            # Metadata estesi (se disponibili)
            track.energy = self._get_numeric_tag(file, ['ENERGY'])
            track.danceability = self._get_numeric_tag(file, ['DANCEABILITY'])

            track.analyzed = True

        except ID3NoHeaderError:
            logger.debug(f"No ID3 header: {filepath}")
        except Exception as e:
            logger.warning(f"Errore lettura metadata {filepath}: {e}")

        return track

    def _get_tag(self, file, tag_names: List[str]) -> Optional[str]:
        """Ottieni tag da file con nomi alternativi"""
        for tag_name in tag_names:
            try:
                if tag_name in file:
                    value = file[tag_name]
                    if hasattr(value, 'text') and value.text:
                        return str(value.text[0])
                    elif isinstance(value, list) and value:
                        return str(value[0])
                    else:
                        return str(value)
            except:
                continue
        return None

    def _get_numeric_tag(self, file, tag_names: List[str]) -> Optional[float]:
        """Ottieni tag numerico"""
        value_str = self._get_tag(file, tag_names)
        if value_str:
            try:
                return float(value_str)
            except:
                pass
        return None

    async def scan_library(self, force_rescan: bool = False) -> Dict[str, Any]:
        """Scansiona libreria musicale"""
        start_time = time.time()
        library_path = Path(self.config.music_library_path)

        logger.info(f"🎵 Scansione libreria: {library_path}")

        if not library_path.exists():
            raise FileNotFoundError(f"Cartella musica non trovata: {library_path}")

        # Reset statistiche
        self.stats = {
            'total_files': 0,
            'analyzed_files': 0,
            'skipped_files': 0,
            'new_files': 0,
            'updated_files': 0,
            'scan_time': 0.0
        }

        # Ottieni lista file esistenti nel DB
        existing_files = self._get_existing_files() if not force_rescan else {}

        # Scansiona directory
        music_files = []
        for ext in self.config.supported_formats:
            music_files.extend(library_path.glob(f"**/*{ext}"))

        self.stats['total_files'] = len(music_files)
        logger.info(f"📁 Trovati {len(music_files)} file musicali")

        # Analizza file in batch
        batch_size = 50
        for i in range(0, len(music_files), batch_size):
            batch = music_files[i:i + batch_size]
            await self._process_batch(batch, existing_files, force_rescan)

            # Log progresso
            processed = min(i + batch_size, len(music_files))
            logger.info(f"📊 Processati {processed}/{len(music_files)} file")

        # Cleanup file eliminati
        self._cleanup_deleted_files(music_files)

        self.stats['scan_time'] = time.time() - start_time
        logger.info(f"✅ Scansione completata in {self.stats['scan_time']:.1f}s")

        return self.stats

    async def _process_batch(self, batch: List[Path], existing_files: Dict[str, Dict], force_rescan: bool):
        """Processa batch di file"""
        for filepath in batch:
            try:
                filepath_str = str(filepath)

                # Controlla se file è cambiato
                if not force_rescan and filepath_str in existing_files:
                    existing_hash = existing_files[filepath_str].get('file_hash', '')
                    current_hash = self._calculate_file_hash(filepath)

                    if existing_hash == current_hash:
                        self.stats['skipped_files'] += 1
                        continue

                # Estrai metadata
                track = self._extract_metadata(filepath)

                # Salva nel database
                if filepath_str in existing_files:
                    self._update_track(track)
                    self.stats['updated_files'] += 1
                else:
                    self._insert_track(track)
                    self.stats['new_files'] += 1

                self.stats['analyzed_files'] += 1

                # Yield per non bloccare event loop
                if self.stats['analyzed_files'] % 10 == 0:
                    await asyncio.sleep(0.01)

            except Exception as e:
                logger.error(f"Errore processamento {filepath}: {e}")

    def _get_existing_files(self) -> Dict[str, Dict]:
        """Ottieni file esistenti dal database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('SELECT filepath, file_hash FROM tracks')
                return {row['filepath']: {'file_hash': row['file_hash']} for row in cursor}
        except:
            return {}

    def _insert_track(self, track: TrackInfo):
        """Inserisci nuovo track nel database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                now = time.time()
                conn.execute('''
                    INSERT INTO tracks (
                        filepath, filename, title, artist, album, genre, year,
                        bpm, key, duration, energy, danceability,
                        bitrate, sample_rate, file_size, last_modified,
                        file_hash, analyzed, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    track.filepath, track.filename, track.title, track.artist,
                    track.album, track.genre, track.year, track.bpm, track.key,
                    track.duration, track.energy, track.danceability,
                    track.bitrate, track.sample_rate, track.file_size,
                    track.last_modified, track.file_hash, track.analyzed,
                    now, now
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Errore inserimento track: {e}")

    def _update_track(self, track: TrackInfo):
        """Aggiorna track esistente"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE tracks SET
                        filename=?, title=?, artist=?, album=?, genre=?, year=?,
                        bpm=?, key=?, duration=?, energy=?, danceability=?,
                        bitrate=?, sample_rate=?, file_size=?, last_modified=?,
                        file_hash=?, analyzed=?, updated_at=?
                    WHERE filepath=?
                ''', (
                    track.filename, track.title, track.artist, track.album,
                    track.genre, track.year, track.bpm, track.key,
                    track.duration, track.energy, track.danceability,
                    track.bitrate, track.sample_rate, track.file_size,
                    track.last_modified, track.file_hash, track.analyzed,
                    time.time(), track.filepath
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Errore aggiornamento track: {e}")

    def _cleanup_deleted_files(self, current_files: List[Path]):
        """Rimuovi dal database file eliminati"""
        try:
            current_paths = {str(f) for f in current_files}
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT filepath FROM tracks')
                db_paths = {row[0] for row in cursor}

                deleted_paths = db_paths - current_paths
                if deleted_paths:
                    placeholders = ','.join('?' * len(deleted_paths))
                    conn.execute(f'DELETE FROM tracks WHERE filepath IN ({placeholders})', list(deleted_paths))
                    conn.commit()
                    logger.info(f"🗑️ Rimossi {len(deleted_paths)} file eliminati dal database")
        except Exception as e:
            logger.error(f"Errore cleanup database: {e}")

    def search_tracks(self,
                     genre: Optional[str] = None,
                     bpm_range: Optional[Tuple[float, float]] = None,
                     energy_range: Optional[Tuple[int, int]] = None,
                     artist: Optional[str] = None,
                     limit: int = 50) -> List[TrackInfo]:
        """Cerca track con filtri"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                query = "SELECT * FROM tracks WHERE 1=1"
                params = []

                if genre:
                    query += " AND genre LIKE ?"
                    params.append(f"%{genre}%")

                if bpm_range:
                    query += " AND bpm BETWEEN ? AND ?"
                    params.extend(bpm_range)

                if energy_range:
                    query += " AND energy BETWEEN ? AND ?"
                    params.extend(energy_range)

                if artist:
                    query += " AND artist LIKE ?"
                    params.append(f"%{artist}%")

                query += " ORDER BY title LIMIT ?"
                params.append(limit)

                cursor = conn.execute(query, params)
                return [TrackInfo.from_dict(dict(row)) for row in cursor]

        except Exception as e:
            logger.error(f"Errore ricerca tracks: {e}")
            return []

    def get_compatible_tracks(self, current_bpm: float, current_genre: str = None, limit: int = 20) -> List[TrackInfo]:
        """Ottieni track compatibili per mixing"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Calcola range BPM compatibili
                bpm_tolerance = 0.15  # ±15%
                min_bpm = current_bpm * (1 - bpm_tolerance)
                max_bpm = current_bpm * (1 + bpm_tolerance)

                # Query con priorità su BPM simili
                query = '''
                    SELECT *,
                           ABS(bpm - ?) as bpm_diff,
                           CASE
                               WHEN genre = ? THEN 1
                               ELSE 0
                           END as genre_match
                    FROM tracks
                    WHERE bpm IS NOT NULL
                    AND (bpm BETWEEN ? AND ?
                         OR bpm BETWEEN ? AND ?
                         OR bpm BETWEEN ? AND ?)
                    ORDER BY genre_match DESC, bpm_diff ASC
                    LIMIT ?
                '''

                params = [
                    current_bpm,  # Per calcolo differenza
                    current_genre or '',  # Per match genere
                    min_bpm, max_bpm,  # Range normale
                    min_bpm / 2, max_bpm / 2,  # Range doppio tempo
                    min_bpm * 2, max_bpm * 2,  # Range metà tempo
                    limit
                ]

                cursor = conn.execute(query, params)
                tracks = [TrackInfo.from_dict(dict(row)) for row in cursor]

                # Calcola compatibilità per ogni track
                for track in tracks:
                    track.compatible_bpm_range = (
                        track.calculate_compatibility(current_bpm),
                        track.bpm
                    )

                return tracks

        except Exception as e:
            logger.error(f"Errore ricerca compatibili: {e}")
            return []

    def get_library_stats(self) -> Dict[str, Any]:
        """Ottieni statistiche libreria"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT
                        COUNT(*) as total_tracks,
                        COUNT(DISTINCT artist) as unique_artists,
                        COUNT(DISTINCT genre) as unique_genres,
                        COUNT(DISTINCT album) as unique_albums,
                        AVG(bpm) as avg_bpm,
                        AVG(duration) as avg_duration,
                        SUM(file_size) as total_size
                    FROM tracks
                ''')

                stats = dict(cursor.fetchone())

                # Top generi
                cursor = conn.execute('''
                    SELECT genre, COUNT(*) as count
                    FROM tracks
                    GROUP BY genre
                    ORDER BY count DESC
                    LIMIT 10
                ''')
                stats['top_genres'] = [dict(row) for row in cursor]

                # Top artisti
                cursor = conn.execute('''
                    SELECT artist, COUNT(*) as count
                    FROM tracks
                    GROUP BY artist
                    ORDER BY count DESC
                    LIMIT 10
                ''')
                stats['top_artists'] = [dict(row) for row in cursor]

                return stats

        except Exception as e:
            logger.error(f"Errore statistiche: {e}")
            return {}

# Factory function
def get_music_scanner(config: DJConfig = None) -> MusicLibraryScanner:
    """Ottieni scanner configurato"""
    if config is None:
        from config import get_config
        config = get_config()

    return MusicLibraryScanner(config)

# Test function
async def test_music_scanner():
    """Test music scanner"""
    from config import get_config

    config = get_config()
    scanner = get_music_scanner(config)

    print("🎵 Test Music Library Scanner")
    print("=" * 50)

    # Test scan
    print("📊 Scansione libreria...")
    stats = await scanner.scan_library()

    print(f"Statistiche scansione:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Test search
    print(f"\n🔍 Test ricerca...")
    tracks = scanner.search_tracks(genre="house", limit=5)
    print(f"Trovati {len(tracks)} track house")

    for track in tracks[:3]:
        print(f"  '{track.title}' - {track.artist} ({track.genre}, {track.bpm} BPM)")

    # Test compatibili
    print(f"\n🎛️ Test compatibilità (BPM 128)...")
    compatible = scanner.get_compatible_tracks(128.0, "house", limit=5)
    print(f"Trovati {len(compatible)} track compatibili")

    for track in compatible[:3]:
        comp = track.compatible_bpm_range[0] if track.compatible_bpm_range else 0
        print(f"  '{track.title}' - {track.bpm} BPM (compatibilità: {comp:.2f})")

    # Stats generali
    print(f"\n📈 Statistiche libreria:")
    lib_stats = scanner.get_library_stats()
    for key, value in lib_stats.items():
        if not isinstance(value, list):
            print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(test_music_scanner())