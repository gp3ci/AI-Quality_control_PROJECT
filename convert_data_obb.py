import os
import xml.etree.ElementTree as ET
import shutil
import random
import math
from pathlib import Path

def rotate_point(cx, cy, x, y, angle_degree):
    """
    Rotate point (x,y) around (cx,cy) by angle_degree (clockwise).
    """
    angle_rad = math.radians(angle_degree)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    
    # Translate point to origin (relative to center)
    tx = x - cx
    ty = y - cy
    
    # Rotate
    # Standard formula for clockwise rotation in image coordinates (y-axis down)
    # x' = x*cos - y*sin
    # y' = x*sin + y*cos
    nx = tx * cos_a - ty * sin_a
    ny = tx * sin_a + ty * cos_a
    
    # Translate back
    return cx + nx, cy + ny

def get_obb_coords(box):
    """
    Calculate 4 corners of the rotated box.
    box: tuple (xtl, ytl, xbr, ybr, rotation)
    """
    xtl, ytl, xbr, ybr, rotation = box
    width = xbr - xtl
    height = ybr - ytl
    cx = xtl + width / 2.0
    cy = ytl + height / 2.0
    
    # Unrotated corners
    # TL, TR, BR, BL
    corners = [
        (cx - width/2, cy - height/2),
        (cx + width/2, cy - height/2),
        (cx + width/2, cy + height/2),
        (cx - width/2, cy + height/2)
    ]
    
    rotated_corners = []
    for x, y in corners:
        rx, ry = rotate_point(cx, cy, x, y, rotation)
        rotated_corners.append((rx, ry))
        
    return rotated_corners

def main():
    base_dir = Path(r"c:/Users/lenovo/Desktop/PROJECTS/Internship-Gp3/fiber_24-01-26")
    dataset_dir = base_dir / "dataset"
    output_dir = base_dir / "yolo_obb_dataset"
    
    # Classes mapping
    classes = {'Splice_can': 0, 'Node': 1}
    
    if output_dir.exists():
        shutil.rmtree(output_dir)
    
    # Create directories
    (output_dir / "images" / "train").mkdir(parents=True, exist_ok=True)
    (output_dir / "images" / "val").mkdir(parents=True, exist_ok=True)
    (output_dir / "labels" / "train").mkdir(parents=True, exist_ok=True)
    (output_dir / "labels" / "val").mkdir(parents=True, exist_ok=True)

    # Process all subfolders dynamically
    subfolders = [f.name for f in dataset_dir.iterdir() if f.is_dir()]
    print(f"Found {len(subfolders)} subfolders in dataset: {subfolders}")
    
    for folder in subfolders:
        folder_path = dataset_dir / folder
        xml_file = folder_path / "annotations.xml"
        
        if not xml_file.exists():
            print(f"Warning: Annotations file not found in {folder_path}")
            continue
            
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        images = []
        for image in root.findall('image'):
            images.append(image)
        
        # Shuffle and split
        random.shuffle(images)
        split_idx = int(len(images) * 0.8)
        train_images = images[:split_idx]
        val_images = images[split_idx:]
        
        def process_images(image_list, split_name):
            for image in image_list:
                file_name_attr = image.get('name')
                filename = os.path.basename(file_name_attr)
                
                src_image_path = folder_path / filename
                if not src_image_path.exists():
                    print(f"Warning: Image {filename} not found in {folder_path}")
                    continue
                    
                width = float(image.get('width'))
                height = float(image.get('height'))
                
                # Copy image
                dst_image_path = output_dir / "images" / split_name / filename
                shutil.copy(src_image_path, dst_image_path)
                
                # Create label file
                label_file = output_dir / "labels" / split_name / f"{Path(filename).stem}.txt"
                
                with open(label_file, 'w') as out_f:
                    for box in image.findall('box'):
                        label = box.get('label')
                        if label not in classes:
                            continue
                            
                        cls_id = classes[label]
                        xtl = float(box.get('xtl'))
                        ytl = float(box.get('ytl'))
                        xbr = float(box.get('xbr'))
                        ybr = float(box.get('ybr'))
                        # Default rotation to 0 if not present
                        rotation = float(box.get('rotation', 0))
                        
                        corners = get_obb_coords((xtl, ytl, xbr, ybr, rotation))
                        
                        # Normalize coordinates
                        flat_coords = []
                        for x, y in corners:
                            # Clamp values to be within image? YOLO OBB usually handles slight OOB, 
                            # but safer to keep normalized 0-1.
                            nx = max(0, min(1, x / width))
                            ny = max(0, min(1, y / height))
                            # Actually, for OBB, values can slightly exceed 0-1 if rotation pushes corner out,
                            # but usually we normalize strictly. Let's just normalize directly.
                            nx = x / width
                            ny = y / height
                            flat_coords.extend([f"{nx:.6f}", f"{ny:.6f}"])
                            
                        # Format: class x1 y1 x2 y2 x3 y3 x4 y4
                        coord_str = " ".join(flat_coords)
                        out_f.write(f"{cls_id} {coord_str}\n")

        process_images(train_images, "train")
        process_images(val_images, "val")
        
    print("OBB Conversion completed successfully!")

if __name__ == "__main__":
    main()
