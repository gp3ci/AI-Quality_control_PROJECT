import os
import cv2
import collections
from ultralytics import YOLO
import easyocr
import numpy as np
import re
import sys

# --- Configuration ---
# Use paths relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")
TILES_DIR = os.path.join(BASE_DIR, "tiles")
OUTPUT_FILE = os.path.join(BASE_DIR, "doc.txt")
DEBUG_CROPS_DIR = os.path.join(BASE_DIR, "debug_crops_processed")

# Thresholds
IOU_THRESHOLD = 0.3  
CONF_THRESHOLD = 0.05 
BOUNDARY_MARGIN = 0 
MAX_BOX_AREA_RATIO = 0.5 
DISTANCE_THRESHOLD = 150 # Pixels
ROI_PADDING = 0.15 
MIN_OCR_CONF = 0.0 # Handled by logic

# --- TEST MODE CONFIG ---
TEST_MODE = True
TARGET_TILE = "after8_54.png"
# ------------------------

# Included classes for filtering (optional, if commented out in process_image then shows all)
INCLUDED_CLASSES = [
    'Taps', 'Splitter_DC', 'Splitter_int_DC', 'power_supply'
]

# --- Classes to SKIP center cropping ---
SKIP_CENTER_CROP_CLASSES = ['Tag_id', 'power_supply']
# ---------------------------------------

# --- Helper Functions ---

def clean_text(text, cls_name):
    """
    Clean OCR text based on class.
    """
    if not text: return ""
    cls_lower = cls_name.lower()
    
    # Specific cleaning for 'Taps' (Numbers only)
    if 'tap' in cls_lower:
        text = text.replace('o', '0').replace('O', '0').replace('l', '1').replace('I', '1').replace('z', '2').replace('Z', '2').replace('s', '5').replace('S', '5').replace('g', '9').replace('G', '9').replace('b', '6').replace('B', '6')
        numbers = re.findall(r'\d+', text)
        valid_nums = [n for n in numbers if len(n) <= 2]
        return valid_nums[-1] if valid_nums else ""

    # Specific cleaning for 'Splitters' (Numbers + Dots)
    if 'splitter' in cls_lower:
        text = text.replace('o', '0').replace('O', '0').replace('l', '1').replace('I', '1').replace('z', '2').replace('Z', '2').replace('s', '5').replace('S', '5').replace('g', '9').replace('G', '9').replace('b', '6').replace('B', '6')
        numbers = re.findall(r'\d*\.?\d+', text)
        valid_nums = []
        for n in numbers:
            if n == '.': continue
            try:
                val = float(n)
                if val == 0: continue
                valid_nums.append(n)
            except: continue
        return valid_nums[-1] if valid_nums else ""

    # power_supply voltage (Preceding digits of 'V')
    if 'power_supply' in cls_lower:
        match = re.search(r'(\d+)\s*[vV]', text)
        if match:
            return match.group(1)
        # Fallback to standard digits if 'V' is missing but looks like a number
        numbers = re.findall(r'\d+', text)
        return numbers[0] if numbers else ""

    # Tag ID cleaning
    if 'tag_id' in cls_lower:
        text = text.replace('o', '0').replace('O', '0').replace('l', '1').replace('I', '1').replace('z', '2').replace('Z', '2').replace('s', '5').replace('S', '5').replace('g', '9').replace('G', '9').replace('b', '6').replace('B', '6')
        tokens = text.split()
        valid_tokens = []
        for t in tokens:
             clean_t = re.sub(r'[^a-zA-Z0-9-]', '', t)
             if len(clean_t) >= 1: valid_tokens.append(clean_t)
        return max(valid_tokens, key=len) if valid_tokens else ""

    # General cleaning
    cleaned = re.sub(r'[^a-zA-Z0-9\s.-]', '', text)
    return " ".join(cleaned.split())

