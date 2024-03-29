import cv2

class VideoHandler:
    def __init__(self, video_path):
        self.cap = cv2.VideoCapture(video_path)
        self.paused = False

    def read_frame(self):
        ret, frame = self.cap.read()
        return ret, frame

    def release(self):
        self.cap.release()

    def is_paused(self):
        return self.paused

    def set_paused(self, paused):
        self.paused = paused

    def resize_frame(self, frame, width, height):
        return cv2.resize(frame, (width, height))
