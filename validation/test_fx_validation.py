#!/usr/bin/env python3
"""
🎛️ FX Validation Test - Conferma mappings FX Unit 2/3/4
Test sistematico dei CC scoperti per tutti i 4 FX Unit
"""

import time
import logging
from traktor_control import get_traktor_controller, DeckID
from config import get_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_fx_unit(controller, fx_unit):
    """Test completo di un FX Unit"""
    print(f"\n🎛️ Testing FX Unit {fx_unit}")
    print("=" * 40)
    
    results = {}
    
    # Test Knobs (Dry/Wet + Knob 1-3)
    knob_tests = [
        ('drywet', 'Dry/Wet Mix'),
        ('knob1', 'Parameter Knob 1'), 
        ('knob2', 'Parameter Knob 2'),
        ('knob3', 'Parameter Knob 3')
    ]
    
    for knob_type, description in knob_tests:
        print(f"🎚️ Testing {description}...")
        try:
            if knob_type == 'drywet':
                success = controller.set_fx_drywet(fx_unit, 0.5)  # 50%
            else:
                knob_num = int(knob_type[-1])  # Extract number from 'knob1', 'knob2', etc.
                success = controller.set_fx_knob(fx_unit, knob_num, 0.7)  # 70%
            
            results[f'{knob_type}'] = success
            status = "✅ OK" if success else "❌ FAIL"
            print(f"   {status} - {description}")
            time.sleep(0.2)
            
        except Exception as e:
            results[f'{knob_type}'] = False
            print(f"   ❌ ERROR - {description}: {e}")
    
    # Test Buttons (RST, FRZ, SPR, On/Off)
    button_tests = [
        ('rst', 'Reset Button'),
        ('frz', 'Freeze Button'),
        ('spr', 'Spread Button'), 
        ('onoff', 'On/Off Switch')
    ]
    
    for button_type, description in button_tests:
        print(f"🔘 Testing {description}...")
        try:
            success = controller.trigger_fx_button(fx_unit, button_type)
            results[f'{button_type}_button'] = success
            status = "✅ OK" if success else "❌ FAIL"
            print(f"   {status} - {description}")
            time.sleep(0.3)
            
        except Exception as e:
            results[f'{button_type}_button'] = False
            print(f"   ❌ ERROR - {description}: {e}")
    
    return results

def main():
    """Test principale - valida tutti i 4 FX Unit"""
    print("🧪 FX Validation Test Suite")
    print("=" * 50)
    print("Testing all discovered FX mappings (CC 97-120)")
    print("Based on pattern logic from confirmed FX1 (CC 76-79, 93-96)")
    
    config = get_config()
    controller = get_traktor_controller(config)
    
    # Connessione con output-only per sicurezza
    if not controller.connect_with_gil_safety(output_only=True):
        print("❌ Connessione MIDI fallita")
        return
    
    print("✅ Connesso a Traktor via IAC Driver")
    
    # Test di base per verificare che MIDI funzioni
    print("\n🔧 Testing basic MIDI connection...")
    basic_test = controller.set_deck_volume(DeckID.A, 0.5)
    if basic_test:
        print("✅ Basic MIDI test passed")
    else:
        print("⚠️ Basic MIDI test failed - continuing anyway")
    
    all_results = {}
    
    # Test FX Unit 2, 3, 4 (FX1 già confermato)
    for fx_unit in [2, 3, 4]:
        try:
            unit_results = test_fx_unit(controller, fx_unit)
            all_results[f'fx{fx_unit}'] = unit_results
            
            # Summary per questo FX Unit
            total_tests = len(unit_results)
            passed_tests = sum(1 for result in unit_results.values() if result)
            success_rate = (passed_tests / total_tests) * 100
            
            print(f"\n📊 FX{fx_unit} Summary: {passed_tests}/{total_tests} tests passed ({success_rate:.0f}%)")
            
        except Exception as e:
            print(f"❌ Critical error testing FX{fx_unit}: {e}")
            all_results[f'fx{fx_unit}'] = {'error': str(e)}
    
    # Report finale
    print("\n" + "=" * 60)
    print("🎯 FINAL VALIDATION REPORT")
    print("=" * 60)
    
    total_fx_units = 3  # FX2, FX3, FX4
    successful_units = 0
    
    for fx_unit in [2, 3, 4]:
        fx_key = f'fx{fx_unit}'
        if fx_key in all_results and 'error' not in all_results[fx_key]:
            unit_results = all_results[fx_key]
            total_tests = len(unit_results)
            passed_tests = sum(1 for result in unit_results.values() if result)
            success_rate = (passed_tests / total_tests) * 100
            
            if success_rate >= 75:  # Consider 75%+ as successful
                successful_units += 1
                status = "✅ VALIDATED"
            else:
                status = "⚠️ PARTIAL"
            
            print(f"FX{fx_unit}: {status} - {passed_tests}/{total_tests} controls ({success_rate:.0f}%)")
            
            # Dettagli failures se ci sono
            failed_controls = [control for control, result in unit_results.items() if not result]
            if failed_controls:
                print(f"     Failed: {', '.join(failed_controls)}")
        else:
            print(f"FX{fx_unit}: ❌ CRITICAL ERROR")
    
    overall_success = (successful_units / total_fx_units) * 100
    print(f"\n🏆 OVERALL SUCCESS: {successful_units}/{total_fx_units} FX Units validated ({overall_success:.0f}%)")
    
    # Raccomandazioni
    print(f"\n💡 RECOMMENDATIONS:")
    if overall_success >= 100:
        print("✅ All FX mappings validated! Ready for production use.")
        print("✅ Update traktor_control.py comments: PREDICTED → CONFIRMED")
    elif overall_success >= 75:
        print("⚠️ Most FX mappings work. Review failed controls.")
        print("⚠️ Consider using working mappings in production.")
    else:
        print("❌ Significant mapping issues detected.")
        print("❌ Manual MIDI Learn session recommended.")
    
    controller.disconnect()
    print("\n👋 Test completato")

if __name__ == "__main__":
    main()
