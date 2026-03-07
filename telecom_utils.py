import numpy as np
import re
import math

# --- GEOMETRY HELPERS ---
def get_center(bbox):
    return ((bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2)

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
    c1 = get_center(box1)
    c2 = get_center(box2)
    return np.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2)

# --- TEXT PARSING HELPERS ---
def parse_power_data(text):
    """Extracts Voltage (V) and Amperage (A) from OCR text."""
    if not text: return None, None
    # Voltage (e.g., 60V, 90 v)
    volts_match = re.search(r'(\d+)\s*[vV]', text)
    volts = int(volts_match.group(1)) if volts_match else 0
    
    # Amps (e.g., 12.5A, 10 A)
    amps_match = re.search(r'(\d+\.?\d*)\s*[aA]', text)
    amps = float(amps_match.group(1)) if amps_match else 0.0
    return volts, amps

def parse_tap_value(text):
    """Extracts numeric value or handles EQZ cases."""
    if not text: return ""
    # Check for EQZ special case
    if "EQZ" in text.upper() or "CE" in text.upper():
        digits = re.findall(r'\d+', text)
        return f"EQZ-{digits[-1]}" if digits else "EQZ"
    return text

def clean_ocr_text(text, cls_name):
    """Your custom cleaning logic. Ported from process_tiles.py for project-wide consistency."""
    if not text: return ""
    cls_lower = cls_name.lower()
    
    # Specific cleaning for 'Taps'
    if 'tap' in cls_lower:
        # Check for EQZ special cases before heavy cleaning
        upper_text = text.upper()
        is_eqz = "EQZ" in upper_text or "CE" in upper_text
        
        # Translation for common OCR errors
        text = text.translate(str.maketrans("oOlIzZsSgGqQbB", "00112255999966"))
        
        if is_eqz:
            # Preservation for EQZ/CE: Keep keyword + last numeric digits
            digits = re.findall(r'\d+', text)
            prefix = "EQZ" if "EQZ" in upper_text else "CE"
            return f"{prefix}{digits[-1]}" if digits else prefix
            
        numbers = re.findall(r'\d+', text)
        valid_nums = [n for n in numbers if len(n) <= 2]
        if valid_nums:
            res = valid_nums[-1]
            # Handle doubled digits (e.g., "22" -> "2", "66" -> "6")
            if len(res) == 2 and res[0] == res[1] and res[0] in '253689':
                res = res[0]
            return "0" if res == "00" else res
        return ""

    # Specific cleaning for 'Splitters' (Numbers + Dots)
    if 'splitter' in cls_lower:
        text = text.translate(str.maketrans("oOlIzZsSgGbB", "001122559966"))
        numbers = re.findall(r'\d*\.?\d+', text)
        valid_nums = [n for n in numbers if n != '.' and float(n) != 0]
        return valid_nums[-1] if valid_nums else ""

    # Power Supply (Voltage preceding 'V')
    if 'power_supply' in cls_lower:
        match = re.search(r'(\d+)\s*[vV]', text)
        if match:
            return match.group(1)
        # Fallback to standard digits if 'V' is missing but looks like a number
        numbers = re.findall(r'\d+', text)
        return numbers[0] if numbers else ""

    # Tag ID cleaning (translation + longest alphanumeric token)
    if 'tag_id' in cls_lower:
        text = text.translate(str.maketrans("oOlIzZsSgGbB", "001122559966"))
        tokens = text.split()
        valid_tokens = []
        for t in tokens:
             clean_t = re.sub(r'[^a-zA-Z0-9-]', '', t)
             if len(clean_t) >= 1: valid_tokens.append(clean_t)
        return max(valid_tokens, key=len) if valid_tokens else ""

    # General cleaning
    cleaned = re.sub(r'[^a-zA-Z0-9\s.-]', '', text)
    return " ".join(cleaned.split())