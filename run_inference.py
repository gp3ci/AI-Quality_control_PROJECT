import os
import cv2
import numpy as np
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
            
            # Pad if smaller than tile_size (at edges)
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
    base_dir = Path(r"c:/Users/lenovo/Desktop/PROJECTS/Internship-Gp3/fiber_24-01-26")
    test_dir = base_dir / "test"
    output_dir = base_dir / "test_output_obb"
    weights_path = base_dir / "runs/obb/fiber_yolov8l_obb/weights/best.pt"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load Model
    print("Loading model...")
    model = YOLO(weights_path)
    
    # Process "BEFORE FIBER.pdf"
    pdf_path = test_dir / "BEFORE FIBER.pdf"
    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found.")
        return

    print(f"Processing {pdf_path}...")
    
    try:
        # Convert first page to image
        # poppler_path=r"C:\Program Files\poppler-xx\bin" # User might need to set this if not in PATH
        # We assume it's in PATH or installed via conda
        pages = convert_from_path(str(pdf_path), first_page=1, last_page=1, dpi=100)
        image = pages[0]
    except Exception as e:
        print(f"Error converting PDF: {e}")
        print("Ensure 'poppler' is installed and in PATH.")
        print("Windows: download from https://github.com/oschwartz10612/poppler-windows/releases/ and add bin/ to PATH")
        return

    print(f"Image size: {image.size}")
    
    # Create valid filename for output folder
    pdf_name = pdf_path.stem
    save_dir = output_dir / pdf_name
    save_dir.mkdir(exist_ok=True)
    
    # Tile
    print("Tiling...")
    tiles, coords = tile_image(image, tile_size=640, overlap=0.2)
    print(f"Created {len(tiles)} tiles.")
    
    # Predict
    print("Running inference...")
    for i, tile in enumerate(tiles):
        # Convert PIL to cv2 for saving with plot (optional, ultralytics handles PIL)
        # Run inference
        results = model.predict(tile, task='obb', conf=0.25, verbose=False) # Lower conf to see potential detections
        result = results[0]
        
        # Save labeled tile
        # plot() returns a numpy array (BGR)
        im_bgr = result.plot() 
        im_rgb = cv2.cvtColor(im_bgr, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(im_rgb)
        
        tile_name = f"tile_{i}_{coords[i][0]}_{coords[i][1]}.jpg"
        im_pil.save(save_dir / tile_name)
        
        if i % 10 == 0:
            print(f"Processed {i}/{len(tiles)}")
            
    print(f"Done! Results saved to {save_dir}")

if __name__ == "__main__":
    main()
