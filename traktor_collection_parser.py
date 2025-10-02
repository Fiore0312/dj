#!/usr/bin/env python3
"""
🎵 Traktor Collection Parser
Parse diretto di collection.nml per accesso completo alla libreria Traktor

Questo modulo risolve il problema fondamentale: il sistema non può "vedere" dove sono le tracce
in Traktor. Invece di navigare ciecamente nel browser, ora abbiamo accesso diretto a tutti i
metadata e posizioni delle tracce.
"""

import xml.etree.ElementTree as ET
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict
import json
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class TraktorTrackInfo:
    """
    Informazioni complete di una traccia da collection.nml
    Struttura completa con tutti i metadata Traktor
    """
    # File info
    filepath: str
    filename: str
    volume: str
    dir: str

    # Basic metadata
    title: str = "Unknown"
    artist: str = "Unknown"
    album: str = "Unknown"
    genre: str = "Unknown"
    label: str = ""
    year: Optional[int] = None

    # DJ metadata (critical!)
    bpm: Optional[float] = None
    bpm_quality: Optional[float] = None
    musical_key: Optional[int] = None  # Traktor key code (0-23)
    musical_key_text: Optional[str] = None  # Human readable (8A, 5B, etc)

    # Technical
    bitrate: Optional[int] = None
    duration: Optional[float] = None  # in seconds
    filesize: Optional[int] = None
    import_date: Optional[str] = None
    last_played: Optional[str] = None
    play_count: int = 0

    # Traktor specific
    rating: int = 0  # 0-255 (Traktor uses 0-255, not 1-5)
    color: Optional[str] = None
    comment: str = ""
    cue_points: List[Dict] = field(default_factory=list)
    loops: List[Dict] = field(default_factory=list)

    # Position mapping (calculated)
    browser_position: Optional[int] = None
    collection_index: Optional[int] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'filepath': self.filepath,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'genre': self.genre,
            'bpm': self.bpm,
            'key': self.musical_key_text or self.musical_key,
            'duration': self.duration,
            'rating': self.rating,
            'play_count': self.play_count,
            'browser_position': self.browser_position
        }

    def get_camelot_key(self) -> Optional[str]:
        """
        Convert Traktor musical_key (0-23) to Camelot notation (1A-12B)

        Traktor Key Mapping:
        0 = C major (8B)    12 = A minor (8A)
        1 = Db major (3B)   13 = Bb minor (3A)
        ...etc
        """
        if self.musical_key is None:
            return None

        # Traktor key to Camelot mapping
        # Reference: https://github.com/Holzhaus/traubisoda/blob/master/src/key.rs
        camelot_map = {
            # Major keys (outer circle)
            0: "8B",   # C
            1: "3B",   # Db/C#
            2: "10B",  # D
            3: "5B",   # Eb
            4: "12B",  # E
            5: "7B",   # F
            6: "2B",   # Gb/F#
            7: "9B",   # G
            8: "4B",   # Ab/G#
            9: "11B",  # A
            10: "6B",  # Bb
            11: "1B",  # B
            # Minor keys (inner circle)
            12: "5A",  # Am
            13: "12A", # Bbm
            14: "7A",  # Bm
            15: "2A",  # Cm
            16: "9A",  # C#m
            17: "4A",  # Dm
            18: "11A", # Ebm
            19: "6A",  # Em
            20: "1A",  # Fm
            21: "8A",  # F#m
            22: "3A",  # Gm
            23: "10A"  # G#m
        }

        return camelot_map.get(self.musical_key, None)

    def is_compatible_key(self, other_key: str) -> bool:
        """
        Check if this track is compatible with another track's key
        Uses Camelot wheel: compatible keys are ±1 number or same number different letter
        """
        my_key = self.get_camelot_key()
        if not my_key or not other_key:
            return True  # Unknown keys = assume compatible

        # Parse Camelot notation (e.g., "8B" -> number=8, letter=B)
        try:
            my_num = int(my_key[:-1])
            my_letter = my_key[-1]
            other_num = int(other_key[:-1])
            other_letter = other_key[-1]
        except:
            return True  # Parse error = assume compatible

        # Perfect match
        if my_key == other_key:
            return True

        # Energy boost/drop (same number, different letter)
        if my_num == other_num and my_letter != other_letter:
            return True

        # Harmonic mixing (±1 number, same letter)
        if my_letter == other_letter:
            if abs(my_num - other_num) == 1:
                return True
            # Handle wrap-around (12 and 1 are neighbors)
            if (my_num == 12 and other_num == 1) or (my_num == 1 and other_num == 12):
                return True

        return False


