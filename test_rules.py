from telecom_rules import RuleEngine
from telecom_utils import clean_ocr_text, get_center

def test_ocr_clean():
    print("Testing OCR Cleaning...")
    res = clean_ocr_text("00", "Taps")
    print(f"  '00' -> '{res}' (Expected: '0')")
    assert res == "0"

def test_amp_rules():
    print("\nTesting Amplifier Rules (Callout A - After Map Only)...")
    engine = RuleEngine()
    
    # Case 1: Dual Amplifier in BEFORE only (Should NOT trigger A)
    amp_b = {'bbox': [100, 100, 150, 150], 'cls': 'amplifier_dual', 'conf': 0.9}
    callouts = engine.generate_callouts([], [amp_b], [])
    found = [c['text'] for c in callouts if 'A' == c['text']]
    print(f"  Dual Amp in Before only: {found} (Expected: [])")

    # Case 2: Dual Amplifier in AFTER (Addition)
    amp_a = {'bbox': [200, 200, 250, 250], 'cls': 'amplifier_dual', 'conf': 0.9}
    callouts = engine.generate_callouts([], [], [amp_a])
    found = [c['text'] for c in callouts if 'A' == c['text']]
    print(f"  Dual Amp in After: {found} (Expected: ['A'])")

    # Case 3: 3-Way Amplifier in AFTER (Match)
    amp_3w_b = {'bbox': [300, 300, 350, 350], 'cls': 'amplifier_3way', 'conf': 0.9}
    amp_3w_a = {'bbox': [300, 300, 350, 350], 'cls': 'amplifier_3way', 'conf': 0.9}
    callouts = engine.generate_callouts([(amp_3w_b, amp_3w_a)], [], [])
    found = [c['text'] for c in callouts if 'A' == c['text']]
    print(f"  3-Way Amp Match: {found} (Expected: ['A'])")
    
    # Case 4: Generic 'Amplifier' type in AFTER (Should NOT trigger A if not dual/3way)
    amp_gen = {'bbox': [400, 400, 450, 450], 'cls': 'amplifier', 'conf': 0.9}
    callouts = engine.generate_callouts([], [], [amp_gen])
    found = [c['text'] for c in callouts if 'A' == c['text']]
    print(f"  Generic Amp in After: {found} (Expected: [])")

def test_h_rules():
    print("\nTesting Callout H (Boosters/LE Addition)...")
    engine = RuleEngine()
    
    booster = {'bbox': [300, 300, 350, 350], 'cls': 'booster', 'conf': 0.9}
    callouts = engine.generate_callouts([], [], [booster])
    found = [c['text'] for c in callouts if 'H' == c['text']]
    print(f"  New Booster: {found} (Expected: ['H'])")

    le = {'bbox': [400, 400, 450, 450], 'cls': 'line_extender', 'conf': 0.9}
    callouts = engine.generate_callouts([], [], [le])
    found = [c['text'] for c in callouts if 'H' == c['text']]
    print(f"  New LE: {found} (Expected: ['H'])")

if __name__ == "__main__":
    test_ocr_clean()
    test_amp_rules()
    test_h_rules()
