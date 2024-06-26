import cv2

class ObjectDetector:
    def estimate_distance(y1, y2, car_camera_height, focal_length, car_height=1):
        person_height_pixels = y2 - y1
        distance_to_person = (car_height * focal_length) / (person_height_pixels * car_camera_height)
        return distance_to_person

    def draw_distance_text(frame, distance, x, y):
        if distance <= 5:
            cv2.putText(frame, f'Distancia: {distance:.2f} metros', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 0, 255), 2)
        else:
            cv2.putText(frame, f'Distancia: {distance:.2f} metros', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 255, 0), 2)

    def draw_bbox(frame, obj, color=(0, 255, 0)):
        x1, y1, x2, y2 = map(int, obj.xyxy[0])
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
