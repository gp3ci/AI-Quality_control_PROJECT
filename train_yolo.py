from ultralytics import YOLO

def main():
    # Load the model. Using yolov8l as requested for high accuracy
    model = YOLO('yolov8l.pt')

    # Train the model
    results = model.train(
        data='c:/Users/lenovo/Desktop/PROJECTS/Internship-Gp3/fiber_24-01-26/data.yaml',
        epochs=50, # Reduced epochs for faster iteration, user can increase if needed
        imgsz=640,
        device=0,
        batch=8, # Adjusted batch size to be safe
        save=True,
        project='c:/Users/lenovo/Desktop/PROJECTS/Internship-Gp3/fiber_24-01-26/runs/detect',
        name='train_v3_standard_aabb',
        exist_ok=True
    )

if __name__ == '__main__':
    main()
