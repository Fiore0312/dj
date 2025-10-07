#!/usr/bin/env python3
"""
🛠️ VISUAL NAVIGATION SETUP - Dependency Installer
=================================================

Setup script for the Enhanced Visual Browser Agent that:
1. Checks for required Python libraries
2. Installs missing dependencies
3. Verifies tesseract OCR installation
4. Tests basic functionality
5. Provides setup recommendations

Run this before using the Jazz folder challenge or visual browser agent.
"""

import subprocess
import sys
import platform
import os
from typing import List, Tuple

def print_header():
    """Print setup header"""
    print("🛠️" * 40)
    print("🛠️ VISUAL BROWSER NAVIGATION SETUP")
    print("🛠️ Enhanced Visual Browser Agent")
    print("🛠️" * 40)
    print()

def check_python_version() -> bool:
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ required")
        return False

    print("✅ Python version compatible")
    return True

def check_and_install_packages() -> bool:
    """Check and install required Python packages"""
    print("\n📦 CHECKING PYTHON PACKAGES")
    print("-" * 40)

    required_packages = [
        ("opencv-python", "cv2"),
        ("Pillow", "PIL"),
        ("numpy", "numpy"),
        ("pytesseract", "pytesseract"),
    ]

    missing_packages = []

    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - MISSING")
            missing_packages.append(package_name)

    if missing_packages:
        print(f"\n📥 Installing missing packages: {', '.join(missing_packages)}")

        for package in missing_packages:
            try:
                print(f"   Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"   ✅ {package} installed")
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Failed to install {package}: {e}")
                return False

        print("✅ All packages installed successfully")

    return True

def check_tesseract_installation() -> bool:
    """Check tesseract OCR installation"""
    print("\n🔍 CHECKING TESSERACT OCR")
    print("-" * 30)

    try:
        import pytesseract

        # Try to get tesseract version
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR v{version} found")

        # Test basic functionality
        from PIL import Image
        import numpy as np

        # Create a test image with text
        test_img = np.ones((100, 300, 3), dtype=np.uint8) * 255  # White background
        test_pil = Image.fromarray(test_img)

        # Try OCR (this might fail on empty image, but tests the pipeline)
        try:
            pytesseract.image_to_string(test_pil)
            print("✅ Tesseract OCR pipeline working")
        except Exception as ocr_e:
            print(f"⚠️ Tesseract OCR test warning: {ocr_e}")
            print("   (This may be normal for empty test image)")

        return True

    except ImportError:
        print("❌ pytesseract not available")
        return False

    except Exception as e:
        print(f"❌ Tesseract OCR error: {e}")
        print("\n💡 TESSERACT INSTALLATION HELP:")

        system = platform.system().lower()
        if system == "darwin":  # macOS
            print("   For macOS: brew install tesseract")
        elif system == "linux":
            print("   For Ubuntu/Debian: sudo apt-get install tesseract-ocr")
            print("   For CentOS/RHEL: sudo yum install tesseract")
        elif system == "windows":
            print("   For Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
            print("   Add tesseract to PATH environment variable")

        return False

def test_basic_functionality() -> bool:
    """Test basic visual navigation functionality"""
    print("\n🧪 TESTING BASIC FUNCTIONALITY")
    print("-" * 35)

    try:
        # Test PIL screenshot
        from PIL import ImageGrab
        screenshot = ImageGrab.grab(bbox=(0, 0, 100, 100))
        print("✅ PIL screenshot working")

        # Test OpenCV
        import cv2
        import numpy as np
        test_array = np.array(screenshot)
        test_cv = cv2.cvtColor(test_array, cv2.COLOR_RGB2BGR)
        print("✅ OpenCV conversion working")

        # Test OCR pipeline
        import pytesseract
        # Simple OCR test (may return empty for no text, but tests pipeline)
        pytesseract.image_to_string(screenshot)
        print("✅ OCR pipeline working")

        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def check_midi_prerequisites() -> bool:
    """Check MIDI prerequisites"""
    print("\n🎵 CHECKING MIDI PREREQUISITES")
    print("-" * 35)

    try:
        # Check if project's traktor_control is available
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from core.traktor_control import TraktorController
        print("✅ TraktorController available")

        # Check for rtmidi or mido
        try:
            import rtmidi
            print("✅ rtmidi available")
        except ImportError:
            try:
                import mido
                print("✅ mido available")
            except ImportError:
                print("⚠️ No MIDI library found (rtmidi or mido recommended)")

        return True

    except ImportError as e:
        print(f"❌ MIDI prerequisites missing: {e}")
        print("💡 Make sure you're running from the correct project directory")
        return False

def provide_usage_instructions():
    """Provide usage instructions"""
    print(f"\n🚀 USAGE INSTRUCTIONS")
    print("=" * 25)
    print()
    print("1. QUICK TEST:")
    print("   python tools/quick_visual_test.py")
    print("   └ Test screenshot, OCR, and navigation")
    print()
    print("2. JAZZ FOLDER CHALLENGE:")
    print("   python tools/jazz_folder_challenge.py")
    print("   └ Full autonomous navigation demo")
    print()
    print("3. INTEGRATION:")
    print("   from agents.enhanced_visual_browser_agent import EnhancedVisualBrowserAgent")
    print("   └ Use in your own scripts")
    print()
    print("📋 REQUIREMENTS FOR SUCCESS:")
    print("   ✓ Traktor Pro 3 running")
    print("   ✓ Browser window visible")
    print("   ✓ IAC Driver configured")
    print("   ✓ Folder names visible in browser tree")
    print()
    print("🛠️ TROUBLESHOOTING:")
    print("   • Check browser area coordinates (x,y,w,h)")
    print("   • Verify MIDI connection")
    print("   • Adjust OCR confidence thresholds")
    print("   • Enable debug screenshots for visual feedback")

def main():
    """Main setup execution"""
    print_header()

    success_steps = []

    # Check Python version
    success_steps.append(check_python_version())

    # Check and install packages
    if success_steps[-1]:
        success_steps.append(check_and_install_packages())

    # Check tesseract
    if success_steps[-1]:
        success_steps.append(check_tesseract_installation())

    # Test basic functionality
    if success_steps[-1]:
        success_steps.append(test_basic_functionality())

    # Check MIDI prerequisites
    if success_steps[-1]:
        success_steps.append(check_midi_prerequisites())

    # Final results
    print("\n📊 SETUP RESULTS")
    print("=" * 20)

    all_success = all(success_steps)

    if all_success:
        print("🏆 SETUP COMPLETE - ALL SYSTEMS GO!")
        print("✅ Visual Browser Navigation Agent ready")
        provide_usage_instructions()
    else:
        print("❌ SETUP INCOMPLETE")
        print("💡 Please resolve the issues above before proceeding")

        failed_steps = sum(1 for success in success_steps if not success)
        print(f"📊 {len(success_steps) - failed_steps}/{len(success_steps)} components ready")

    return all_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)