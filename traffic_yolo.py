from ultralytics import YOLO

def get_car_counts(video_path=0):
    """
    Uses YOLOv11 to count cars per junction side.
    For now, we assume a fixed 4-way junction (North, East, South, West).
    TODO: Add lane/ROI mapping for real cameras.
    """
    model = YOLO("yolov11n.pt")  # Load model (nano for speed)

    results = model(video_path, stream=True)

    # Placeholder: just mock some counts for demo
    # Replace with real ROI-based car detection
    return {"North": 12, "East": 3, "South": 0, "West": 7}

