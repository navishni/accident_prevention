import cv2
import numpy as np
import time
from member5_calibration import play_alarm, stop_alarm

# -----------------------------
# Parameters
# -----------------------------
ALERT_SOUND = "alert.mp3"   # make sure this file exists
FRAME_WIDTH, FRAME_HEIGHT = 640, 360
SPEED_LIMIT = 30
vehicle_speed = 40  # dummy speed > SPEED_LIMIT

# -----------------------------
# Create dummy frame
# -----------------------------
frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)  # black frame
blink_counter = 0

print("✅ Dummy Warning Test Started. Press 'q' to quit.")

while True:
    display_frame = frame.copy()
    
    # flashing red banner
    if (blink_counter // 20) % 2 == 0:
        overlay = display_frame.copy()
        cv2.rectangle(overlay, (0, FRAME_HEIGHT-80), (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 255), -1)
        alpha = 0.5
        display_frame = cv2.addWeighted(overlay, alpha, display_frame, 1-alpha, 0)
        cv2.putText(display_frame, "⚠ REDUCE SPEED!", (30, FRAME_HEIGHT-30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        # play alarm
        play_alarm(ALERT_SOUND)
    else:
        stop_alarm()
    
    blink_counter += 1

    cv2.imshow("Dummy Warning Test", display_frame)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        stop_alarm()
        break

cv2.destroyAllWindows()
print("👋 Test Ended.")
