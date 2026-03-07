from ultralytics import YOLO
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")

try:
    print(f"Loading YOLO from {MODEL_PATH}...")
    model = YOLO(MODEL_PATH)
    print("Main model loaded.")
    
    ps_model_path = os.path.join(os.path.dirname(MODEL_PATH), "power_supply_best.pt")
    ps_model = YOLO(ps_model_path)
    print("PS model loaded.")
    
    node_model_path = os.path.join(os.path.dirname(MODEL_PATH), "3x3_4x4_new_model.pt")
    node_model = YOLO(node_model_path)
    print("Node model loaded.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