@dataclass
class PlaylistInfo:
    """Information about a Traktor playlist"""
    name: str
    type: str  # "LIST", "FOLDER", "SMARTLIST"
    uuid: str
    entries: List[str] = field(default_factory=list)  # Track filepaths


class TraktorCollectionParser:
    """
    Parser per collection.nml di Traktor

    Fornisce accesso completo alla libreria Traktor:
    - Parse di tutti i metadata
    - Mapping track → browser position
    - Support per playlists
    - Caching per performance
    """

    def __init__(self, collection_path: Optional[str] = None):
        """
        Initialize parser

        Args:
            collection_path: Path to collection.nml. If None, tries default locations.
        """
        self.collection_path = collection_path or self._find_collection_nml()
        self.tracks: Dict[str, TraktorTrackInfo] = {}
        self.playlists: Dict[str, PlaylistInfo] = {}
        self.browser_position_map: Dict[str, int] = {}
        self.last_parse_time: Optional[float] = None
        self.collection_hash: Optional[str] = None

        logger.info(f"📂 Traktor Collection Parser initialized")
        if self.collection_path:
            logger.info(f"   Collection: {self.collection_path}")
        else:
            logger.warning("⚠️  Collection.nml not found in default locations")

    def _find_collection_nml(self) -> Optional[str]:
        """
        Find collection.nml in default Traktor locations

        Returns:
            Path to collection.nml or None if not found
        """
        # macOS default locations
        possible_paths = [
            Path.home() / "Documents" / "Native Instruments" / "Traktor 3.11.1" / "collection.nml",
            Path.home() / "Documents" / "Native Instruments" / "Traktor 3" / "collection.nml",
            Path.home() / "Documents" / "Native Instruments" / "Traktor 2" / "collection.nml",
            Path.home() / "Documents" / "Native Instruments" / "Traktor" / "collection.nml",
        ]

        for path in possible_paths:
            if path.exists():
                logger.info(f"✅ Found collection.nml: {path}")
                return str(path)

        logger.warning("❌ Collection.nml not found in default locations")
        logger.info("   Checked:")
        for path in possible_paths:
            logger.info(f"   - {path}")

        return None

    def parse_collection(self, force_refresh: bool = False) -> bool:
        """
        Parse collection.nml and extract all track info

        Args:
            force_refresh: Force re-parse even if cached

        Returns:
            True if successful, False otherwise
        """
        if not self.collection_path:
            logger.error("❌ No collection path set")
            return False

        collection_path = Path(self.collection_path)

        if not collection_path.exists():
            logger.error(f"❌ Collection file not found: {collection_path}")
            return False

        # Check if collection changed (using file hash)
        current_hash = self._calculate_file_hash(collection_path)

        if not force_refresh and current_hash == self.collection_hash:
            logger.info("✅ Collection unchanged, using cached data")
            return True

        logger.info(f"🔄 Parsing Traktor collection: {collection_path}")
        start_time = time.time()

        try:
            # Parse XML
            tree = ET.parse(collection_path)
            root = tree.getroot()

            # Parse COLLECTION section
            collection_elem = root.find('COLLECTION')
            if collection_elem is None:
                logger.error("❌ No COLLECTION element found in NML")
                return False

            entries_count = int(collection_elem.get('ENTRIES', 0))
            logger.info(f"   Found {entries_count} tracks in collection")

            # Parse each track entry
            self.tracks.clear()
            position = 0

            for entry in collection_elem.findall('ENTRY'):
                track_info = self._parse_entry(entry, position)
                if track_info:
                    self.tracks[track_info.filepath] = track_info
                    self.browser_position_map[track_info.filepath] = position
                    position += 1

            # Parse PLAYLISTS section
            playlists_elem = root.find('PLAYLISTS')
            if playlists_elem is not None:
                self._parse_playlists(playlists_elem)

            # Update metadata
            self.last_parse_time = time.time()
            self.collection_hash = current_hash

            elapsed = time.time() - start_time
            logger.info(f"✅ Collection parsed successfully in {elapsed:.2f}s")
            logger.info(f"   Tracks: {len(self.tracks)}")
            logger.info(f"   Playlists: {len(self.playlists)}")

            return True

        except ET.ParseError as e:
            logger.error(f"❌ XML parse error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error parsing collection: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _parse_entry(self, entry: ET.Element, position: int) -> Optional[TraktorTrackInfo]:
        """Parse a single ENTRY element"""
        try:
            # LOCATION (required)
            location = entry.find('LOCATION')
            if location is None:
                return None

            volume = location.get('VOLUME', '')
            dir_path = location.get('DIR', '')
            filename = location.get('FILE', '')

            # Construct full filepath
            # Traktor uses "/:Users/:Music/" format, convert to "/Users/Music/"
            filepath = self._construct_filepath(volume, dir_path, filename)

            # INFO section
            info = entry.find('INFO')
            title = info.get('TITLE', 'Unknown') if info is not None else 'Unknown'
            artist = info.get('ARTIST', 'Unknown') if info is not None else 'Unknown'
            album = info.get('ALBUM', '') if info is not None else ''
            genre = info.get('GENRE', '') if info is not None else ''
            label = info.get('LABEL', '') if info is not None else ''
            comment = info.get('COMMENT', '') if info is not None else ''

            # Rating parsing (Traktor uses strings like '+', '++', '+++', 'NNN', etc)
            rating = 0
            if info is not None:
                rating_str = info.get('RATING', '0')
                try:
                    rating = int(rating_str)
                except ValueError:
                    # Traktor sometimes uses + symbols or other strings
                    # Count '+' symbols as rating (+ = 1, ++ = 2, etc)
                    rating = rating_str.count('+')
                    if rating == 0:
                        # Other non-numeric ratings (NNN, **, etc)
                        rating = 0

            # Play count parsing with safety
            play_count = 0
            if info is not None:
                try:
                    play_count = int(info.get('PLAYCOUNT', 0))
                except ValueError:
                    play_count = 0

            # TEMPO section
            tempo = entry.find('TEMPO')
            bpm = float(tempo.get('BPM', 0)) if tempo is not None else None
            bpm_quality = float(tempo.get('BPM_QUALITY', 0)) if tempo is not None else None

            # MUSICAL_KEY section
            musical_key_elem = entry.find('MUSICAL_KEY')
            musical_key = None
            if musical_key_elem is not None:
                key_value = musical_key_elem.get('VALUE')
                if key_value:
                    musical_key = int(key_value)

            # Parse cue points
            cue_points = []
            for cue in entry.findall('CUE_V2'):
                cue_points.append({
                    'name': cue.get('NAME', ''),
                    'start': float(cue.get('START', 0)),
                    'type': int(cue.get('TYPE', 0))
                })

            # Create track info
            track = TraktorTrackInfo(
                filepath=filepath,
                filename=filename,
                volume=volume,
                dir=dir_path,
                title=title,
                artist=artist,
                album=album,
                genre=genre,
                label=label,
                comment=comment,
                bpm=bpm,
                bpm_quality=bpm_quality,
                musical_key=musical_key,
                rating=rating,
                play_count=play_count,
                cue_points=cue_points,
                browser_position=position,
                collection_index=position
            )

            # Add Camelot key text
            track.musical_key_text = track.get_camelot_key()

            return track

        except Exception as e:
            logger.error(f"❌ Error parsing entry: {e}")
            return None

    def _construct_filepath(self, volume: str, dir_path: str, filename: str) -> str:
        """
        Construct full filepath from Traktor's format

        Traktor uses: VOLUME="Macintosh HD" DIR="/:Users/:Music/" FILE="track.mp3"
        Convert to: /Users/Music/track.mp3
        """
        # Remove leading/trailing slashes and replace /: with /
        clean_dir = dir_path.replace('/:', '/').strip('/')

        # Construct path
        if clean_dir:
            return f"/{clean_dir}/{filename}"
        else:
            return f"/{filename}"

    def _parse_playlists(self, playlists_elem: ET.Element):
        """Parse PLAYLISTS section"""
        # TODO: Implement playlist parsing if needed
        pass

    def _calculate_file_hash(self, filepath: Path) -> str:
        """Calculate MD5 hash of file for change detection"""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def get_track_by_path(self, filepath: str) -> Optional[TraktorTrackInfo]:
        """Get track info by filepath"""
        return self.tracks.get(filepath)

    def get_track_browser_position(self, filepath: str) -> Optional[int]:
        """Get browser position for a track"""
        return self.browser_position_map.get(filepath)

    def get_tracks_by_bpm_range(self, min_bpm: float, max_bpm: float) -> List[TraktorTrackInfo]:
        """Get all tracks within BPM range"""
        return [
            track for track in self.tracks.values()
            if track.bpm and min_bpm <= track.bpm <= max_bpm
        ]

    def get_tracks_by_key(self, key: str) -> List[TraktorTrackInfo]:
        """Get all tracks with specific Camelot key (e.g., "8A")"""
        return [
            track for track in self.tracks.values()
            if track.get_camelot_key() == key
        ]

    def get_compatible_tracks(self, reference_track: TraktorTrackInfo,
                            bpm_tolerance: float = 6.0) -> List[TraktorTrackInfo]:
        """
        Get tracks compatible with reference track

        Compatible means:
        - BPM within tolerance or musical ratios (1.5x, 2x, etc)
        - Key is harmonically compatible (Camelot wheel)

        Args:
            reference_track: Track to find compatibles for
            bpm_tolerance: BPM difference tolerance (default ±6 BPM)

        Returns:
            List of compatible tracks sorted by compatibility score
        """
        if not reference_track.bpm:
            return []

        compatible = []
        ref_bpm = reference_track.bpm
        ref_key = reference_track.get_camelot_key()

        for track in self.tracks.values():
            if track.filepath == reference_track.filepath:
                continue  # Skip same track

            if not track.bpm:
                continue  # Skip tracks without BPM

            # Check BPM compatibility
            bpm_compatible = False

            # Direct BPM match (±tolerance)
            if abs(track.bpm - ref_bpm) <= bpm_tolerance:
                bpm_compatible = True

            # Musical ratios (1.5x, 2x, 0.5x, etc)
            ratios = [1.5, 2.0, 0.5, 0.75, 1.33, 0.67]
            for ratio in ratios:
                scaled_bpm = ref_bpm * ratio
                if abs(track.bpm - scaled_bpm) <= bpm_tolerance:
                    bpm_compatible = True
                    break

            if not bpm_compatible:
                continue

            # Check key compatibility
            if ref_key:
                track_key = track.get_camelot_key()
                if track_key and not track.is_compatible_key(ref_key):
                    continue  # Skip incompatible keys

            compatible.append(track)

        # Sort by BPM closeness
        compatible.sort(key=lambda t: abs(t.bpm - ref_bpm) if t.bpm else 999)

        return compatible

    def get_all_tracks(self) -> List[TraktorTrackInfo]:
        """Get all tracks in collection"""
        return list(self.tracks.values())

    def get_collection_stats(self) -> Dict:
        """Get collection statistics"""
        if not self.tracks:
            return {}

        total_tracks = len(self.tracks)
        tracks_with_bpm = sum(1 for t in self.tracks.values() if t.bpm)
        tracks_with_key = sum(1 for t in self.tracks.values() if t.musical_key is not None)
        avg_bpm = sum(t.bpm for t in self.tracks.values() if t.bpm) / tracks_with_bpm if tracks_with_bpm > 0 else 0

        # Genre distribution
        genres = defaultdict(int)
        for track in self.tracks.values():
            if track.genre:
                genres[track.genre] += 1

        return {
            'total_tracks': total_tracks,
            'tracks_with_bpm': tracks_with_bpm,
            'tracks_with_key': tracks_with_key,
            'average_bpm': round(avg_bpm, 1),
            'genres': dict(sorted(genres.items(), key=lambda x: x[1], reverse=True)[:10]),
            'last_parse': self.last_parse_time,
            'collection_path': self.collection_path
        }

    def save_cache(self, cache_path: str = ".traktor_cache.json"):
        """Save parsed collection to cache file"""
        cache_data = {
            'collection_hash': self.collection_hash,
            'last_parse_time': self.last_parse_time,
            'tracks': {path: track.to_dict() for path, track in self.tracks.items()},
            'browser_position_map': self.browser_position_map
        }

        with open(cache_path, 'w') as f:
            json.dump(cache_data, f, indent=2)

        logger.info(f"💾 Cache saved: {cache_path}")

    def load_cache(self, cache_path: str = ".traktor_cache.json") -> bool:
        """Load parsed collection from cache file"""
        try:
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)

            self.collection_hash = cache_data['collection_hash']
            self.last_parse_time = cache_data['last_parse_time']
            self.browser_position_map = cache_data['browser_position_map']

            # Reconstruct tracks (simplified from dict)
            # Note: This is a simplified version, full reconstruction would need more work

            logger.info(f"💾 Cache loaded: {cache_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Error loading cache: {e}")
            return False


