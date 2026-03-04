from ultralytics import YOLO

def main():
    # Load the OBB model
    model = YOLO('yolov8l-obb.pt')

    # Train the model
    # task='obb' is typically inferred from the model weights, but good to be explicit if needed.
    # Actually, for ultralytics 8.0+, just passing the -obb model is enough.
    results = model.train(
        data='c:/Users/lenovo/Desktop/PROJECTS/Internship-Gp3/fiber_24-01-26/data_obb.yaml',
        epochs=100,
        imgsz=640,
        batch=8,
        name='fiber_yolov8l_obb'
    )

if __name__ == '__main__':
    main()
