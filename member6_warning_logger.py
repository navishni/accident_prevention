import cv2
import csv
import time
import os
import pygame

# Initialize mixer
pygame.mixer.init()

def play_alarm(alert_sound):
    """Play alarm in loop if not already playing"""
    if os.path.exists(alert_sound):
        try:
            if not pygame.mixer.music.get_busy():  # play only if not already playing
                pygame.mixer.music.load(alert_sound)
                pygame.mixer.music.play(-1)  # loop until stopped
        except Exception as e:
            print("🔇 Could not play alarm:", e)
    else:
        print("🔇 Alert sound file not found:", alert_sound)

def stop_alarm():
    """Stop alarm if it is playing"""
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

def run_warning_system(video_source="videoplayback.mp4", alert_sound="alert.mp3", speed_limit=30):
    """Main warning system"""
    cap = cv2.VideoCapture(video_source)

    if not cap.isOpened():
        print("❌ Error: Could not open video source ->", video_source)
        return

    log_file = "alerts.csv"
    with open(log_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "PedestrianID", "Speed(km/h)"])

    print("✅ Warning System Started. Press Q to quit.")

    blink_counter = 0  # counter for blinking effect

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("📁 End of video or cannot read frame.")
            break

        # Debug info
        print("⚡ Frame captured:", frame.shape)

        pedestrian_in_roi = True      # Dummy test (always true for now)
        vehicle_speed = 40            # Dummy test (always 40 km/h)

        if pedestrian_in_roi and vehicle_speed > speed_limit:
            print("⚠ Reduce Speed! Speed =", vehicle_speed, "km/h")
            play_alarm(alert_sound)

            # Log to CSV
            with open(log_file, mode="a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([time.strftime("%H:%M:%S"), 1, vehicle_speed])

            # Transparent flashing warning banner
            h, w, _ = frame.shape
            overlay = frame.copy()

            if (blink_counter // 20) % 2 == 0:  # flash every ~20 frames
                cv2.rectangle(overlay, (0, h - 80), (w, h), (0, 0, 255), -1)  # red bar
                alpha = 0.5  # transparency
                frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

                cv2.putText(frame, "⚠ REDUCE SPEED!", (30, h - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 3)

            blink_counter += 1

        else:
            stop_alarm()

        cv2.imshow("Warning System", frame)
        print("📺 Frame displayed in window")

        # Check for 'q' key press
        if cv2.waitKey(30) & 0xFF == ord('q'):
            print("👋 Exiting Warning System.")
            stop_alarm()
            break

    cap.release()
    cv2.destroyAllWindows()


# -----------------------------
# Run program (choose source)
# -----------------------------
if __name__ == "_main_":
    # For webcam → run_warning_system(0)
    # For video file → run_warning_system("dashcam.mp4")
    run_warning_system(0, "alert.mp3", 30)