# member2_detection.py
from ultralytics import YOLO

import cv2

def detect_pedestrians(frame, model):
    """
    Detect pedestrians in a frame using YOLOv8.
    Returns list of bounding boxes: [[x1,y1,x2,y2], ...]
    """
    results = model.predict(frame, imgsz=640, conf=0.25)  # modern API
    rects = []
    for r in results:
        if r.boxes is not None:
            for box in r.boxes:
                cls = int(box.cls[0])  # class index
                label = model.names.get(cls, str(cls))
                if label.lower() in ('person', 'people'):
                    xyxy = box.xyxy[0].cpu().numpy()  # get [x1, y1, x2, y2]
                    rects.append([int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])])

    return rects
