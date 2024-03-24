import torch
from ultralytics import YOLO

class ModelHandler:
    def __init__(self, model_path):
        torch.cuda.set_device(0)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = YOLO(model_path).to(self.device)
        self.names = self.model.names
        # Check for CUDA device and set it
        print(f'Using device: {self.device}')

    def detect_objects(self, frame):
        return self.model.track(frame, persist=True)
