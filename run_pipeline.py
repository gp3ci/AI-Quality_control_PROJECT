import os
import cv2
import json
import shutil
import argparse
from align_maps import pdf_to_image, align_and_pad_expanded_maps, create_tiles
from telecom_vision import TelecomDetector
from telecom_rules import RuleEngine
from main import match_objects

# --- CONFIG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")
TILES_DIR = os.path.join(BASE_DIR, "tiles")
OUTPUT_FILE = os.path.join(BASE_DIR, "final_report.txt")
DETECTION_IMAGES_DIR = os.path.join(BASE_DIR, "detection_images")
ALL_OCR_JSON_FILE = os.path.join(BASE_DIR, "all_ocr_results.json")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
OCR_TXT_FILE = os.path.join(BASE_DIR, "ocr.txt")

def clean_directory(dir_path):
    """Removes all files in a directory to start fresh."""
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path, exist_ok=True)

def setup_directories():
    """Ensures a clean slate for the current run."""
    print("Setting up clean output directories...")
    clean_directory(os.path.join(TILES_DIR, "before"))
    clean_directory(os.path.join(TILES_DIR, "after"))
    clean_directory(DETECTION_IMAGES_DIR)
    clean_directory(RESULTS_DIR)

def process_pipeline(before_pdf, after_pdf):
    # 0. Setup clean environment
    setup_directories()
    
    # 1. Map Alignment & Tiling
    print("--- STAGE 1: PDF EXTRACTION & ALIGNMENT ---")
    prefix_before = os.path.splitext(os.path.basename(before_pdf))[0]
    prefix_after = os.path.splitext(os.path.basename(after_pdf))[0]

    img_before = pdf_to_image(before_pdf)
    img_after = pdf_to_image(after_pdf)
    
    print("Aligning maps (Universal Canvas)...")
    final_before, final_after = align_and_pad_expanded_maps(img_before, img_after)

    # Temporary save for visualization/debugging of alignment
    cv2.imwrite(os.path.join(BASE_DIR, "ref_before_aligned.png"), final_before)
    cv2.imwrite(os.path.join(BASE_DIR, "ref_after_aligned.png"), final_after)

    print("--- STAGE 2: TILING ---")
    create_tiles(final_before, os.path.join(TILES_DIR, "before"), prefix_before, tile_size=640, overlap=0.2)
    create_tiles(final_after, os.path.join(TILES_DIR, "after"), prefix_after, tile_size=640, overlap=0.2)
    
    # 2. Init AI Models & Rule Engine
    print("--- STAGE 3: MODEL INITIALIZATION ---")
    detector = TelecomDetector(MODEL_PATH)
    engine = RuleEngine()

    # 3. Detect and Evaluate
    print("--- STAGE 4: INFERENCE, OCR & BUSINESS LOGIC ---")
    after_root = os.path.join(TILES_DIR, "after")
    before_root = os.path.join(TILES_DIR, "before")
    
    pairs = []
    if os.path.exists(after_root):
        for f in sorted(os.listdir(after_root)):
            if f.endswith(('.png', '.jpg')):
                after_path = os.path.join(after_root, f)
                before_name = f.replace(prefix_after, prefix_before)
                before_path = os.path.join(before_root, before_name)
                if os.path.exists(before_path):
                    pairs.append((before_path, after_path))

    print(f"Found {len(pairs)} synchronized tile pairs. Processing...")

    all_ocr_data = {}
    
    with open(OUTPUT_FILE, 'w') as f_out, open(OCR_TXT_FILE, 'w') as f_ocr:
        f_ocr.write("OCR DETECTION REPORT\n" + "="*20 + "\n\n")
        
        for before_path, after_path in pairs:
            name = os.path.basename(after_path)
            
            img_b = cv2.imread(before_path)
            img_a = cv2.imread(after_path)
            if img_b is None or img_a is None: continue

            # 3.1 DETECTION & OCR (Confidence tuned to 0.25)
            objs_b = detector.detect_objects(img_b, conf_threshold=0.25)
            objs_a = detector.detect_objects(img_a, conf_threshold=0.25)
            
            objs_b = detector.run_ocr_on_objects(img_b, objs_b)
            objs_a = detector.run_ocr_on_objects(img_a, objs_a)
            
            all_ocr_data[name] = {"before_map": objs_b, "after_map": objs_a}
            
            # Write to ocr.txt
            f_ocr.write(f"--- TILE: {name} ---\nBEFORE MAP:\n")
            if not objs_b: f_ocr.write("  (No detections)\n")
            for obj in objs_b:
                f_ocr.write(f"  - [{obj['cls']}] Confidence: {obj['conf']:.2f} | OCR: '{obj.get('text', '')}'\n")
            
            f_ocr.write("AFTER MAP:\n")
            if not objs_a: f_ocr.write("  (No detections)\n")
            for obj in objs_a:
                f_ocr.write(f"  - [{obj['cls']}] Confidence: {obj['conf']:.2f} | OCR: '{obj.get('text', '')}'\n")
            f_ocr.write("\n")

            # 3.4 MATCHING & RULES
            matches, removed, added = match_objects(objs_b, objs_a)
            callouts = engine.generate_callouts(matches, removed, added)

            # 3.3. VISUAL DEBUG SAVES (Enabled by default in original method)
            img_b_vis = img_b.copy()
            img_a_vis = img_a.copy()
            for obj in objs_b:
                x1, y1, x2, y2 = [int(v) for v in obj['bbox']]
                cv2.rectangle(img_b_vis, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(img_b_vis, f"{obj['cls']} {obj.get('text', '')}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

            for obj in objs_a:
                x1, y1, x2, y2 = [int(v) for v in obj['bbox']]
                cv2.rectangle(img_a_vis, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(img_a_vis, f"{obj['cls']} {obj.get('text', '')}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                
            cv2.imwrite(os.path.join(DETECTION_IMAGES_DIR, f"DETECTIONS_BEFORE_{name}"), img_b_vis)
            cv2.imwrite(os.path.join(DETECTION_IMAGES_DIR, f"DETECTIONS_AFTER_{name}"), img_a_vis)
            
            # 3.5 REPORTING & ANNOTATION
            if callouts:
                f_out.write(f"\n--- TILE: {name} ---\n")
                for c in callouts:
                    line = f"TILE: {name} | LOC: {c['loc']} | CALLOUT: {c['text']} ({c['desc']}) | DETECTED BY: {c.get('model', 'unknown')}"
                    f_out.write(line + "\n")
                    print(line)
                    
                    # Annotate image
                    cv2.rectangle(img_a, (c['loc'][0], c['loc'][1]-10), (c['loc'][0]+200, c['loc'][1]), (0,0,0), -1)
                    cv2.putText(img_a, c['text'], (c['loc'][0], c['loc'][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                
                cv2.imwrite(os.path.join(RESULTS_DIR, f"result_{name}"), img_a)

    # 5. Final Aggregation
    print("--- STAGE 5: FINALIZING DATA ---")
    with open(ALL_OCR_JSON_FILE, 'w') as f_json:
        json.dump(all_ocr_data, f_json, indent=4)

    print(f"\n✅ PIPELINE COMPLETE. Report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="End-to-End Coax Rule Engine Pipeline")
    parser.add_argument('--before', type=str, required=True, help="Path to Before PDF")
    parser.add_argument('--after', type=str, required=True, help="Path to After PDF")
    
    args = parser.parse_args()
    process_pipeline(args.before, args.after)
