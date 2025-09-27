#!/usr/bin/env python3
"""
🔧 Installer Dipendenze DJ AI System
Installa automaticamente tutte le dipendenze necessarie
"""

import subprocess
import sys

def install_package(package):
    """Installa un package usando pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installato con successo")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore installazione {package}: {e}")
        return False

def main():
    print("🎧 DJ AI System - Installer Dipendenze")
    print("=" * 50)

    # Lista dipendenze essenziali
    dependencies = [
        "python-rtmidi>=1.4.9",
        "mido>=1.2.10",
        "mutagen>=1.46.0",
        "requests>=2.32.0"
    ]

    print("📦 Installazione dipendenze...")

    success_count = 0
    for dep in dependencies:
        print(f"\n📥 Installando {dep}...")
        if install_package(dep):
            success_count += 1

    print(f"\n📊 Risultati:")
    print(f"✅ Successi: {success_count}/{len(dependencies)}")

    if success_count == len(dependencies):
        print("\n🎉 Tutte le dipendenze installate con successo!")
        print("🚀 Ora puoi avviare il sistema con: python3 dj_ai.py")
    else:
        print(f"\n⚠️  {len(dependencies) - success_count} dipendenze fallite")
        print("💡 Prova a installarle manualmente con pip")

    # Test import
    print("\n🧪 Test import...")
    test_imports = [
        ("rtmidi", "rtmidi"),
        ("mido", "mido"),
        ("mutagen", "mutagen"),
        ("requests", "requests")
    ]

    for name, module in test_imports:
        try:
            __import__(module)
            print(f"✅ {name}: OK")
        except ImportError:
            print(f"❌ {name}: FALLITO")

if __name__ == "__main__":
    main()