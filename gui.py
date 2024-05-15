import tkinter as tk
from tkinter import ttk
import cv2
from threading import Thread
from model_handler import ModelHandler
from video_handler import VideoHandler
from object_detector import ObjectDetector
from key_handler import KeyHandler
from lane_detector import LaneDetector
from voice_assistant import VoiceAssistant
from datetime import datetime
from PIL import Image, ImageTk
import cv2


# Load model
model_handler = ModelHandler('models/yolov8n.pt')

video_path = 'datasets/videos/street5.mp4'
video_handler = VideoHandler(video_path)
lane_detector = LaneDetector()
play = True

assistant = VoiceAssistant(language="es-ES")

show_mic_image = False
assistant_action = None

# Function to run in a separate thread the voice assistant
def run_voice_assistant():
    global show_mic_image
    global assistant_action
    while play:
        if assistant.listen_for_keyword():
            show_mic_image = True
            assistant.text_to_speech("¿En qué puedo ayudarte?")
            assistant_action = assistant.process_command()
            show_mic_image = False

# Voice assistant thread
voice_assistant_thread = Thread(target=run_voice_assistant)
voice_assistant_thread.daemon = True
voice_assistant_thread.start()

# Variables to keep track of frames for the last 5 seconds
frame_count = 0
fps = video_handler.get_fps()

out = None

# Function to handle button click events
def clip_action():
    global assistant_action
    assistant_action = "Clip"


# GUI setup
root = tk.Tk()
root.title("Drivia - Asistente de conducción")
root.geometry("1280x720")

logo = Image.open('assets/logo.png')
logo = logo.resize((100, 100), Image.LANCZOS)

logo_photo = ImageTk.PhotoImage(logo)

root.wm_iconphoto(False, logo_photo)

# Left panel for buttons
left_panel = tk.Frame(root)
left_panel.pack(side="left", fill="both", expand=True)

logo_label = tk.Label(left_panel, image=logo_photo)
logo_label.pack(side="top", padx=10, pady=10)

clip_button = ttk.Button(left_panel, text="Clip", command=clip_action)
clip_button.pack(side="top", padx=10, pady=10)

# Add mic_image_label and hide initially
mic_image = Image.open('assets/mic.png')
mic_image = mic_image.resize((55, 100), Image.LANCZOS)
mic_image = ImageTk.PhotoImage(mic_image)
mic_image_label = tk.Label(left_panel, image=mic_image)
mic_image_label.pack(side="top", padx=10, pady=10)
mic_label = tk.Label(left_panel, text="Haz tu consulta", wraplength=100)
mic_label.pack(side="top", padx=5, pady=5)

warning_label = tk.Label(left_panel, text="", fg="orange", wraplength=100)
warning_label.pack(side="top", padx=10, pady=10)
danger_label = tk.Label(left_panel, text="", fg="red", wraplength=100)
danger_label.pack(side="top", padx=10, pady=10)
# Right panel for video display
right_panel = tk.Frame(root)
right_panel.pack(side="right", fill="both", expand=True)

video_label = tk.Label(right_panel)
video_label.pack()

def update_frame():
    global play
    global frame_count
    global assistant_action
    global out
    if play:
        if not video_handler.is_paused():
            ret, frame = video_handler.read_frame()
            if not ret:
                play = False
                root.destroy()
                return

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
                        # Draw red lines around the video
                        if distance_to_person > 5:
                            danger_label.config(text="")
                            warning_label.config(text="Peatón detectado en la carretera, ten precaución.")
                        else:
                            warning_label.config(text="")
                            danger_label.config(text="Estás muy cerca del peatón, extrema las precauciones.")
                    else:
                        warning_label.config(text="")
                        danger_label.config(text="")
            #KeyHandler.draw_key_controls(frame_)
            
            if show_mic_image is True:
                mic_image_label.pack(side="top", padx=10, pady=10)  # Show mic image when listening
                mic_label.pack(side="top", padx=5, pady=5)
            else:
                mic_image_label.pack_forget()  # Hide mic image when not listening
                mic_label.pack_forget()
                
            # Convert the frame to RGB format
            frame_rgb = cv2.cvtColor(frame_, cv2.COLOR_BGR2RGB)
            # Convert the frame to ImageTk format
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(image=img)
            # Update the label with the new frame
            video_label.img = img_tk
            video_label.config(image=img_tk)
            
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
            
    root.after(1, update_frame)  # Update frame every 10 milliseconds

update_frame()

root.mainloop()

# Release resources
video_handler.release()
cv2.destroyAllWindows()
if out is not None:
    out.release()

update_frame()

root.mainloop()

# Release resources
video_handler.release()
cv2.destroyAllWindows()
if out is not None:
    out.release()
