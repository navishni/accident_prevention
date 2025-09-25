# master_orchestrator_webcam_distance.py
import time
import cv2
from ultralytics import YOLO
from member2_detection import detect_pedestrians
from member3_tracker import CentroidTracker
from member4_optical_flow import pixels_per_sec_from_frames
from member5_calibration import speed_kmh_from_pixels_sec, play_alarm, stop_alarm

# -----------------------------
# Parameters
# -----------------------------
VIDEO_SOURCE = "videoplayback.mp4"              # 0 = default webcam, or video file path/stream URL
ALERT_SOUND = "alert.mp3"
SPEED_LIMIT = 30               # km/h (base threshold, not strictly needed now)
METERS_PER_PIXEL = 0.05        # calibration constant
DEFAULT_FPS = 30               # fallback if webcam doesn't provide FPS

# ROI (Region of Interest) for pedestrian closeness
ROI_RATIO = 0.6   # lower 40% of frame treated as danger zone

# -----------------------------
# Initialize
# -----------------------------
cap = cv2.VideoCapture(VIDEO_SOURCE)
if not cap.isOpened():
    print("❌ Error: Cannot open video source:", VIDEO_SOURCE)
    exit()

cap_fps = cap.get(cv2.CAP_PROP_FPS)
fps = cap_fps if cap_fps and cap_fps > 1.0 else DEFAULT_FPS
print(f"Using video source={VIDEO_SOURCE}, fps={fps}")

model = YOLO("yolov8n.pt")
tracker = CentroidTracker()
prev_frame = None
last_alarm_playing = False

# -----------------------------
# Main Loop
# -----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        time.sleep(0.05)  # retry for webcam
        continue

    frame_h, frame_w = frame.shape[:2]
    roi_top = int(frame_h * ROI_RATIO)

    # 1️⃣ Detect pedestrians
    rects = detect_pedestrians(frame, model)

    # 2️⃣ Track pedestrians
    tracked_bboxes = tracker.update(rects)

    # 3️⃣ Estimate vehicle speed
    if prev_frame is not None:
        pixels_sec = pixels_per_sec_from_frames(prev_frame, frame, fps)
        speed = speed_kmh_from_pixels_sec(pixels_sec, METERS_PER_PIXEL)
    else:
        speed = 0.0

    # 4️⃣ Distance check: is any pedestrian in danger zone?
    pedestrian_close = False
    for oid, bbox in tracked_bboxes.items():
        x1, y1, x2, y2 = bbox
        if y2 > roi_top:  # pedestrian's feet inside danger zone
            pedestrian_close = True
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame, f"ID {oid} CLOSE", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        else:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"ID {oid}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # 5️⃣ Warning logic
    if pedestrian_close and speed > 1:   # ✅ Alert only if car is moving
        print(f"⚠ ALERT! Speed={speed:.1f} km/h | Pedestrians close={len(tracked_bboxes)}")
        play_alarm(ALERT_SOUND)
        last_alarm_playing = True
    else:
        if last_alarm_playing:
            print(f"✅ Car stopped or safe. Alarm OFF. Speed={speed:.1f} km/h")
            stop_alarm()
            last_alarm_playing = False

    # -----------------------------
    # Visualization
    # -----------------------------
    # Draw ROI line
    cv2.line(frame, (0, roi_top), (frame_w, roi_top), (255, 255, 0), 2)

    cv2.putText(frame, f"Speed: {speed:.1f} km/h", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.putText(frame, f"Detections: {len(rects)}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    cv2.imshow("Warning System (Webcam + Distance Check)", frame)
    prev_frame = frame.copy()

    # Quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# -----------------------------
# Cleanup
# -----------------------------
cap.release()
cv2.destroyAllWindows()
stop_alarm()