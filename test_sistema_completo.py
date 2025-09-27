#!/usr/bin/env python3
"""
🧪 Test Sistema Completo DJ AI
Test di tutti i componenti principali
"""

import asyncio
import sys
from pathlib import Path

# Aggiungi directory root al path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test imports di base"""
    print("🔍 Test imports...")

    try:
        import config
        print("✅ config")

        from core.openrouter_client import OpenRouterClient, DJContext
        print("✅ OpenRouter client")

        import traktor_control
        print("✅ traktor_control")

        import music_library
        print("✅ music_library")

        import ai_dj_agent
        print("✅ ai_dj_agent")

        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_openrouter():
    """Test connessione OpenRouter"""
    print("\n🤖 Test OpenRouter AI...")

    try:
        from core.openrouter_client import get_openrouter_client, DJContext
        from config import get_config

        config = get_config()
        if not config.openrouter_api_key:
            print("❌ API key mancante")
            return False

        client = get_openrouter_client(config.openrouter_api_key)

        # Test veloce
        context = DJContext(venue_type="club", energy_level=5)
        response = client.get_dj_decision(context, "Test rapido - rispondi solo 'OK'", urgent=True)

        if response.success:
            print(f"✅ AI Response: {response.response}")
            print(f"⏱️ Tempo: {response.processing_time_ms:.0f}ms")
            return True
        else:
            print(f"❌ Errore AI: {response.error}")
            return False

    except Exception as e:
        print(f"❌ OpenRouter error: {e}")
        return False

def test_traktor_midi():
    """Test setup MIDI Traktor"""
    print("\n🎛️ Test MIDI Setup...")

    try:
        from traktor_control import TraktorController
        from config import get_config

        config = get_config()
        controller = TraktorController(config)
        success = controller.connect()

        if success:
            print("✅ MIDI connection OK")

            # Test segnale di base
            from traktor_control import DeckID
            controller.set_deck_volume(DeckID.A, 0.5)
            print("✅ Test comando volume inviato")

            controller.disconnect()
            return True
        else:
            print("❌ MIDI connection failed")
            return False

    except Exception as e:
        print(f"❌ MIDI error: {e}")
        return False

def test_music_library():
    """Test music library scanner"""
    print("\n🎵 Test Music Library...")

    try:
        from music_library import MusicLibraryScanner
        from config import get_config

        config = get_config()
        scanner = MusicLibraryScanner(config)

        # Conta solo i file senza scanning completo
        music_path = Path(config.music_library_path)
        if not music_path.exists():
            print(f"❌ Cartella music non trovata: {config.music_library_path}")
            return False

        music_files = []
        for ext in config.supported_formats:
            music_files.extend(music_path.glob(f"**/*{ext}"))

        print(f"✅ {len(music_files)} file musicali trovati")
        return len(music_files) > 0

    except Exception as e:
        print(f"❌ Music library error: {e}")
        return False

def test_dj_agent():
    """Test AI DJ agent"""
    print("\n🎯 Test DJ Agent...")

    try:
        from ai_dj_agent import SimpleDJAgent
        from core.openrouter_client import get_openrouter_client
        from traktor_control import TraktorController
        from music_library import MusicLibraryScanner
        from config import get_config

        config = get_config()

        # Crea componenti necessari
        ai_client = get_openrouter_client(config.openrouter_api_key)
        traktor = TraktorController(config)
        music_scanner = MusicLibraryScanner(config)

        agent = SimpleDJAgent(ai_client, traktor, music_scanner)
        print("✅ DJ Agent initialized")

        # Test track suggestion
        from core.openrouter_client import DJContext
        context = DJContext(venue_type="club", energy_level=6, current_bpm=128)

        # Test semplice - usa direttamente il client AI
        response = agent.ai_client.get_dj_decision(context, "Il crowd sta ballando bene, cosa faccio?")

        if response.success:
            print(f"✅ AI Advice: {response.response[:100]}...")
            return True
        else:
            print("❌ Nessun consiglio ricevuto")
            return False

    except Exception as e:
        print(f"❌ DJ Agent error: {e}")
        return False

def main():
    """Test completo sistema"""
    print("🎧 TEST SISTEMA DJ AI COMPLETO")
    print("=" * 50)

    results = []

    # Test sequenziali
    results.append(("Imports", test_imports()))
    results.append(("Music Library", test_music_library()))
    results.append(("MIDI Setup", test_traktor_midi()))
    results.append(("OpenRouter AI", test_openrouter()))
    results.append(("DJ Agent", test_dj_agent()))

    # Risultati
    print("\n📊 RISULTATI TEST")
    print("=" * 30)

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:15} {status}")
        if result:
            passed += 1

    print(f"\n🎯 Test passati: {passed}/{len(results)}")

    if passed == len(results):
        print("\n🎉 SISTEMA COMPLETAMENTE FUNZIONALE!")
        print("🚀 Pronto per DJ session autonoma")
    else:
        print("\n⚠️  Alcuni test falliti - verifica configurazione")

    return passed == len(results)

if __name__ == "__main__":
    main()