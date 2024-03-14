import threading as thr
import cv2
from PIL import Image
import queue as qu
import numpy as np

raw_frames: qu.LifoQueue = qu.LifoQueue()
new_frames: list = []
frame_count: int = 0

def get_frames(path:str):
    global raw_frames, new_frames, frame_count

    capture = cv2.VideoCapture(path)
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    success: bool = True
    while success:
        try:
            print(raw_frames.qsize(), len(new_frames))
            success, content = capture.read()
            content = cv2.cvtColor(content, cv2.COLOR_BGR2RGB)
            raw_frames.put(item=content)
        except: break
    capture.release()
    print("Thread 1 finished")


def convert_frames():
    global raw_frames, new_frames, frame_count

    while True:
        content = raw_frames.get()
        content = cv2.resize(content, (500,500))
        frame = content
        new_frames.append(frame)
        if len(new_frames) == frame_count:
            break
    print("Thread 2 finished")


if __name__ == "__main__":
    path: str = r"_images\video_2.mp4"
    
    thread_1: thr.Thread = thr.Thread(target=get_frames,     daemon=True, args=[path])
    thread_2: thr.Thread = thr.Thread(target=convert_frames, daemon=True)
    
    thread_1.start() 
    thread_2.start()
    
    thread_1.join()
    thread_2.join()

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video = cv2.VideoWriter("test2.mp4", 0, fourcc, 30, (500, 500))
    for frame in new_frames:
        content = cv2.cvtColor(np.array(object=frame), cv2.COLOR_RGB2BGR)
        video.write(image=content)

    video.release()
