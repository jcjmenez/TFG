import cv2

from model_handler import ModelHandler
from video_handler import VideoHandler
from object_detector import ObjectDetector
from key_handler import KeyHandler
from lane_detector import LaneDetector

# Load model
model_handler = ModelHandler('yolov8n.pt')

video_path = 'dataset/videos/back3.mp4'
video_handler = VideoHandler(video_path)
lane_detector = LaneDetector()
ret = True

while ret:
    if not video_handler.is_paused():
        ret, frame = video_handler.read_frame()
        if not ret:
            break

        # Resize frame to 720p for better visualization and performance
        frame = video_handler.resize_frame(frame, 1280, 720)
        frame = lane_detector.detect_lanes(frame)
        results = model_handler.detect_objects(frame)
        # MODEL DEBUG: frame_ = results[0].plot()
        frame_ = frame.copy()

        # Loop through detected objects
        for obj in results[0].boxes:
            obj_name = model_handler.names[int(obj.cls)]
            # Check if the detected object is a person
            if obj_name == 'person':
                ObjectDetector.draw_bbox(frame_, obj)
                # Assuming the car's camera is mounted at a fixed height and angle
                car_camera_height = 0.8  # meters (height of car's camera)
                focal_length = 700  # pixels (focal length of the camera)
                y1, y2 = obj.xyxy[0][1], obj.xyxy[0][3]
                distance_to_person = ObjectDetector.estimate_distance(y1, y2,
                                                                    car_camera_height, focal_length)

                ObjectDetector.draw_distance_text(frame_, distance_to_person, int(obj.xyxy[0][0]), int(obj.xyxy[0][1]))

    KeyHandler.draw_key_controls(frame_)
    cv2.imshow('frame', frame_)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    else:
        KeyHandler.handle_key_press(key, video_handler)

video_handler.release()
cv2.destroyAllWindows()
