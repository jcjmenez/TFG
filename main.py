import cv2
import torch

from model_handler import ModelHandler
from video_handler import VideoHandler
from object_detection import ObjectDetection
from key_handler import KeyHandler



# Load model
model_handler = ModelHandler('yolov8n.pt')

video_path = 'videos/video2.mp4'
video_handler = VideoHandler(video_path)

ret = True

while ret:
    if not video_handler.is_paused():
        ret, frame = video_handler.read_frame()
    if not ret:
        break

    results = model_handler.detect_objects(frame)
    frame_ = results[0].plot()

    # Loop through detected objects
    for obj in results[0].boxes:
        obj_name = model_handler.names[int(obj.cls)]
        # Check if the detected object is a person
        if obj_name == 'person':
            ObjectDetection.draw_bbox(frame_, obj)
            # Assuming the car's camera is mounted at a fixed height and angle
            car_camera_height = 0.8  # meters (height of car's camera)
            focal_length = 700  # pixels (focal length of the camera)
            y1, y2 = obj.xyxy[0][1], obj.xyxy[0][3]
            distance_to_person = ObjectDetection.estimate_distance(y1, y2,
                                                                   car_camera_height, focal_length)

            ObjectDetection.draw_distance_text(frame_, distance_to_person, int(obj.xyxy[0][0]), int(obj.xyxy[0][1]))

    KeyHandler.draw_key_controls(frame_)
    cv2.imshow('frame', frame_)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    else:
        KeyHandler.handle_key_press(key, video_handler)

video_handler.release()
cv2.destroyAllWindows()
