import fitz
import cv2
import numpy as np
from ultralytics import YOLO
from skimage.morphology import skeletonize
from collections import deque
import os
from callout_utils import add_interactive_callouts, get_user_callout_info


# -----------------------------
# Convert PDF → Image
# -----------------------------
def pdf_to_image(pdf_path):

    doc = fitz.open(pdf_path)
    page = doc.load_page(0)

    pix = page.get_pixmap(matrix=fitz.Matrix(4,4))

    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
        pix.h, pix.w, pix.n
    )

    if pix.n == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    else:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    return img


# -----------------------------
# YOLO Node Detection
# -----------------------------
def detect_node(img, model):

    results = model(img, imgsz=1280, conf=0.1)

    result = results[0]

    best_conf = -1
    best_bbox = None
    best_center = None

    if result.obb is not None and len(result.obb) > 0:

        boxes = result.obb

        for i in range(len(boxes)):

            conf = float(boxes.conf[i])

            if conf > best_conf:

                best_conf = conf

                pts = boxes.xyxyxyxy[i].cpu().numpy()

                x1 = int(pts[:,0].min())
                y1 = int(pts[:,1].min())
                x2 = int(pts[:,0].max())
                y2 = int(pts[:,1].max())

                cx = int((x1+x2)/2)
                cy = int((y1+y2)/2)

                best_bbox = (x1,y1,x2,y2)
                best_center = (cx,cy)

    elif result.boxes is not None and len(result.boxes) > 0:

        boxes = result.boxes.xyxy.cpu().numpy()
        confs = result.boxes.conf.cpu().numpy()

        for i in range(len(boxes)):

            conf = float(confs[i])

            if conf > best_conf:

                best_conf = conf

                x1,y1,x2,y2 = map(int,boxes[i])

                cx = int((x1+x2)/2)
                cy = int((y1+y2)/2)

                best_bbox = (x1,y1,x2,y2)
                best_center = (cx,cy)

    if best_bbox is None:
        return None,None,None

    print(f"Node confidence: {best_conf:.3f}")

    return best_bbox,best_center,best_conf


# -----------------------------
# Color-Agnostic Mask
# -----------------------------
def build_general_cable_mask(img):

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # saturation = strong color highlight
    s = hsv[:, :, 1]

    # brightness
    v = hsv[:, :, 2]

    # detect any strong colored pixel
    mask_color = cv2.bitwise_and(
        cv2.threshold(s, 70, 255, cv2.THRESH_BINARY)[1],
        cv2.threshold(v, 80, 255, cv2.THRESH_BINARY)[1]
    )

    # morphological closing to connect color transitions
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25,25))
    mask = cv2.morphologyEx(mask_color, cv2.MORPH_CLOSE, kernel)

    # remove thin noise
    kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel2)

    return mask
