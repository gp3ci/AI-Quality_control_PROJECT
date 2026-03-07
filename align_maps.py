import cv2
import numpy as np
import fitz  # PyMuPDF
import os

def pdf_to_image(pdf_path, dpi=600):
    """
    Converts the first page of a PDF to a numpy image (BGR).
    """
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)  # Load first page
    pix = page.get_pixmap(dpi=dpi)
    img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
    if pix.n == 4: # RGBA to RGB
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
    elif pix.n == 3: # RGB to BGR
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    return img_array

def align_and_pad_expanded_maps(img_before, img_after):
    """
    Aligns and pads maps using a multi-resolution approach to save memory at high DPI.
    """
    print("Detecting features (Downsampled phase)...")
    
    # 0. Multi-Resolution Strategy
    # We downsample the images to calculate the alignment (Homography) 
    # and then apply that transformation back to the full-resolution images.
    h1, w1 = img_before.shape[:2]
    h2, w2 = img_after.shape[:2]
    
    # Target alignment resolution around 1500px wide
    scale_1 = 1500.0 / w1
    scale_2 = 1500.0 / w2
    
    img_before_small = cv2.resize(img_before, (0, 0), fx=scale_1, fy=scale_1)
    img_after_small = cv2.resize(img_after, (0, 0), fx=scale_2, fy=scale_2)

    # 1. Detect Features using SIFT on small images
    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(img_before_small, None)
    kp2, des2 = sift.detectAndCompute(img_after_small, None)

    # 2. Match Features
    print("Matching features...")
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    good = [m for m, n in matches if m.distance < 0.7 * n.distance]
    print(f"Good matches found: {len(good)}")

    if len(good) > 10:
        # Extract points in small coordinate space
        src_pts_small = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts_small = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        # 3. Calculate Transformation on small space
        M_small, mask = cv2.findHomography(dst_pts_small, src_pts_small, cv2.RANSAC, 5.0)
        
        # 4. Rescale Homography for native resolution
        # To get M_native:
        # 1. Scale After back to native: S_after_inv = diag(1/scale_2, 1/scale_2, 1)
        # 2. Apply M_small
        # 3. Scale Before to native: S_before_inv = diag(1/scale_1, 1/scale_1, 1)
        
        S_inv_before = np.diag([1.0/scale_1, 1.0/scale_1, 1.0])
        S_after = np.diag([scale_2, scale_2, 1.0])
        M = S_inv_before @ M_small @ S_after
        
        print(f"Homography Matrix Calculated (Rescaled to Native).", flush=True)

        # 5. Determine Universal Canvas Size (Native Resolution)
        corners_after = np.float32([[0, 0], [0, h2], [w2, h2], [w2, 0]]).reshape(-1, 1, 2)
        transformed_corners = cv2.perspectiveTransform(corners_after, M)

        all_corners = np.concatenate(([[0, 0], [0, h1], [w1, h1], [w1, 0]], 
                                       transformed_corners.reshape(-1, 2)), axis=0)
        [x_min, y_min] = np.int32(all_corners.min(axis=0) - 0.5)
        [x_max, y_max] = np.int32(all_corners.max(axis=0) + 0.5)

        # 6. मास्टर कनवस (Master Canvas) Translation
        translation_dist = [-x_min, -y_min]
        H_translation = np.array([[1, 0, translation_dist[0]], [0, 1, translation_dist[1]], [0, 0, 1]], dtype=np.float32)

        output_size = (x_max - x_min, y_max - y_min)
        print(f"Calculated Universal Canvas Size: {output_size}", flush=True)
        
        # Extended Safety Check
        if output_size[0] > 25000 or output_size[1] > 25000:
             print(f"WARNING: Output size {output_size} is critically large! Risk of memory error.", flush=True)

        print(f"Warping to Universal Canvas size: {output_size}...", flush=True)
        
        # Free memory of downsampled images
        del img_before_small
        del img_after_small
        
        try:
            final_before = cv2.warpPerspective(img_before, H_translation, output_size, 
                                               borderValue=(255, 255, 255))
            final_after = cv2.warpPerspective(img_after, H_translation @ M, output_size, 
                                              borderValue=(255, 255, 255))
        except cv2.error as e:
            print(f"OpenCV Error during warping: {e}", flush=True)
            return img_before, img_after

        return final_before, final_after
    else:
        print("Could not find enough shared geographic anchors.")
        return img_before, img_after

def create_tiles(image, output_dir, prefix, tile_size=640, overlap=0.2):
    """
    Splits the image into tiles of size tile_size x tile_size with specified overlap.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    h, w = image.shape[:2]
    step = int(tile_size * (1 - overlap))
    
    count = 1
    for y in range(0, h, step):
        for x in range(0, w, step):
            x_start = x
            y_start = y
            x_end = x + tile_size
            y_end = y + tile_size

            # Adjust for edges
            if x_end > w:
                x_start = max(0, w - tile_size)
                x_end = w
            if y_end > h:
                y_start = max(0, h - tile_size)
                y_end = h
            
            tile = image[y_start:y_end, x_start:x_end]
            
            # Save tile
            tile_name = f"{prefix}_{count}.png"
            cv2.imwrite(os.path.join(output_dir, tile_name), tile)
            count += 1
    
    print(f"Created {count-1} tiles in {output_dir}")

if __name__ == "__main__":
    # Define paths (using absolute paths or relative if in same dir)
    path_before = "4120594_HS-SO CAL NORTH-HRBHCAAG-MB004W_BEFORE_COAX (2).pdf"
    path_after = "4120594_HS-SO CAL NORTH-HRBHCAAG-MB00W_AFTER_COAX (2).pdf"
    
    if not os.path.exists(path_before):
        print(f"Error: {path_before} not found.")
        exit(1)
    if not os.path.exists(path_after):
        print(f"Error: {path_after} not found.")
        exit(1)

    print("Loading and converting PDFs...")
    img_before = pdf_to_image(path_before)
    img_after = pdf_to_image(path_after)
    
    print("Aligning maps (Universal Canvas)...")
    final_before, final_after = align_and_pad_expanded_maps(img_before, img_after)
    
    # Save results
    # Use "ref_before" and "aligned_after" names to stay consistent with debug tool
    # even though "ref_before" is now also warped/translated.
    cv2.imwrite("ref_before.png", final_before)
    cv2.imwrite("aligned_after.png", final_after)
    print("Saved 'ref_before.png' and 'aligned_after.png'.")

    # Tiling
    print("Generating tiles...")
    prefix_before = os.path.splitext(os.path.basename(path_before))[0]
    prefix_after = os.path.splitext(os.path.basename(path_after))[0]

    create_tiles(final_before, "tiles/before", prefix_before, tile_size=640, overlap=0.2)
    create_tiles(final_after, "tiles/after", prefix_after, tile_size=640, overlap=0.2)
    print("Tiling done.")