def is_yellow_box(image, bbox):
    """Check for yellow color to identify Tag_ID."""
    x1, y1, x2, y2 = bbox
    roi = image[y1:y2, x1:x2]
    if roi.size == 0: return False
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    lower_yellow = np.array([15, 40, 40])
    upper_yellow = np.array([45, 255, 255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    return (np.sum(mask > 0) / mask.size) > 0.05

def extract_text_from_roi(image, bbox, reader, cls_name, debug_id=""):
    """
    Perform Advanced OCR with Multi-Pass Preprocessing, Center Crop, and Upscaling.
    """
    x1, y1, x2, y2 = bbox
    h_img, w_img = image.shape[:2]
    
    # Padding
    pad_pct = ROI_PADDING
    pad_x = int((x2 - x1) * pad_pct)
    pad_y = int((y2 - y1) * pad_pct)
    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(w_img, x2 + pad_x)
    y2 = min(h_img, y2 + pad_y)
    
    if x2 <= x1 or y2 <= y1: return ""
    
    # 1. Crop from original CLEAN image
    crop_original = image[y1:y2, x1:x2]
    
    # 2. Center Crop (50%) - Applied to ALL classes now for better isolation
    # Skip for Tag_id and other items in SKIP_CENTER_CROP_CLASSES
    if cls_name not in SKIP_CENTER_CROP_CLASSES:
        h_r, w_r = crop_original.shape[:2]
        crop_ratio = 0.45 # Keep central 50%
        cx, cy = w_r // 2, h_r // 2
        w_crop, h_crop = int(w_r * crop_ratio), int(h_r * crop_ratio)
        
        sx = max(0, cx - w_crop // 2)
        sy = max(0, cy - h_crop // 2)
        ex = min(w_r, cx + w_crop // 2)
        ey = min(h_r, cy + h_crop // 2)
        
        if w_crop > 0 and h_crop > 0:
            crop_original = crop_original[sy:ey, sx:ex]
    else:
        # print(f"  Skipping center crop for {cls_name}")
        pass
    # ---------------------------------------
    
    # 3. Dynamic Upscaling
    h_r, w_r = crop_original.shape[:2]
    scale_factor = 3
    min_height = 64
    if h_r < min_height:
        temp_scale = min_height / h_r
        scale_factor = max(scale_factor, temp_scale)
    
    scale_factor = max(4, scale_factor) # Minimum 4x scale
    
    crop_scaled = cv2.resize(crop_original, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
    
    # 4. Variations
    # Normal
    gray = cv2.cvtColor(crop_scaled, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    gray_clahe = clahe.apply(gray)
    img_normal = cv2.cvtColor(gray_clahe, cv2.COLOR_GRAY2BGR)
    
    # Inverted
    gray_inv = cv2.bitwise_not(gray_clahe)
    img_inv = cv2.cvtColor(gray_inv, cv2.COLOR_GRAY2BGR)
    
    # Otsu
    _, gray_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    img_otsu = cv2.cvtColor(gray_otsu, cv2.COLOR_GRAY2BGR)
    
    # Denoised
    img_denoised_gray = cv2.fastNlMeansDenoising(gray_clahe, None, 10, 7, 21)
    img_denoised = cv2.cvtColor(img_denoised_gray, cv2.COLOR_GRAY2BGR)
    
    # Sharpened
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    img_sharpened_gray = cv2.filter2D(gray_clahe, -1, kernel)
    img_sharpened = cv2.cvtColor(img_sharpened_gray, cv2.COLOR_GRAY2BGR)
    
    # Adaptive
    img_adaptive_gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    img_adaptive = cv2.cvtColor(img_adaptive_gray, cv2.COLOR_GRAY2BGR)

    variations = [
        ("Normal", img_normal), ("Inverted", img_inv), ("Otsu", img_otsu),
        ("Denoised", img_denoised), ("Sharpened", img_sharpened), ("Adaptive", img_adaptive)
    ]
    
    # Save debug crop if enabled
    if DEBUG_CROPS_DIR:
        os.makedirs(DEBUG_CROPS_DIR, exist_ok=True)
        cv2.imwrite(os.path.join(DEBUG_CROPS_DIR, f"{debug_id}_{cls_name}.png"), crop_original)

    # 5. Run EasyOCR
    candidates = []
    for v_name, v_img in variations:
        try:
            v_img_rgb = cv2.cvtColor(v_img, cv2.COLOR_BGR2RGB)
            res = reader.readtext(v_img_rgb, detail=0)
            if res:
                txt = " ".join(res)
                cln = clean_text(txt, cls_name)
                score = 0
                if cln: score += 100
                if txt: score += len(txt)
                candidates.append({"raw": txt, "clean": cln, "score": score})
        except: pass
        
    if candidates:
        best = max(candidates, key=lambda x: x['score'])
        return best['clean']
    
    return ""

def calculate_iou(box1, box2):
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2
    x_inter_min = max(x1_min, x2_min)
    y_inter_min = max(y1_min, y2_min)
    x_inter_max = min(x1_max, x2_max)
    y_inter_max = min(y1_max, y2_max)
    if x_inter_max < x_inter_min or y_inter_max < y_inter_min: return 0.0
    intersection_area = (x_inter_max - x_inter_min) * (y_inter_max - y_inter_min)
    box1_area = (x1_max - x1_min) * (y1_max - y1_min)
    box2_area = (x2_max - x2_min) * (y2_max - y2_min)
    union_area = box1_area + box2_area - intersection_area
    if union_area == 0: return 0.0
    return intersection_area / union_area

def calculate_distance(box1, box2):
    c1 = ((box1[0]+box1[2])/2, (box1[1]+box1[3])/2)
    c2 = ((box2[0]+box2[2])/2, (box2[1]+box2[3])/2)
    return np.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2)

def process_image(img, model):
    """Run YOLO on an image and return list of objects (supports OBB)."""
    # Debug: Verbose=True to see if YOLO finds anything
    # Lower conf to 0.05 to capture more objects than default 0.25
    results = model(img, verbose=True, conf=0.05)[0]
    objects = []
    h, w = img.shape[:2]
    
    # Handle OBB (Oriented Bounding Box) models
    det_list = []
    is_obb = False
    
    if hasattr(results, 'obb') and results.obb is not None:
         # Check length? OBB object might be iterable directly
         if len(results.obb) > 0:
             det_list = results.obb
             is_obb = True
    elif results.boxes is not None and len(results.boxes) > 0:
        det_list = results.boxes
    
    if not det_list:
        # Try checking boxes again just in case (sometimes mapped differently)
        if results.boxes is not None and len(results.boxes) > 0:
             det_list = results.boxes
        else:
             print("  No boxes (OBB or HBB) in raw detection.")
             return objects
        
    print(f"  Raw boxes found: {len(det_list)}")
    
    for box in det_list:
        cls_id = int(box.cls[0])
        cls_name = model.names[cls_id]
        
        # Get AABB (Axis Aligned Bounding Box) [x1, y1, x2, y2]
        if is_obb:
             try:
                # Attempt to access standard xyxy if available
                # If not, use xywhr center
                # Standard OBB object in new ultralytics might have .xyxy calculated?
                if hasattr(box, 'xyxy'):
                     x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                else:
                    x, y, w_b, h_b, r = box.xywhr[0].cpu().numpy()
                    x1 = int(x - w_b/2)
                    y1 = int(y - h_b/2)
                    x2 = int(x + w_b/2)
                    y2 = int(y + h_b/2)
             except: continue
        else:
            # HBB
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        # Filter size
        if ((x2-x1)*(y2-y1)) / (h*w) > MAX_BOX_AREA_RATIO: continue
        
        # --- REMOVED YELLOW LOGIC TO MATCH test_model.py ---
        # is_yellow = is_yellow_box(img, [x1, y1, x2, y2])
        # if cls_name.lower() == 'tag_id' and not is_yellow: continue
        # if is_yellow: cls_name = 'Tag_id'
        
        # Filter classes based on INCLUDED_CLASSES
        allowed_classes = [c.lower() for c in INCLUDED_CLASSES]
        if cls_name.lower() not in allowed_classes and cls_name != 'Tag_id':
             continue

        objects.append({
            'bbox': [x1, y1, x2, y2],
            'cls': cls_name,
            'conf': float(box.conf[0])
        })
    
    print(f"  Final objects: {len(objects)}")
    return objects

def main():
    print("Loading YOLO model...")
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model not found at {MODEL_PATH}")
        return
    model = YOLO(MODEL_PATH)
    print(f"Model classes: {model.names}")
    
    print("Initializing EasyOCR...")
    reader = easyocr.Reader(['en'], gpu=True)
    
    print("Identifying tiles...")
    # Group logic: Assuming folders like 'X_before' and 'X_after' 
    # OR strictly paired files within same structure. 
    # Based on user request: "folders tiles/after/COAX AFTER_65.png"
    
    # We will search specifically for the 'after' folder and look for corresponding 'before' folder/files
    # Assuming standard structure: tiles/after/ROOT... and tiles/before/ROOT...
    
    after_root = os.path.join(TILES_DIR, "after")
    before_root = os.path.join(TILES_DIR, "before")
    
    if not os.path.exists(after_root):
        print(f"Error: 'after' directory not found at {after_root}")
        # Fallback to recursively finding 'after' dirs if structure is different
        return

    # Gather After files
    # We walk to find all images in 'after'
    pairs = []
    for root, dirs, files in os.walk(after_root):
        for f in files:
            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                after_path = os.path.join(root, f)
                rel_path = os.path.relpath(after_path, after_root)
                
                # Construct Before path
                # Try simple replacement output "AFTER" -> "BEFORE" in filename
                f_before = f.replace("AFTER", "BEFORE").replace("after", "before")
                
                # Check directly in 'before' root with same relative path structure?
                # Or just assume flat 'before' folder?
                # Let's try matching relative structure first
                before_path_cand = os.path.join(before_root, os.path.dirname(rel_path), f_before)
                
                if os.path.exists(before_path_cand):
                    pairs.append((before_path_cand, after_path))
                else:
                    # Try non-replaced filename in before folder
                    before_path_cand_2 = os.path.join(before_root, os.path.dirname(rel_path), f)
                    if os.path.exists(before_path_cand_2):
                        pairs.append((before_path_cand_2, after_path))

    # --- FILTER FOR SINGLE TILE TEST ---
    if TEST_MODE:
        filtered_pairs = [p for p in pairs if TARGET_TILE.lower() == os.path.basename(p[1]).lower()]
        if filtered_pairs:
            print(f"Test Mode: Restricting to {len(filtered_pairs)} pair(s) matching '{TARGET_TILE}'")
            pairs = filtered_pairs
        else:
            print(f"Warning: Target tile '{TARGET_TILE}' not found in pairs. Trying partial match...")
            filtered_pairs = [p for p in pairs if TARGET_TILE.lower() in os.path.basename(p[1]).lower()]
            if filtered_pairs:
                 pairs = filtered_pairs
                 print(f"Test Mode: Found {len(pairs)} partial matches for '{TARGET_TILE}'")
            else:
                 print("Available pairs (first 5):")
                 for p in pairs[:5]: print(os.path.basename(p[1]))
                 return    
    # -----------------------------------
            
    print(f"Found {len(pairs)} Before/After pairs.")
    
    with open(OUTPUT_FILE, 'w') as f_out:
        f_out.write("Comparison Report\n=================\n\n")
        f_out.flush()
        
        for i, (before_path, after_path) in enumerate(pairs):
            name = os.path.basename(after_path)
            
            # --- CONSOLE REPORT HEADER ---
            print(f"\n{'='*40}")
            print(f"COMPARING: {name}")
            print(f"{'='*40}")
            
            f_out.write(f"--- Comparison: {name} ---\n")
            f_out.flush() 
            
            img_b = cv2.imread(before_path)
            img_a = cv2.imread(after_path)
            
            if img_b is None:
                print(f"Error reading Before: {before_path}")
                continue
            if img_a is None:
                print(f"Error reading After: {after_path}")
                continue
            
            objs_b = process_image(img_b, model)
            objs_a = process_image(img_a, model)
            
            # OCR for all objects
            for o in objs_b:
                o['text'] = extract_text_from_roi(img_b, o['bbox'], reader, o['cls'], "B_"+name)
            for o in objs_a:
                o['text'] = extract_text_from_roi(img_a, o['bbox'], reader, o['cls'], "A_"+name)
                
            # Matching
            matched_b = set()
            matches = [] 
            
            # 1. Try Position Match
            for ib, ob in enumerate(objs_b):
                best_match = None
                best_score = float('inf') 
                best_iou = 0
                match_idx = -1
                
                for ia, oa in enumerate(objs_a):
                     iou = calculate_iou(ob['bbox'], oa['bbox'])
                     if iou > IOU_THRESHOLD:
                         if iou > best_iou:
                             best_iou = iou
                             match_idx = ia
                
                if match_idx != -1:
                    matches.append((ob, objs_a[match_idx]))
                    objs_a[match_idx]['matched'] = True
                    matched_b.add(ib)
                    continue

                for ia, oa in enumerate(objs_a):
                    if oa.get('matched'): continue
                    if oa['cls'] != ob['cls']: continue 
                    dist = calculate_distance(ob['bbox'], oa['bbox'])
                    if dist < DISTANCE_THRESHOLD:
                         if dist < best_score:
                            best_score = dist
                            best_match = oa
                            match_idx = ia
                
                if best_match:
                    matches.append((ob, best_match))
                    objs_a[match_idx]['matched'] = True
                    matched_b.add(ib)
            
            # REPORTING (Console & File)
            # Create a list of all items to report
            report_items = []

            # 1. Matched Objects (Both Changed and Unchanged)
            for ob, oa in matches:
                status = "SAME"
                val_b = ob.get('text', '')
                val_a = oa.get('text', '')
                
                # Check specifics
                changes = []
                if val_b != val_a:
                    status = "CHANGED"
                    if ob['cls'].lower() == 'power_supply':
                        changes.append(f"Voltage change")
                    else:
                        changes.append(f"Val changed")
                
                # Pos check
                cb = ((ob['bbox'][0]+ob['bbox'][2])//2, (ob['bbox'][1]+ob['bbox'][3])//2)
                ca = ((oa['bbox'][0]+oa['bbox'][2])//2, (oa['bbox'][1]+oa['bbox'][3])//2)
                dist = np.sqrt((cb[0]-ca[0])**2 + (cb[1]-ca[1])**2)
                if dist > 20: 
                    if status == "SAME": status = "MOVED"
                    else: status += "+MOVED"
                
                report_items.append({
                    'cls': ob['cls'],
                    'status': status,
                    'val_b': val_b,
                    'val_a': val_a,
                    'details': ", ".join(changes) if changes else ""
                })

            # 2. Removed Objects (In Before, not matched in After)
            for ib, ob in enumerate(objs_b):
                if ib not in matched_b:
                    report_items.append({
                        'cls': ob['cls'],
                        'status': "REMOVED",
                        'val_b': ob.get('text', ''),
                        'val_a': "-",
                        'details': "Not in After"
                    })

            # 3. New Objects (In After, not matched)
            for oa in objs_a:
                if not oa.get('matched'):
                    report_items.append({
                        'cls': oa['cls'],
                        'status': "NEW",
                        'val_b': "-",
                        'val_a': oa.get('text', ''),
                        'details': "Not in Before"
                    })
            
            # Print Table
            # Header
            header = f"{'CLASS':<20} | {'STATUS':<15} | {'BEFORE VAL':<15} | {'AFTER VAL':<15} | {'DETAILS'}"
            sep = "-" * len(header)
            
            print(header)
            print(sep)
            f_out.write(header + "\n")
            f_out.write(sep + "\n")
            
            for item in report_items:
                line = f"{item['cls']:<20} | {item['status']:<15} | {item['val_b']:<15} | {item['val_a']:<15} | {item['details']}"
                print(line)
                f_out.write(line + "\n")
            
            f_out.flush()
            print("\n")
            
    print(f"Done. Report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
