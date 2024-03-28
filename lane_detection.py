import cv2
import numpy as np
from key_handler import KeyHandler
from video_handler import VideoHandler

def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked_img = cv2.bitwise_and(img, mask)
    return masked_img

def draw_lines(img, lines, color=[255, 0, 0], thickness=3):
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(img, (x1, y1), (x2, y2), color, thickness)

def detect_lanes(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred_img = cv2.GaussianBlur(gray_img, (5, 5), 0)
    edges = cv2.Canny(blurred_img, 50, 150)

    height, width = img.shape[:2]
    vertices = np.array([[(0, height), (width / 2, height / 2), (width, height)]], dtype=np.int32)
    masked_edges = region_of_interest(edges, vertices)

    lines = cv2.HoughLinesP(masked_edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=100)
    line_img = np.zeros((height, width, 3), dtype=np.uint8)
    draw_lines(line_img, lines)

    combined_img = cv2.addWeighted(img, 0.8, line_img, 1.0, 0.0)

    return combined_img

video_path = 'videos/highway1.mp4'
video_handler = VideoHandler(video_path)

while True:
    if not video_handler.is_paused():
        ret, frame = video_handler.read_frame()
    if not ret:
        break

    processed_frame = detect_lanes(frame)

    cv2.imshow('Lane Detection', processed_frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    else:
        KeyHandler.handle_key_press(key, video_handler)

video_handler.release()
cv2.destroyAllWindows()
