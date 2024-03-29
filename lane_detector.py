import cv2
import numpy as np
from key_handler import KeyHandler
from video_handler import VideoHandler

class LaneDetector:
    def __init__(self):
        self.prev_extended_lines = None
        self.current_lane = None

    def region_of_interest(self, img, vertices):
        mask = np.zeros_like(img)
        cv2.fillPoly(mask, vertices, 255)
        masked_img = cv2.bitwise_and(img, mask)
        return masked_img

    def find_intersection(self, left_line, right_line):
        x1_left, y1_left, x2_left, y2_left = left_line
        x1_right, y1_right, x2_right, y2_right = right_line
        
        # Calculate the slopes and intercepts of the lines
        slope_left = (y2_left - y1_left) / (x2_left - x1_left) if (x2_left - x1_left) != 0 else float('inf')
        slope_right = (y2_right - y1_right) / (x2_right - x1_right) if (x2_right - x1_right) != 0 else float('inf')
        
        if slope_left == 0 and slope_right == 0:
            return None
        
        intercept_left = y1_left - slope_left * x1_left
        intercept_right = y1_right - slope_right * x1_right
        
        # Find the intersection point of the lines
        if slope_left != float('inf') and slope_right != float('inf') and slope_left != slope_right:
            # Points intersection
            # y = m1 * x + b1
            # y = m2 * x + b2
            # m1 * x + b1 = m2 * x + b2
            # x = (b2 - b1) / (m1 - m2)
            intersection_x = (intercept_right - intercept_left) / (slope_left - slope_right)
            intersection_y = slope_left * intersection_x + intercept_left
            return [intersection_x, intersection_y]
        else:
            # Parallel lines, return None
            return None
    
    def extend_lines(self, left_line, right_line, width, height):
        RES_SEPARATION_FACTOR = 0.13
        max_line_separation = width * RES_SEPARATION_FACTOR # Maximum separation between the lines based on the resolution
        if left_line is None or right_line is None:
            return None

        intersections = self.find_intersection(left_line, right_line)
        if intersections is None:
            # If no intersection point found, draw the previous lines
            return None

        # Find y-coordinate at the bottom of the screen
        bottom_y = height - 1

        x1_left, y1_left, x2_left, y2_left = left_line
        x1_right, y1_right, x2_right, y2_right = right_line
        # Calculate the x-coordinate for the bottom of the screen for each line
        bottom_x_left = int((bottom_y - y1_left) / ((y2_left - y1_left) / (x2_left - x1_left)) + x1_left)
        bottom_x_right = int((bottom_y - y1_right) / ((y2_right - y1_right) / (x2_right - x1_right)) + x1_right)

        # If there are no previous lines, draw the current lines
        extended_left_line = (abs(bottom_x_left), abs(bottom_y), abs(int(intersections[0])), abs(int(intersections[1])))
        extended_right_line = (abs(bottom_x_right), abs(bottom_y), abs(int(intersections[0])), abs(int(intersections[1])))
        # Calculate the separation between the lines
        line_separation = abs(bottom_x_right - bottom_x_left)
        # Check if the separation is small
        if line_separation <= max_line_separation:
            # Use the previous lines
            if self.prev_extended_lines is not None:
                return None
            else:
                
                self.prev_extended_lines = [extended_left_line, extended_right_line]
                return extended_left_line, extended_right_line
    
        
        if int(intersections[0]) < 0 or int(intersections[1]) < 0 or int(intersections[0]) > width or int(intersections[1]) > height:
            return None
        
        self.prev_extended_lines = [extended_left_line, extended_right_line]

        return extended_left_line, extended_right_line


    def draw_lanes(self, img, lines, color=[255, 0, 0], thickness=3, min_slope_threshold=0.4):
        max_left_line = None
        max_right_line = None
        max_left_x = float('inf')
        max_right_x = float('-inf')

        # Find the lines with the maximum left and right x coordinates
        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    if x2 != x1:
                        slope = (y2 - y1) / (x2 - x1)
                        if abs(slope) > min_slope_threshold:
                            if x1 <= max_left_x:
                                max_left_x = x1
                                max_left_line = (x1, y1, x2, y2)
                            if x2 >= max_right_x:
                                max_right_x = x2
                                max_right_line = (x1, y1, x2, y2)
        
        extended_lines = self.extend_lines(max_left_line, max_right_line, img.shape[1], img.shape[0])
        # Intersection point found, draw the extended lines
        lines_to_draw = None
        # If the lines are not extended, use the previous extended lines
        if extended_lines is not None:
            lines_to_draw = extended_lines
        else:
            lines_to_draw = self.prev_extended_lines
        if lines_to_draw is not None:
            for line in lines_to_draw:
                x1, y1, x2, y2 = line
                cv2.line(img, (x1, y1), (x2, y2), color, thickness)
        self.current_lane = lines_to_draw

    def detect_lanes(self, img):
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred_img = cv2.GaussianBlur(gray_img, (5, 5), 0)
        edges = cv2.Canny(blurred_img, 50, 150)

        height, width = img.shape[:2]
        vertices = np.array([[(0, height), (width / 2, height / 2), (width, height)]], dtype=np.int32)
        masked_edges = self.region_of_interest(edges, vertices)

        lines = cv2.HoughLinesP(masked_edges, 1, np.pi/180, 120, minLineLength=50, maxLineGap=100)
        line_img = np.zeros((height, width, 3), dtype=np.uint8)
        self.draw_lanes(line_img, lines)

        combined_img = cv2.addWeighted(img, 0.8, line_img, 1.0, 0.0)

        return combined_img


def main():
    video_path = 'videos/street5.mp4'
    video_handler = VideoHandler(video_path)
    lane_detector = LaneDetector()
    while True:
        if not video_handler.is_paused():
            ret, frame = video_handler.read_frame()
            if not ret:
                break
            frame = video_handler.resize_frame(frame, 1280, 720)

            processed_frame = lane_detector.detect_lanes(frame)
            cv2.imshow('Lane Detection', processed_frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        else:
            KeyHandler.handle_key_press(key, video_handler)

    video_handler.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()    