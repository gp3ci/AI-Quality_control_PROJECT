import os
import cv2
import numpy as np
import argparse
from pathlib import Path
from pdf2image import convert_from_path
from ultralytics import YOLO
from PIL import Image

def tile_image(image, tile_size=640, overlap=0.2):
    """
    Split image into tiles with overlap.
    """
    img_w, img_h = image.size
    stride = int(tile_size * (1 - overlap))
    
    tiles = []
    coords = [] # (x, y)
    
    y = 0
    while y < img_h:
        x = 0
        while x < img_w:
            # Crop
            box = (x, y, x + tile_size, y + tile_size)
            tile = image.crop(box)
            
            # Pad if smaller than tile_size
            if tile.size != (tile_size, tile_size):
                new_tile = Image.new("RGB", (tile_size, tile_size), (255, 255, 255))
                new_tile.paste(tile, (0, 0))
                tile = new_tile
                
            tiles.append(tile)
            coords.append((x, y))
            
            x += stride
        y += stride
        
    return tiles, coords

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dpi', type=int, default=200, help='DPI for PDF conversion')
    parser.add_argument('--tile_size', type=int, default=640, help='Tile crop size')
    parser.add_argument('--conf', type=float, default=0.25, help='Confidence threshold')
    args = parser.parse_args()

    base_dir = Path(r"c:/Users/lenovo/Desktop/PROJECTS/Internship-Gp3/fiber_24-01-26")
    test_dir = base_dir / "test"
    # Create distinct output folder for this run setting
    run_name = f"dpi{args.dpi}_tile{args.tile_size}_conf{args.conf}"
    output_dir = base_dir / "test_output_obb" / run_name
    weights_path = base_dir / "runs/obb/fiber_yolov8l_obb/weights/best.pt"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"--- Starting Inference Debug Run: {run_name} ---")
    print(f"DPI: {args.dpi}, Tile Size: {args.tile_size}, Conf: {args.conf}")

    # Load Model
    model = YOLO(weights_path)
    
    # Process "BEFORE FIBER.pdf"
    pdf_path = test_dir / "BEFORE FIBER.pdf"
    
    try:
        print("Converting PDF...")
        pages = convert_from_path(str(pdf_path), first_page=1, last_page=1, dpi=args.dpi)
        image = pages[0]
    except Exception as e:
        print(f"Error converting PDF: {e}")
        return

    print(f"Image size: {image.size}")
    
    # Tile
    print("Tiling...")
    # NOTE: We keep overlap proportional, or fixed? Let's use 20%
    tiles, coords = tile_image(image, tile_size=args.tile_size, overlap=0.2)
    print(f"Created {len(tiles)} tiles.")
    
    # Predict
    print("Running inference...")
    detections_count = 0
    for i, tile in enumerate(tiles):
        # Resize tile if it's not 640x640 (YOLO will do this internally, but good to know)
        # We pass the raw cropped tile (e.g. 1024x1024) to YOLO. 
        # YOLOv8 default imgsz is 640. It will resize 1024->640 (zoom out).
        
        results = model.predict(tile, task='obb', conf=args.conf, verbose=False, imgsz=640) 
        result = results[0]
        
        if len(result.obb) > 0:
            detections_count += len(result.obb)
            # Save nicely labeled tile ONLY if detections found (to save space/time checking)
            im_bgr = result.plot() 
            im_rgb = cv2.cvtColor(im_bgr, cv2.COLOR_BGR2RGB)
            im_pil = Image.fromarray(im_rgb)
            
            tile_name = f"tile_{i}_det_{len(result.obb)}.jpg"
            im_pil.save(output_dir / tile_name)
    
    print(f"Total Detections: {detections_count}")
    print(f"Results saved to {output_dir}")

if __name__ == "__main__":
    main()
