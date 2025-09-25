# member5_calibration.py
import pygame
import os

# Initialize pygame mixer
pygame.mixer.init()
alarm_channel = None
alarm_sound = None

# -----------------------------
# Speed Calibration
# -----------------------------
def speed_kmh_from_pixels_sec(pixels_per_sec, meters_per_pixel=0.05):
    """
    Convert pixel/sec from optical flow into km/h.
    meters_per_pixel: calibration factor (adjust experimentally)
    """
    meters_per_sec = pixels_per_sec * meters_per_pixel
    kmh = meters_per_sec * 3.6
    return kmh

# -----------------------------
# Alarm Functions
# -----------------------------
def play_alarm(alert_file="alert.mp3"):
    global alarm_channel, alarm_sound

    if alarm_sound is None:
        if not os.path.exists(alert_file):
            print(f"❌ Alarm file not found: {alert_file}")
            return
        alarm_sound = pygame.mixer.Sound(alert_file)

    if alarm_channel is None or not alarm_channel.get_busy():
        alarm_channel = alarm_sound.play(-1)  # -1 = loop until stopped
        print("🔊 Alarm started")

def stop_alarm():
    global alarm_channel
    if alarm_channel is not None and alarm_channel.get_busy():
        alarm_channel.stop()
        print("🔇 Alarm stopped")
