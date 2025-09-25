# member4_optical_flow.py
import cv2
import numpy as np

def pixels_per_sec_from_frames(prev_frame, curr_frame, fps):
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
    flow = cv2.calcOpticalFlowFarneback(prev_gray, curr_gray, None,
                                        0.5, 3, 15, 3, 5, 1.2, 0)
    mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
    avg_mag = np.mean(mag)
    pixels_per_sec = avg_mag * fps
    return pixels_per_sec