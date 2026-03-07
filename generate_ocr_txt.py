import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "all_ocr_results.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "ocr.txt")

def generate():
    if not os.path.exists(JSON_FILE):
        print(f"Error: {JSON_FILE} not found. Please run the pipeline first.")
        return

    print(f"Reading {JSON_FILE}...")
    with open(JSON_FILE, 'r') as f:
        data = json.load(f)

    print(f"Writing to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f_out:
        f_out.write("OCR DETECTION REPORT (Generated from JSON)\n")
        f_out.write("="*40 + "\n\n")

        for tile_name, results in data.items():
            f_out.write(f"--- TILE: {tile_name} ---\n")
            
            f_out.write("BEFORE MAP:\n")
            objs_b = results.get("before_map", [])
            if not objs_b:
                f_out.write("  (No detections)\n")
            for obj in objs_b:
                f_out.write(f"  - [{obj['cls']}] Conf: {obj['conf']:.2f} | OCR: '{obj.get('text', '')}'\n")
            
            f_out.write("AFTER MAP:\n")
            objs_a = results.get("after_map", [])
            if not objs_a:
                f_out.write("  (No detections)\n")
            for obj in objs_a:
                f_out.write(f"  - [{obj['cls']}] Conf: {obj['conf']:.2f} | OCR: '{obj.get('text', '')}'\n")
            
            f_out.write("\n")

    print("Done! ocr.txt has been created.")

if __name__ == "__main__":
    generate()