# -----------------------------
# Extract Cable Connected to Node
# -----------------------------
def extract_connected_thick_line(img,bbox):

    h,w = img.shape[:2]
    x1,y1,x2,y2 = bbox

    raw_mask = build_general_cable_mask(img)

    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(31,31))
    kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))

    closed = cv2.morphologyEx(raw_mask,cv2.MORPH_CLOSE,kernel_close)
    cleaned = cv2.morphologyEx(closed,cv2.MORPH_OPEN,kernel_open)

    num_labels,labels,stats,_ = cv2.connectedComponentsWithStats(cleaned,8)

    node_mask = np.zeros((h,w),dtype=np.uint8)

    margin = max(10,min(80,(x2-x1)//2,(y2-y1)//2))

    cv2.rectangle(
        node_mask,
        (max(0,x1-margin),max(0,y1-margin)),
        (min(w-1,x2+margin),min(h-1,y2+margin)),
        255,-1
    )

    valid=set()

    for lbl in range(1,num_labels):

        comp=(labels==lbl).astype(np.uint8)*255

        if cv2.countNonZero(cv2.bitwise_and(comp,node_mask))>0:
            valid.add(lbl)

    final=np.zeros((h,w),dtype=np.uint8)

    for lbl in valid:
        final[labels==lbl]=255

    return final


# -----------------------------
# Skeletonize
# -----------------------------
def get_skeleton(binary):

    skel = skeletonize(binary//255)

    return skel.astype(np.uint8)


# -----------------------------
# Find Start Pixels
# -----------------------------
def find_start_pixels(skeleton,bbox,max_search_radius=300):

    x1,y1,x2,y2 = bbox
    cx=(x1+x2)//2
    cy=(y1+y2)//2

    h,w = skeleton.shape

    for margin in range(8,max_search_radius,8):

        ring = np.zeros((h,w),dtype=np.uint8)

        cv2.rectangle(
            ring,
            (max(0,x1-margin),max(0,y1-margin)),
            (min(w-1,x2+margin),min(h-1,y2+margin)),
            255,3
        )

        inter = cv2.bitwise_and(skeleton,ring)

        pts = np.argwhere(inter>0)

        if len(pts)>0:
            return [(px,py) for py,px in pts]

    ys,xs=np.where(skeleton>0)

    if len(ys)==0:
        return []

    dists=(xs-cx)**2+(ys-cy)**2

    idx=np.argmin(dists)

    return [(int(xs[idx]),int(ys[idx]))]


# -----------------------------
# BFS Cable Trace
# -----------------------------
def trace_line(skeleton,start):

    h,w=skeleton.shape

    visited=set()
    queue=deque([(start,0)])

    visited.add(start)

    furthest=start
    max_dist=0

    parent={start:None}

    dirs=[(-1,-1),(-1,0),(-1,1),
          (0,-1),(0,1),
          (1,-1),(1,0),(1,1)]

    while queue:

        (x,y),dist=queue.popleft()

        if dist>max_dist:
            max_dist=dist
            furthest=(x,y)

        for dx,dy in dirs:

            nx,ny=x+dx,y+dy

            if 0<=nx<w and 0<=ny<h:

                if skeleton[ny,nx]>0 and (nx,ny) not in visited:

                    visited.add((nx,ny))
                    parent[(nx,ny)]=(x,y)

                    queue.append(((nx,ny),dist+1))

    path=[]
    curr=furthest

    while curr is not None:
        path.append(curr)
        curr=parent[curr]

    path.reverse()

    return furthest,max_dist,path


# -----------------------------
# Main Pipeline
# -----------------------------
def process_map(pdf_path,model_path):

    print("Converting PDF to image...")

    img = pdf_to_image(pdf_path)

    print("Loading YOLO model...")

    model = YOLO(model_path)

    bbox,node_center,conf = detect_node(img,model)

    if bbox is None:
        print("Node not detected")
        return

    x1,y1,x2,y2 = bbox
    cx,cy = node_center

    print("Node detected:",cx,cy)

    cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),3)

    cv2.putText(img,"NODE",(x1,y1-10),
                cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)

    print("Extracting cable connected to node...")

    lines = extract_connected_thick_line(img,bbox)

    skeleton = get_skeleton(lines)

    start_pixels = find_start_pixels(skeleton,bbox)

    if not start_pixels:
        print("Cable not found")
        return

    best_port=None
    best_path=[]
    max_dist=-1

    for sp in start_pixels:

        port,dist,path = trace_line(skeleton,sp)

        if dist>max_dist:
            max_dist=dist
            best_port=port
            best_path=path

    px,py = best_port

    print("Port detected:",best_port)

    if best_path:
        pts=np.array(best_path,np.int32).reshape((-1,1,2))

        cv2.polylines(img,[pts],False,(255,0,0),4)

    cv2.rectangle(img,(px-40,py-40),(px+40,py+40),(0,0,255),3)

    cv2.putText(img,"PORT",(px+10,py),
                cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)

    os.makedirs("outputs",exist_ok=True)

    out="outputs/result.png"

    cv2.imwrite(out,img)

    print("Output image saved:",out)

    # --- PDF Callout Generation ---
    callout_text = get_user_callout_info()
    
    # Scale coordinates for PDF (4x matrix used in pdf_to_image)
    pdf_node_pos = (cx / 4.0, cy / 4.0)
    pdf_port_pos = (px / 4.0, py / 4.0)
    
    callout_data = [
        {'point': pdf_node_pos, 'text': "NODE"},
        {'point': pdf_port_pos, 'text': callout_text}
    ]
    
    pdf_out = out.replace(".png", ".pdf")
    print(f"Generating PDF callouts for Node and Port...")
    
    add_interactive_callouts(pdf_path, pdf_out, callout_data)
    
    print("PDF output saved:", pdf_out)

# ----------------------------------
# RUN
# ----------------------------------
if __name__=="__main__":

    PDF_PATH="maps/HUB32_BL_BL_OVERVIEW_FIBER.pdf"
    MODEL_PATH="models/node_model.pt"

    process_map(PDF_PATH,MODEL_PATH)