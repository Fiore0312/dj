#!/usr/bin/env python3
"""
🎧 Autonomous DJ System - Setup Script
Automated setup for complete DJ system with Traktor Pro integration
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Ensure Python 3.8+ is being used"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def setup_virtual_environment():
    """Create and activate virtual environment"""
    venv_path = Path("dj_env")

    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "dj_env"], check=True)
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment already exists")

    # Get activation script path
    if platform.system() == "Windows":
        activate_script = venv_path / "Scripts" / "activate.bat"
        pip_path = venv_path / "Scripts" / "pip"
    else:
        activate_script = venv_path / "bin" / "activate"
        pip_path = venv_path / "bin" / "pip"

    print(f"📝 To activate virtual environment, run:")
    if platform.system() == "Windows":
        print(f"   dj_env\\Scripts\\activate")
    else:
        print(f"   source dj_env/bin/activate")

    return pip_path

def install_dependencies(pip_path):
    """Install all required dependencies"""
    print("📥 Installing dependencies...")

    try:
        # Upgrade pip first
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)

        # Install requirements
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)

        print("✅ All dependencies installed successfully")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print("💡 Try activating the virtual environment and running:")
        print("   pip install -r requirements.txt")
        return False

    return True

def setup_midi_system():
    """Setup MIDI system based on operating system"""
    os_name = platform.system()
    print(f"🎛️ Setting up MIDI for {os_name}...")

    if os_name == "Windows":
        print("💡 For Windows:")
        print("   1. Download and install LoopMIDI from https://www.tobias-erichsen.de/software/loopmidi.html")
        print("   2. Create a virtual MIDI port named 'TraktorPy'")

    elif os_name == "Darwin":  # macOS
        print("💡 For macOS:")
        print("   1. Virtual MIDI ports will be created automatically")
        print("   2. Open Audio MIDI Setup if you need manual configuration")

    elif os_name == "Linux":
        print("💡 For Linux:")
        print("   1. Install ALSA utilities: sudo apt-get install alsa-utils")
        print("   2. Load virtual MIDI module: sudo modprobe snd-virmidi midi_devs=2")

    print("✅ MIDI setup instructions provided")

def create_project_structure():
    """Create any missing project directories"""
    directories = [
        "traktor_midi_driver/__pycache__",
        "dj_gui/__pycache__",
        "autonomous_dj/__pycache__",
        "logs",
        "config",
        "music_cache"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    print("✅ Project structure verified")

def create_initial_config():
    """Create initial configuration files"""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    # Create basic config file
    config_content = """[MIDI]
virtual_port_name = TraktorPy
latency_target_ms = 5.0
auto_connect = true

[GUI]
theme = dark
window_width = 1200
window_height = 800
always_on_top = false

[DJ_AGENT]
default_profile = club_dj
energy_adaptation = high
transition_length = long
harmonic_mixing = strict

[AUDIO]
sample_rate = 44100
buffer_size = 512
audio_cache_size = 100

[LOGGING]
level = INFO
log_file = logs/dj_system.log
max_file_size = 10MB
backup_count = 5
"""

    config_file = config_dir / "dj_config.ini"
    if not config_file.exists():
        config_file.write_text(config_content)
        print("✅ Initial configuration created")
    else:
        print("✅ Configuration file already exists")

def main():
    """Main setup function"""
    print("🎧 Autonomous DJ System - Setup")
    print("=" * 40)

    # Check Python version
    check_python_version()

    # Setup virtual environment
    pip_path = setup_virtual_environment()

    # Install dependencies
    if not install_dependencies(pip_path):
        print("❌ Setup failed during dependency installation")
        sys.exit(1)

    # Setup MIDI system
    setup_midi_system()

    # Create project structure
    create_project_structure()

    # Create initial config
    create_initial_config()

    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Activate virtual environment (see command above)")
    print("   2. Install and configure Traktor Pro")
    print("   3. Setup MIDI as instructed for your OS")
    print("   4. Run: python main.py")

    print("\n📚 For detailed setup instructions, see CLAUDE.md")

if __name__ == "__main__":
    main()