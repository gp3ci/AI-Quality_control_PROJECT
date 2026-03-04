import os
import xml.etree.ElementTree as ET
import shutil
import random
import math
from pathlib import Path

def convert_bbox(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)

def main():
    base_dir = Path(r"c:/Users/lenovo/Desktop/PROJECTS/Internship-Gp3/fiber_24-01-26")
    dataset_dir = base_dir / "dataset"
    output_dir = base_dir / "yolo_dataset"
    
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
                # Fix path: dataset/1/annotations.xml refers to "before/Pilot...", but file is likely at "dataset/1/Pilot..."
                # We stick to the basename
                filename = os.path.basename(file_name_attr)
                
                # Check for file existence
                src_image_path = folder_path / filename
                if not src_image_path.exists():
                    print(f"Warning: Image {filename} not found in {folder_path}")
                    continue
                    
                width = int(image.get('width'))
                height = int(image.get('height'))
                
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
                        # Handle rotation if present to get accurate AABB
                        rotation = float(box.get('rotation', 0))
                        xtl = float(box.get('xtl'))
                        ytl = float(box.get('ytl'))
                        xbr = float(box.get('xbr'))
                        ybr = float(box.get('ybr'))

                        if rotation != 0:
                            # Calculate corners of the rotated box
                            width_box = xbr - xtl
                            height_box = ybr - ytl
                            cx = xtl + width_box / 2.0
                            cy = ytl + height_box / 2.0
                            
                            # Define corners relative to center
                            fw = width_box / 2.0
                            fh = height_box / 2.0
                            corners = [(-fw, -fh), (fw, -fh), (fw, fh), (-fw, fh)]
                            
                            # Rotate corners
                            angle_rad = math.radians(rotation)
                            cos_a = math.cos(angle_rad)
                            sin_a = math.sin(angle_rad)
                            
                            rotated_corners = []
                            for px, py in corners:
                                nx = px * cos_a - py * sin_a
                                ny = px * sin_a + py * cos_a
                                rotated_corners.append((cx + nx, cy + ny))
                            
                            # Find AABB of the rotated box
                            xs = [pt[0] for pt in rotated_corners]
                            ys = [pt[1] for pt in rotated_corners]
                            xtl = min(xs)
                            xbr = max(xs)
                            ytl = min(ys)
                            ybr = max(ys)
                            
                            # Clamp to image boundaries
                            xtl = max(0, xtl)
                            ytl = max(0, ytl)
                            xbr = min(width, xbr)
                            ybr = min(height, ybr)

                        b = (xtl, xbr, ytl, ybr)
                        bb = convert_bbox((width, height), b)
                        
                        out_f.write(f"{cls_id} {bb[0]:.6f} {bb[1]:.6f} {bb[2]:.6f} {bb[3]:.6f}\n")

        process_images(train_images, "train")
        process_images(val_images, "val")
        
    print("Conversion completed successfully!")

if __name__ == "__main__":
    main()
