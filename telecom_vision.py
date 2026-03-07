import cv2
import numpy as np
import os
from ultralytics import YOLO
import easyocr
from telecom_utils import clean_ocr_text

class TelecomDetector:
    def __init__(self, model_path, gpu=True):
        print(f"Loading YOLO from {model_path}...")
        self.model = YOLO(model_path)
        
        ps_model_path = os.path.join(os.path.dirname(model_path), "power_supply_best.pt")
        print(f"Loading Power Supply YOLO from {ps_model_path}...")
        self.ps_model = YOLO(ps_model_path)
        
        node_model_path = os.path.join(os.path.dirname(model_path), "3x3_4x4_new_model.pt")
        print(f"Loading Nodes YOLO from {node_model_path}...")
        self.node_model = YOLO(node_model_path)
        
        print("Loading EasyOCR...")
        self.reader = easyocr.Reader(['en'], gpu=gpu)
        # Configuration
        self.ROI_PADDING = 0.15
        self.SKIP_CENTER_CROP = ['tag_id', 'power_supply']

    def detect_objects(self, img, conf_threshold=0.05):
        """Runs YOLO detection (Supports OBB)."""
        h, w = img.shape[:2]
        final_objects = []

        # Helper to parse box
        def parse_box(box, is_obb):
            if is_obb:
                x, y, w_b, h_b, r = box.xywhr[0].cpu().numpy()
                x1 = int(x - w_b/2)
                y1 = int(y - h_b/2)
                x2 = int(x + w_b/2)
                y2 = int(y + h_b/2)
            else:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            x1, y1 = int(max(0, x1)), int(max(0, y1))
            x2, y2 = int(min(w, x2)), int(min(h, y2))
            return [x1, y1, x2, y2]
            
        def process_results(results, model, allowed_classes=None, blocked_classes=None, model_name=""):
            objs = []
            det_list = []
            is_obb = False
            if hasattr(results, 'obb') and results.obb is not None and len(results.obb) > 0:
                 det_list, is_obb = results.obb, True
            elif hasattr(results, 'boxes') and results.boxes is not None and len(results.boxes) > 0:
                det_list = results.boxes
                
            for box in det_list:
                cls_id = int(box.cls[0])
                cls_name = model.names[cls_id].lower()
                
                # Apply class filters
                if allowed_classes and not any(a in cls_name for a in allowed_classes):
                    continue
                if blocked_classes and any(b in cls_name for b in blocked_classes):
                    continue
                    
                bbox = parse_box(box, is_obb)
                
                # Rule compatibility: legacy rules look for "node" inside node names "node_4x4", etc.
                if any(x in cls_name for x in ['1x4', '2x2', '3x3', '4x4']) and 'node' not in cls_name:
                    if '1x4' in cls_name:
                        cls_name = "node_1x1"
                    else:
                        cls_name = f"node_{cls_name}"
                    
                objs.append({
                    'bbox': bbox,
                    'cls': cls_name,
                    'conf': float(box.conf[0]),
                    'text': '',
                    'model': model_name
                })
            return objs

        # 1. Main Model (best.pt) -> Everything EXCEPT nodes and power blocks
        results_main = self.model(img, verbose=False, conf=conf_threshold)[0]
        # Restrict best.pt: Do NOT include nodes or power_block
        objs_main = process_results(results_main, self.model, blocked_classes=['node', 'power_block'], model_name='best.pt')

        # 2. Power Supply Model -> ONLY Power Blocks
        results_ps = self.ps_model(img, verbose=False, conf=0.51)[0]
        # Restrict ps_model: ONLY allow power_block
        objs_ps = process_results(results_ps, self.ps_model, allowed_classes=['power_block'], model_name='power_supply_best.pt')

        # 3. Node Model -> ONLY Nodes (1x1, 2x2, 3x3, 4x4)
        results_node = self.node_model(img, verbose=False, conf=conf_threshold)[0]
        # Restrict node_model: ONLY allow node classes
        objs_node = process_results(results_node, self.node_model, allowed_classes=['node'], model_name='3x3_4x4_new_model.pt')

        final_objects = []
        final_objects.extend(objs_node)
        final_objects.extend(objs_ps)
        final_objects.extend(objs_main)

        # 4. Filter objects based on new rules
        filtered_final = []
        margin_x = int(w * 0.05)
        margin_y = int(h * 0.05)

        for obj in final_objects:
            cls_lower = obj['cls'].lower()
            x1, y1, x2, y2 = obj['bbox']
            
            # Rule: Node-related classes confidence thresholds
            if 'node' in cls_lower:
                # 1x1 node (includes 1x4 from main model mapped to node_1x1) threshold 0.85
                if '1x1' in cls_lower:
                    if obj['conf'] < 0.85:
                        continue
                # Other nodes threshold 0.8
                elif obj['conf'] < 0.8:
                    continue
            
            # Rule: Line Extender threshold >= 0.15
            if 'line_extender' in cls_lower and obj['conf'] < 0.15:
                continue

            # Rule: Tap confidence >= 0.5 (Detect all taps)
            if 'tap' in cls_lower and obj['conf'] < 0.5:
                continue

            # Rule: Splitter confidence >= 0.15 (Adjusted for better recall)
            if 'splitter' in cls_lower and obj['conf'] < 0.15:
                continue

            # Rule: Tap and Splitter boundary filtering (ignore partials)
               # Ignore partials near image borders (within 15 pixels)
                edge_padding = 15
                if x1 < edge_padding or y1 < edge_padding or x2 > (w - edge_padding) or y2 > (h - edge_padding):
                    continue
                if (x2 - x1) < 15 or (y2 - y1) < 15:
                    continue
                
                # Minimal BBox padding (5-8 pixels or 5%) to avoid nearby text
                pad = max(5, int(min(x2-x1, y2-y1) * 0.05))
                # Cap at 8 pixels as requested
                pad = min(pad, 8)
                
                x1, y1 = max(0, x1 - pad), max(0, y1 - pad)
                x2, y2 = min(w, x2 + pad), min(h, y2 + pad)
                obj['bbox'] = [x1, y1, x2, y2]
            
            filtered_final.append(obj)
            
        return filtered_final

    def run_ocr_on_objects(self, img, objects):
        """Iterates through detected objects and adds OCR text."""
        for obj in objects:
            cls_name = obj['cls'].lower()
            # Skip classes that don't need OCR to save time
            if not any(x in cls_name for x in ['tap', 'splitter', 'power_supply', 'node', 'tag_id']):
                continue
            
            # Special Rule: Only trigger OCR for Taps if detection confidence > 0.7
            if 'tap' in cls_name and obj['conf'] < 0.7:
                continue
               
            raw_text = self._extract_text_from_roi(img, obj['bbox'], obj['cls'])
            obj['text'] = raw_text
        return objects

    def _extract_text_from_roi(self, image, bbox, cls_name):
        """
        Refined OCR Pipeline: Minimal BBox -> White Border -> Multi-Preprocessing (Gray, Otsu, Adaptive, Opened) -> Voting.
        """
        import collections
        x1, y1, x2, y2 = bbox
        h_img, w_img = image.shape[:2]
        
        # 1. Crop ROI (BBox minimal padding applied in detect_objects)
        crop = image[y1:y2, x1:x2]
        if crop.size == 0: return ""

        # 2. Add White Border Padding (5-10 pixels as requested)
        # Gives OCR margin without including external objects
        border = 10
        crop = cv2.copyMakeBorder(crop, border, border, border, border, 
                                 cv2.BORDER_CONSTANT, value=[255, 255, 255])

        # 3. Normalize ROI Size and Scale
        # Resize to a consistent baseline (e.g., 128x128) to stabilize OCR
        # Then upscale 3x using BICUBIC interpolation to help with thin/small digits
        h_r, w_r = crop.shape[:2]
        target_size = 128
        # Maintain aspect ratio while resizing to target_size
        scale_to_target = target_size / max(h_r, w_r)
        crop = cv2.resize(crop, None, fx=scale_to_target, fy=scale_to_target, interpolation=cv2.INTER_CUBIC)
        
        # 3x Bicubic scaling for small digits
        crop = cv2.resize(crop, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        
        # Variation 1: Straight Grayscale (inverted for white-on-black maps if needed, but usually black-on-white)
        # Variation 2: Gaussian Blur + Otsu Threshold
        blurred_g = cv2.GaussianBlur(gray, (5, 5), 0)
        _, otsu = cv2.threshold(blurred_g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Variation 3: Median Blur + Adaptive Threshold
        blurred_m = cv2.medianBlur(gray, 3)
        adaptive = cv2.adaptiveThreshold(blurred_m, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # Variation 4: Morphological Opening (Remove small noise)
        kernel = np.ones((3,3), np.uint8)
        opening = cv2.morphologyEx(otsu, cv2.MORPH_OPEN, kernel)
        
        # Variation 5: CLAHE (Contrast Enhancement)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        cl1 = clahe.apply(gray)
        
        # Variation 6: Sharpening kernel
        kernel_sharpen = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(gray, -1, kernel_sharpen)

        variations = [
            ("Grayscale", cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)),
            ("Otsu", cv2.cvtColor(otsu, cv2.COLOR_GRAY2RGB)),
            ("Adaptive", cv2.cvtColor(adaptive, cv2.COLOR_GRAY2RGB)),
            ("Opening", cv2.cvtColor(opening, cv2.COLOR_GRAY2RGB)),
            ("CLAHE", cv2.cvtColor(cl1, cv2.COLOR_GRAY2RGB)),
            ("Sharpened", cv2.cvtColor(sharpened, cv2.COLOR_GRAY2RGB))
        ]

        # 4. Configure OCR & collect results
        is_numeric = any(x in cls_name.lower() for x in ['tap', 'splitter'])
        allowlist = '0123456789' if is_numeric else None
        
        results = []
        for name, v_img in variations:
            try:
                # detail=1 to get bounding box, text, and confidence
                res = self.reader.readtext(v_img, detail=1, allowlist=allowlist)
                if res:
                    # res format: [([[x,y],...], text, confidence), ...]
                    valid_texts = []
                    for (bbox_ocr, text, conf) in res:
                        cls_name_low = cls_name.lower()
                        # Apply confidence threshold: 0.8 for 'tap', 0.2 for 'splitter'
                        # Note: Tap detection thresh check is already in run_ocr_on_objects
                        if 'tap' in cls_name_low and conf < 0.8:
                            continue
                        if 'splitter' in cls_name_low and conf < 0.2:
                            continue

                        # Boundary Alignment Check for Taps
                        # If digits are touching the original boundary of the shape, ignore them.
                        if 'tap' in cls_name_low:
                            # bbox_ocr coordinates are in the 3x scaled + bordered image
                            # The original crop was bordered by 'border' pixels before scaling.
                            # So the original ROI in the scaled image starts at border_scaled.
                            border_scaled = border * scale_to_target * 3
                            h_scaled, w_scaled = v_img.shape[:2]
                            
                            # Flatten coordinates
                            coords = np.array(bbox_ocr)
                            xmin, ymin = np.min(coords, axis=0)
                            xmax, ymax = np.max(coords, axis=0)

                            # If it touches or is extremely close to the edge of the original content ROI
                            # (The ROI starts at border_scaled and ends at w_scaled - border_scaled)
                            # We use a threshold of 3 pixels in the 3x-upscaled image to detect "touching"
                            edge_thresh = 3 
                            if (xmin < (border_scaled + edge_thresh) or 
                                ymin < (border_scaled + edge_thresh) or 
                                xmax > (w_scaled - border_scaled - edge_thresh) or 
                                ymax > (h_scaled - border_scaled - edge_thresh)):
                                continue
                               
                        valid_texts.append(text)
                   
                    if valid_texts:
                        txt = " ".join(valid_texts)
                        clean = clean_ocr_text(txt, cls_name)
                        if clean:
                            results.append(clean)
            except Exception as e:
                continue

        # 5. Majority Voting and Validation
        if not results:
            return ""
            
        counts = collections.Counter(results)
        # Get the most common result
        best_pick, count = counts.most_common(1)[0]
        
        # If numeric and we have a tie with a non-zero, prefer the non-zero result if count matches
        if is_numeric and best_pick == '0' and len(counts) > 1:
            for val, c in counts.most_common():
                if val != '0' and c == count:
                    return val

        return best_pick
