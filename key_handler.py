import cv2

class KeyHandler:
    def handle_key_press(key, video_handler):
        current_frame_pos = video_handler.cap.get(cv2.CAP_PROP_POS_FRAMES)
        total_frames = video_handler.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = video_handler.cap.get(cv2.CAP_PROP_FPS)
        frame_jump = 20 * fps  # Jump 5 seconds
        small_frame_jump = 5 * fps  # Jump 5 seconds
        
        if key == ord('p'):
            video_handler.cap.set(cv2.CAP_PROP_POS_FRAMES, min(current_frame_pos + frame_jump, total_frames))
        elif key == ord('o'):
            video_handler.cap.set(cv2.CAP_PROP_POS_FRAMES, max(current_frame_pos - frame_jump, 0))
        elif key == ord('l'):
            video_handler.cap.set(cv2.CAP_PROP_POS_FRAMES, min(current_frame_pos + small_frame_jump, total_frames))
        elif key == ord('k'):
            video_handler.cap.set(cv2.CAP_PROP_POS_FRAMES, max(current_frame_pos - small_frame_jump, 0))
        elif key == ord(' '):
            video_handler.set_paused(not video_handler.is_paused())
    
    def draw_key_controls(frame):
        cv2.putText(frame, "Controls: p-Advance 20s, o-Rewind 20s, l-Advance 5s, k-Rewind 5s, Space-Pause/Resume, q-Quit", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
