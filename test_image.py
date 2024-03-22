import cv2
import threading
import time

def capture_video(camera_index, stop_event, capture_event):
    cap = cv2.VideoCapture(camera_index)
    while not stop_event.is_set():
        ret, frame = cap.read()
        if ret:
            cv2.imshow(f'Camera {camera_index}', frame)
            cv2.waitKey(1)
            
            if capture_event.is_set():
                save_frame(frame, camera_index)
                capture_event.clear()  # 이미지를 저장한 후 이벤트를 초기화합니다.

    cap.release()

def save_frame(frame, camera_index):
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f'camera_{camera_index}_{timestamp}.png'
    cv2.imwrite(filename, frame)
    print(f'Saved {filename}')

if __name__ == '__main__':
    camera_indexes = [0, 1, 2]
    stop_event = threading.Event()
    capture_event = threading.Event()  # 이미지 캡처 명령을 위한 이벤트

    print('Starting video capture threads...')
    threads = []
    for index in camera_indexes:
        thread = threading.Thread(target=capture_video, args=(index, stop_event, capture_event))
        thread.start()
        threads.append(thread)
    print('Video capture threads ready !')
    
    print('Press "c" to capture image, and "q" to quit.')
    
    try:
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                capture_event.set()  # 'c'를 누르면 이벤트를 설정하여 모든 카메라가 이미지를 저장하도록 함
    finally:
        stop_event.set()
        for thread in threads:
            thread.join()
        cv2.destroyAllWindows()
