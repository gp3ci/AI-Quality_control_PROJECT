import os
import fitz  # PyMuPDF
import cv2
import numpy as np
import argparse
import shutil
import platform
import subprocess

def get_best_corner(page, ss_width_pts, full_overlay_h, margin=30):
    """
    Analyzes the first page to find the corner with the highest average brightness (whitest).
    Returns (x, y, needs_extension) where x,y are coordinates.
    """
    pix = page.get_pixmap(dpi=150) # Increased from 72
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
    
    if pix.n == 4:
        gray = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    h_img, w_img = gray.shape
    
    corners = {
        "TL": (margin, margin),
        "TR": (page.rect.width - ss_width_pts - margin, margin),
        "BL": (margin, page.rect.height - full_overlay_h - margin),
        "BR": (page.rect.width - ss_width_pts - margin, page.rect.height - full_overlay_h - margin)
    }
    
    brightness_vals = {}
    clear_corners = []
    
    threshold = 252 # Very strict white threshold
    
    for name, pos in corners.items():
        scale = 150 / 72
        x1, y1 = max(0, int(pos[0] * scale)), max(0, int(pos[1] * scale))
        x2, y2 = min(w_img, int((pos[0] + ss_width_pts) * scale)), min(h_img, int((pos[1] + full_overlay_h) * scale))
        roi = gray[y1:y2, x1:x2]
        
        if roi.size > 0:
            avg_b = np.mean(roi)
            min_b = np.min(roi)
            brightness_vals[name] = avg_b
            # Corner is clear only if its minimum brightness is high (no dark pixels)
            if min_b >= threshold:
                clear_corners.append(name)
    
    print(f"DEBUG: Corner brightness (avg): {brightness_vals}")
    print(f"DEBUG: Clear corners (min > {threshold}): {clear_corners}")
    
    if not clear_corners:
        print(f"DEBUG: No clear corners found. Triggering map extension.")
        return (margin, -full_overlay_h - margin, True)
    
    # Pick the whitest among the clear corners
    best_corner = max(clear_corners, key=lambda n: brightness_vals[n])
    return (corners[best_corner][0], corners[best_corner][1], False)

def overlay_on_pdf(pdf_path, screenshot_path, prism_id, node_name, instance, output_path):
    print(f"Processing {pdf_path}...")
    doc = fitz.open(pdf_path)
    page_orig = doc[0]
    total_pages = doc.page_count
    
    # 1. Image Dimensions - Huge size to 700
    temp_img = fitz.open(screenshot_path)
    img_rect = temp_img[0].rect
    ss_w_pts = 800 
    ss_h_pts = (img_rect.height / img_rect.width) * ss_w_pts
    temp_img.close()
    
    # 2. Text Preparation
    text_content = (
        f"PID:{prism_id}\n"
        f"NODE:{node_name}\n"
        f"INSTANCE:{instance}\n"
        f"BEFORE PRINT\n"
        f"PG 1 OF {total_pages}"
    )
    
    # Calculate dynamic width & height for font size 24
    font_size = 24 
    max_line_w = 0
    for line in text_content.split('\n'):
        w = fitz.get_text_length(line, fontname="helv", fontsize=font_size)
        if w > max_line_w:
            max_line_w = w
    
    padding_w = 30
    padding_h = 25
    text_box_w = max_line_w + padding_w
    line_height = font_size + 8
    text_box_h = line_height * 5 + padding_h
    
    gap = 10
    full_overlay_h = ss_h_pts + text_box_h + gap
    
    # 3. Find Position on ORIGINAL page dimensions
    startX, startY, extended = get_best_corner(page_orig, ss_w_pts, full_overlay_h)
    
    # Handle Extension if needed
    if extended:
        print("DEBUG: Creating extended page at the top.")
        ext_h = full_overlay_h + 100
        # Create a new document to assist in shifting if needed, or just insert page
        # More reliably: update current page and shift contents
        old_rect = page_orig.rect
        new_height = old_rect.height + ext_h
        
        # Create a new version of the first page with shifted content
        new_doc = fitz.open() # Temporary doc
        new_page = new_doc.new_page(width=old_rect.width, height=new_height)
        new_page.show_pdf_page(fitz.Rect(0, ext_h, old_rect.width, new_height), doc, 0)
        
        # Replace first page in original doc
        doc.delete_page(0)
        doc.insert_pdf(new_doc, from_page=0, to_page=0, start_at=0)
        new_doc.close()
        
        page = doc[0] # The new shifted page
        startX = 30
        startY = 50 
        is_bottom = False
    else:
        page = page_orig
        is_bottom = startY > (page.rect.height / 2)

    # 4. Define Rects based on Layout
    if is_bottom:
        # Box on TOP, Screenshot BELOW
        text_rect = fitz.Rect(startX, startY, startX + text_box_w, startY + text_box_h)
        ss_rect = fitz.Rect(startX, startY + text_box_h + gap, startX + ss_w_pts, startY + text_box_h + gap + ss_h_pts)
    else:
        # Screenshot on TOP, Box BELOW (standard)
        ss_rect = fitz.Rect(startX, startY, startX + ss_w_pts, startY + ss_h_pts)
        text_rect = fitz.Rect(startX, startY + ss_h_pts + gap, startX + text_box_w, startY + ss_h_pts + gap + text_box_h)

    # 5. Insert Screenshot
    page.insert_image(ss_rect, filename=screenshot_path)
    
    # 6. Yellow Text Box with Red Border
    page.draw_rect(text_rect, color=(1, 0, 0), fill=(1, 1, 0), width=2)
    
    # 7. Insert Multi-line Text
    page.insert_textbox(
        text_rect,
        text_content,
        fontsize=font_size,
        fontname="helv",
        color=(0, 0, 0),
        align=0
    )
    
    doc.save(output_path)
    doc.close()
    print(f"✅ Created: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Map Overlay Tool (Core Logic)")
    parser.add_argument("--map", required=True, help="Input Map PDF")
    parser.add_argument("--ss", required=True, help="Screenshot Image")
    parser.add_argument("--prism", required=True, help="Prism ID")
    parser.add_argument("--node", required=True, help="Node Name")
    parser.add_argument("--instance", required=True, help="Instance/Node Details")
    parser.add_argument("--out", default="processed_map.pdf", help="Output filename")
    parser.add_argument("--download", action="store_true", help="Copy output to system Downloads folder")
    parser.add_argument("--open", action="store_true", help="Open the generated PDF automatically")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.map):
        print(f"Error: {args.map} not found.")
        return
    if not os.path.exists(args.ss):
        print(f"Error: {args.ss} not found.")
        return
        
    overlay_on_pdf(args.map, args.ss, args.prism, args.node, args.instance, args.out)

    # Handle Download (Copy to Downloads folder)
    if args.download:
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        if os.path.exists(downloads_path):
            dest = os.path.join(downloads_path, os.path.basename(args.out))
            shutil.copy2(args.out, dest)
            print(f"📥 Copied to Downloads: {dest}")
        else:
            print("Warning: Downloads folder not found.")

    # Handle Open
    if args.open:
        print(f"📖 Opening {args.out}...")
        if platform.system() == "Windows":
            os.startfile(args.out)
        elif platform.system() == "Darwin": # macOS
            subprocess.run(["open", args.out])
        else: # Linux
            subprocess.run(["xdg-open", args.out])

if __name__ == "__main__":
    main()
