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
from user_settings import UserSettings


# Load model
model_handler = ModelHandler('models/yolov8n.pt')

video_path = 'datasets/videos/video1.mp4'
video_handler = VideoHandler(video_path)
lane_detector = LaneDetector()
play = True

assistant = VoiceAssistant(language="es-ES")

show_mic_image = False
assistant_action = None

def run_voice_assistant():
    global show_mic_image
    global assistant_action
    while play:
        if assistant.listen_for_keyword():
            show_mic_image = True
            assistant.text_to_speech("¿En qué puedo ayudarte?")
            assistant_action = assistant.process_command()
            show_mic_image = False

voice_assistant_thread = Thread(target=run_voice_assistant)
voice_assistant_thread.daemon = True
voice_assistant_thread.start()

frame_count = 0
fps = video_handler.get_fps()
out = None

def clip_action():
    global assistant_action
    assistant_action = "Clip"

def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")

    
    settings_window.wm_iconphoto(False, logo_photo)

    clip_seconds_label = tk.Label(settings_window, text="Duración del clip (segundos):")
    clip_seconds_label.grid(row=1, column=0, padx=10, pady=5)
    clip_seconds_entry = tk.Entry(settings_window)
    clip_seconds_entry.grid(row=1, column=1, padx=10, pady=5)

    car_camera_height_label = tk.Label(settings_window, text="Altura de la cámara (metros):")
    car_camera_height_label.grid(row=2, column=0, padx=10, pady=5)
    car_camera_height_entry = tk.Entry(settings_window)
    car_camera_height_entry.grid(row=2, column=1, padx=10, pady=5)

    focal_length_label = tk.Label(settings_window, text="Distancia focal (mm):")
    focal_length_label.grid(row=3, column=0, padx=10, pady=5)
    focal_length_entry = tk.Entry(settings_window)
    focal_length_entry.grid(row=3, column=1, padx=10, pady=5)

    current_settings = user_settings.get_settings(1)
    if current_settings:
        clip_seconds_entry.insert(0, current_settings['CLIP_SECONDS'])
        car_camera_height_entry.insert(0, current_settings['CAR_CAMERA_HEIGHT'])
        focal_length_entry.insert(0, current_settings['FOCAL_LENGTH'])


    def save_settings():
        clip_seconds = int(clip_seconds_entry.get())
        car_camera_height = float(car_camera_height_entry.get())
        focal_length = float(focal_length_entry.get())
        user_settings.save_settings(1, clip_seconds, car_camera_height, focal_length)
        settings_window.destroy()

    save_button = tk.Button(settings_window, text="Guardar", command=save_settings, bg="black", fg="white")
    save_button.grid(row=4, column=0, columnspan=2, pady=10)

# GUI setup
root = tk.Tk()
root.title("Drivia - Asistente de conducción")
root.geometry("1280x720")

logo = Image.open('assets/logo.png')
logo = logo.resize((100, 100), Image.LANCZOS)
logo_photo = ImageTk.PhotoImage(logo)
root.wm_iconphoto(False, logo_photo)

# Database path
db_path = 'db/user_settings.db'

user_settings = UserSettings(db_path)

# Left panel for buttons
left_panel = tk.Frame(root)
left_panel.pack(side="left", fill="both", expand=True)

logo_label = tk.Label(left_panel, image=logo_photo)
logo_label.pack(side="top", padx=10, pady=10)

clip_icon = ImageTk.PhotoImage(Image.open('assets/clip.png').resize((50, 50), Image.LANCZOS))
clip_icon_sub = clip_icon._PhotoImage__photo.subsample(3, 3)
clip_button = ttk.Button(left_panel, text="Clip", image=clip_icon_sub, command=clip_action, compound="left")
clip_button.pack(side="top", padx=10, pady=10)


settings_icon = ImageTk.PhotoImage(Image.open('assets/settings.png').resize((50, 50), Image.LANCZOS))
settings_icon_sub = settings_icon._PhotoImage__photo.subsample(3, 3)
settings_button = ttk.Button(left_panel, text="Settings", image=settings_icon_sub, command=open_settings, compound="left")
settings_button.pack(side="top", padx=10, pady=10)

mic_image = Image.open('assets/mic.png')
mic_image = mic_image.resize((55, 100), Image.LANCZOS)
mic_image = ImageTk.PhotoImage(mic_image)
mic_image_label = tk.Label(left_panel, image=mic_image)
mic_image_label.pack(side="top", padx=10, pady=10)
mic_label = tk.Label(left_panel, text="Haz tu consulta", wraplength=100)
mic_label.pack(side="top", padx=5, pady=5)

bottom_panel = tk.Frame(root)
bottom_panel.pack(side="bottom", fill="x")

warning_label = tk.Label(bottom_panel, text="", fg="orange", font=("Arial", 24, "bold"))
warning_label.pack(side="top", padx=10)

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

            settings = user_settings.get_settings(1)
            frame = video_handler.resize_frame(frame, 960, 540)
            frame_width = int(video_handler.get_width())
            frame_height = int(video_handler.get_height())
            frame = lane_detector.detect_lanes(frame)
            results = model_handler.detect_objects(frame)
            frame_ = frame.copy()

            for obj in results[0].boxes:
                obj_name = model_handler.names[int(obj.cls)]
                if obj_name == 'person':
                    ObjectDetector.draw_bbox(frame_, obj)
                    y1, y2 = obj.xyxy[0][1], obj.xyxy[0][3]
                    distance_to_person = ObjectDetector.estimate_distance(y1, y2,
                                                                        settings['CAR_CAMERA_HEIGHT'], settings['FOCAL_LENGTH'])

                    ObjectDetector.draw_distance_text(frame_, distance_to_person, int(obj.xyxy[0][0]), int(obj.xyxy[0][1]))
                    if lane_detector.is_object_inside_lane((obj.xyxy[0][0], obj.xyxy[0][1], obj.xyxy[0][2], obj.xyxy[0][3])):
                        ObjectDetector.draw_bbox(frame_, obj, (0, 0, 255))
                        if distance_to_person > 5:
                            warning_label.config(text="Peatón detectado en la carretera, ten precaución.", fg="orange")
                        else:
                            warning_label.config(text="Estás muy cerca del peatón, extrema las precauciones.", fg="red")
                    else:
                        warning_label.config(text="")
            
            if show_mic_image is True:
                mic_image_label.pack(side="top", padx=10, pady=10)
                mic_label.pack(side="top", padx=5, pady=5)
            else:
                mic_image_label.pack_forget()
                mic_label.pack_forget()

            frame_rgb = cv2.cvtColor(frame_, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(image=img)
            video_label.img = img_tk
            video_label.config(image=img_tk)
            
            key = cv2.waitKey(1) & 0xFF
            
            play = KeyHandler.handle_key_press(key, video_handler)
            
            # Increment frame count
            frame_count += 1
            
            # Start saving frames
            if assistant_action == "Clip":
                if frame_count >= fps * settings['CLIP_SECONDS']:
                    if out is not None:
                        out.release()
                    
                    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    out = cv2.VideoWriter(f'clips/{current_datetime}.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

                    # Set the frame position
                    video_handler.set_frame_position(video_handler.get_frame_position() - int(fps * settings['CLIP_SECONDS']))
                    # Read and save frames
                    for i in range(int(fps * settings['CLIP_SECONDS'])):
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