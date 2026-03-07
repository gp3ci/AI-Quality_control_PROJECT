import os
import cv2
import json
import collections
from telecom_vision import TelecomDetector
from telecom_rules import RuleEngine
from telecom_utils import calculate_iou, calculate_distance

# --- CONFIG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")
TILES_DIR = os.path.join(BASE_DIR, "tiles")
OUTPUT_FILE = os.path.join(BASE_DIR, "final_report.txt")
DETECTION_IMAGES_DIR = os.path.join(BASE_DIR, "detection_images")
ALL_OCR_JSON_FILE = os.path.join(BASE_DIR, "all_ocr_results.json")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

# Create output dirs if needed
os.makedirs(DETECTION_IMAGES_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

def match_objects(objs_b, objs_a, threshold_dist=150, iou_thresh=0.5):
    """Pairs objects based on IOU and Distance."""
    matches = []
    matched_b_indices = set()
    
    # Tag matches in After list
    for oa in objs_a: oa['matched'] = False

    # 1. Try IOU Match (Strongest)
    for ib, ob in enumerate(objs_b):
        best_match_idx = -1
        best_iou = 0
        
        for ia, oa in enumerate(objs_a):
            if oa['matched']: continue
            iou = calculate_iou(ob['bbox'], oa['bbox'])
            if iou > iou_thresh and iou > best_iou:
                best_iou = iou
                best_match_idx = ia
        
        if best_match_idx != -1:
            matches.append((ob, objs_a[best_match_idx]))
            objs_a[best_match_idx]['matched'] = True
            matched_b_indices.add(ib)

    # 2. Try Distance Match (Fallback)
    for ib, ob in enumerate(objs_b):
        if ib in matched_b_indices: continue
        
        best_match_idx = -1
        min_dist = float('inf')
        
        for ia, oa in enumerate(objs_a):
            if oa['matched']: continue
            # Only match similar classes for distance fallback, or both are nodes
            is_node_b = 'node' in ob['cls'].lower()
            is_node_a = 'node' in oa['cls'].lower()
            if not (is_node_b and is_node_a) and ob['cls'] != oa['cls']: continue
            
            dist = calculate_distance(ob['bbox'], oa['bbox'])
            if dist < threshold_dist and dist < min_dist:
                min_dist = dist
                best_match_idx = ia
                
        if best_match_idx != -1:
            matches.append((ob, objs_a[best_match_idx]))
            objs_a[best_match_idx]['matched'] = True
            matched_b_indices.add(ib)

    # Separate Lists
    removed = [objs_b[i] for i in range(len(objs_b)) if i not in matched_b_indices]
    added = [oa for oa in objs_a if not oa['matched']]
    
    return matches, removed, added

def main():
    # 1. INIT
    detector = TelecomDetector(MODEL_PATH)
    engine = RuleEngine()
    
    # 2. FILE PAIRING LOGIC (Simulated for modularity)
    # Ensure you have 'before' and 'after' folders in 'tiles'
    after_root = os.path.join(TILES_DIR, "after")
    before_root = os.path.join(TILES_DIR, "before")
    
    pairs = []
    if os.path.exists(after_root):
        for f in os.listdir(after_root):
            if f.endswith(('.png', '.jpg')):
                after_path = os.path.join(after_root, f)
                # Naive matching: assumes filename matches or replaces 'AFTER' with 'BEFORE'
                before_name = f.replace("AFTER", "BEFORE").replace("after", "before")
                before_path = os.path.join(before_root, before_name)
                if os.path.exists(before_path):
                    pairs.append((before_path, after_path))

    print(f"Found {len(pairs)} pairs to process.")

    with open(OUTPUT_FILE, 'w') as f_out:
        all_ocr_data = {}
        for before_path, after_path in pairs:
            name = os.path.basename(after_path)
            print(f"Processing: {name}")
            
            img_b = cv2.imread(before_path)
            img_a = cv2.imread(after_path)
            
            # 3. DETECTION & OCR
            objs_b = detector.detect_objects(img_b, conf_threshold=0.25)
            objs_a = detector.detect_objects(img_a, conf_threshold=0.25)
            
            objs_b = detector.run_ocr_on_objects(img_b, objs_b)
            objs_a = detector.run_ocr_on_objects(img_a, objs_a)
            
            # --- OVERRIDE/ADDITION: SAVE TO JSON ---
            ocr_doc = {
                "before_map": objs_b,
                "after_map": objs_a
            }
            all_ocr_data[name] = ocr_doc
            
            # --- SAVE VISUAL DETECTIONS ---
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
            print(f"Saved detection images for {name} to {DETECTION_IMAGES_DIR}")
            
            # 4. MATCHING
            matches, removed, added = match_objects(objs_b, objs_a)
            
            # 5. RULE ENGINE
            callouts = engine.generate_callouts(matches, removed, added)
            
            # 6. REPORTING
            f_out.write(f"\n--- MAP: {name} ---\n")
            for c in callouts:
                line = f"LOC: {c['loc']} | CALLOUT: {c['text']} ({c['desc']}) | DETECTED BY: {c.get('model', 'unknown')}"
                print(line)
                f_out.write(line + "\n")
                
                # Annotate Image
                cv2.rectangle(img_a, (c['loc'][0], c['loc'][1]-10), (c['loc'][0]+200, c['loc'][1]), (0,0,0), -1)
                cv2.putText(img_a, c['text'], (c['loc'][0], c['loc'][1]), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Save Debug Image
            cv2.imwrite(os.path.join(RESULTS_DIR, f"result_{name}"), img_a)

    # Dump consolidated OCR
    with open(ALL_OCR_JSON_FILE, 'w') as f_json:
        json.dump(all_ocr_data, f_json, indent=4)
        print(f"Consolidated OCR data saved to {ALL_OCR_JSON_FILE}")

    print(f"Complete. Report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()