if __name__ == "__main__":
    # Test the parser
    logging.basicConfig(level=logging.INFO)

    print("🎵 Traktor Collection Parser Test")
    print("=" * 60)

    parser = TraktorCollectionParser()

    if parser.collection_path:
        print(f"\n📂 Collection found: {parser.collection_path}")

        # Parse collection
        if parser.parse_collection():
            print("\n✅ Collection parsed successfully!")

            # Show stats
            stats = parser.get_collection_stats()
            print("\n📊 Collection Statistics:")
            print(f"   Total tracks: {stats['total_tracks']}")
            print(f"   Tracks with BPM: {stats['tracks_with_bpm']}")
            print(f"   Tracks with Key: {stats['tracks_with_key']}")
            print(f"   Average BPM: {stats['average_bpm']}")

            if stats['genres']:
                print("\n🎼 Top Genres:")
                for genre, count in list(stats['genres'].items())[:5]:
                    print(f"   {genre}: {count} tracks")

            # Show some example tracks
            all_tracks = parser.get_all_tracks()
            if all_tracks:
                print("\n🎵 Sample Tracks:")
                for track in all_tracks[:5]:
                    print(f"\n   {track.artist} - {track.title}")
                    print(f"   BPM: {track.bpm}  Key: {track.get_camelot_key()}")
                    print(f"   Position: {track.browser_position}")
                    print(f"   File: {track.filepath}")

                # Test compatibility
                reference_track = all_tracks[0]
                print(f"\n🔍 Compatible tracks with: {reference_track.artist} - {reference_track.title}")
                compatible = parser.get_compatible_tracks(reference_track)
                print(f"   Found {len(compatible)} compatible tracks")

                for track in compatible[:3]:
                    print(f"   - {track.artist} - {track.title} (BPM: {track.bpm}, Key: {track.get_camelot_key()})")
        else:
            print("\n❌ Failed to parse collection")
    else:
        print("\n❌ Collection.nml not found")
        print("   Please specify path manually:")
        print("   parser = TraktorCollectionParser('/path/to/collection.nml')")