import cv2
from threading import Thread
from model_handler import ModelHandler
from video_handler import VideoHandler
from object_detector import ObjectDetector
from key_handler import KeyHandler
from lane_detector import LaneDetector
from voice_assistant import VoiceAssistant
from datetime import datetime

# Load model
model_handler = ModelHandler('models/yolov8n.pt')

video_path = 'datasets/videos/street5.mp4'
video_handler = VideoHandler(video_path)
lane_detector = LaneDetector()
play = True

assistant = VoiceAssistant(language="es-ES")

listening_image = None
assistant_action = None
# Function to run in a separate thread the voice assistant
def run_voice_assistant():
    global listening_image
    global assistant_action
    while play:
        if assistant.listen_for_keyword():
            listening_image = cv2.imread('assets/mic.jpg')
            assistant_action = assistant.process_command()
            listening_image = None

# Voice assistant thread
voice_assistant_thread = Thread(target=run_voice_assistant)
voice_assistant_thread.daemon = True
voice_assistant_thread.start()

# Variables to keep track of frames for the last 5 seconds
frame_count = 0
fps = video_handler.get_fps()

out = None

while play:
    if not video_handler.is_paused():
        ret, frame = video_handler.read_frame()
        if not ret:
            play = False
            break

        # Resize frame for better visualization and performance
        frame = video_handler.resize_frame(frame, 960, 540)
        frame_width = int(video_handler.get_width())
        frame_height = int(video_handler.get_height())
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
                if lane_detector.is_object_inside_lane((obj.xyxy[0][0], obj.xyxy[0][1], obj.xyxy[0][2], obj.xyxy[0][3])):
                    # If the person is inside the lane boundaries, warn the driver
                    ObjectDetector.draw_bbox(frame_, obj, (0, 0, 255))

        KeyHandler.draw_key_controls(frame_)
        
        if listening_image is not None:
            # Resize listening image
            listening_image_resized = cv2.resize(listening_image, (55, 100))
            h, w, _ = listening_image_resized.shape
            # Show mic in the bottom center of the frame
            frame_[frame_.shape[0] - h - 10:frame_.shape[0] - 10, int((frame_.shape[1] - w) / 2):int((frame_.shape[1] + w) / 2)] = listening_image_resized
            
        cv2.imshow('frame', frame_)
        key = cv2.waitKey(1) & 0xFF
        
        play = KeyHandler.handle_key_press(key, video_handler)
        
        # Increment frame count
        frame_count += 1
        
        # Start saving frames from the last 5 seconds when 'h' key is pressed
        if assistant_action == "Clip":
            if frame_count >= fps * 5:
                if out is not None:
                    out.release()
                
                current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                out = cv2.VideoWriter(f'clips/{current_datetime}.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

                # Set the frame position to start from 5 seconds ago
                video_handler.set_frame_position(video_handler.get_frame_position() - int(fps * 5))
                # Read and save frames for the last 5 seconds
                for i in range(int(fps * 5)):
                    ret, frame = video_handler.read_frame()
                    if ret:
                        out.write(frame)
                # Reset frame count
                frame_count = 0
            assistant_action = None

# Release resources
video_handler.release()
cv2.destroyAllWindows()
if out is not None:
    out.release()
