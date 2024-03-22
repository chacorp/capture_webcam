import cv2
import numpy as np
import threading
import time

def combine_frames(frames):
    return np.hstack(frames)

def capture_video(camera_index, cap_dict, frame_lock, stop_event):
    cap = cv2.VideoCapture(camera_index)
    cap.set(cv2.CAP_PROP_FPS, 30)
    while not stop_event.is_set():
        ret, frame = cap.read()
        if ret:
            with frame_lock:
                cap_dict[camera_index] = frame
    cap.release()

if __name__ == '__main__':
    camera_indexes = [0, 1, 2]
    captured_frames = {}
    frame_lock = threading.Lock()
    stop_event = threading.Event()
    prev_frame_time = time.time()
    print('Starting video capture threads...')
    
    
    threads = []
    for index in camera_indexes:
        thread = threading.Thread(target=capture_video, args=(index, captured_frames, frame_lock, stop_event))
        thread.start()
        threads.append(thread)
    print('Video capture threads ready !')
    
    is_recording = False
    out = None
    FPS = 30
    current_time = time.strftime('%Y%m%d_%H%M%S')
    print('Press "r" to start recording, "s" to stop recording, and "q" to quit.')
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')    
    height, width = None, None
    listed_frames = []

    frame_count = 0  # 프레임 수를 세기 위한 카운터
    start_time = time.time()  # FPS 계산을 시작하기 위한 초기 시간
    try:
        while True:
            with frame_lock:
                frames = [captured_frames.get(index) for index in camera_indexes]
            if all(frame is not None for frame in frames):  # 수정된 부분
                combined_frame = combine_frames(frames)
                frame_count += 1  # 새 프레임을 처리할 때마다 카운터 증가
                
                if is_recording:                    
                    if out is None:
                        if height is None:
                            height, width = combined_frame.shape[:2]
                        out = cv2.VideoWriter(f'output_{current_time}.mp4', fourcc, FPS, (width, height))
                    listed_frames.append(combined_frame)
                
                elapsed_time = time.time() - start_time
                if elapsed_time >= 1.0:  # 1초마다 FPS 출력
                    _fps = frame_count / elapsed_time
                    print(f"FPS: {_fps:.2f}")  # 경과 시간 동안 처리된 프레임 수를 이용해 FPS 계산 및 출력
                    frame_count = 0  # 카운터 초기화
                    start_time = time.time()  # 시작 시간 재설정
                
                cv2.imshow('Combined Video', combined_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                print('Start recording!')
                is_recording = True
            elif key == ord('s'):
                print('Stopped recording!')
                is_recording = False
                print(f'Writing video to output_{current_time}.mp4')
                for frames in (listed_frames):
                    out.write(frames)
                listed_frames = []
                if out:
                    out.release()
                    out = None
    finally:
        stop_event.set()
        for thread in threads:
            thread.join()
        if out:
            out.release()
        cv2.destroyAllWindows()
