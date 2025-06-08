# -*- coding: utf-8 -*-
"""
Created on Sun Jun  8 05:06:56 2025

@author: IXYTY
"""
import cv2
import threading
import time
from queue import Queue
from ultralytics import YOLO
import platform
import pygame
import threading
import numpy as np
import os

# 播放报警音函数（Windows示例）
pygame.mixer.init()

def play_alert_sound():
    try:
        pygame.mixer.music.load(r'warning-alarm-991.wav')
        pygame.mixer.music.play()
    except Exception as e:
        print(f"[Error] 播放警告音频失败: {e}")
    
    
    """
def put_chinese_text(img, text, pos, font_size=30, color=(0, 0, 255)):
    在OpenCV窗口上显示中文文字，兼容中文
    import PIL.Image, PIL.ImageDraw, PIL.ImageFont
    img_pil = PIL.Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = PIL.ImageDraw.Draw(img_pil)
    font_path = "fzxbsj.TTF"  # 这里用宋体字体文件，需要放在脚本同目录或者指定完整路径
    font = PIL.ImageFont.truetype(font_path, font_size, encoding="utf-8")
    draw.text(pos, text, font=font, fill=color)
    img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    return img

"""

class CameraHandler:
    def __init__(self, cam_id, source, model_path):
        self.cam_id = cam_id
        self.source = source
        self.model_path = model_path
        self.frame_queue = Queue(maxsize=1)
        self.stop_flag = False
        self.alert_triggered = False
        self.model = YOLO(model_path)
        self.window_name = f"Camera {cam_id}"
        self.cap = None

    def camera_reader(self):
        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            print(f"摄像头 {self.source} 打不开")
            self.stop_flag = True
            return
        
        fps_limit = 5  # 限制帧率，单位fps
        frame_interval = 1 / fps_limit

        while not self.stop_flag:
            start_time = time.time()
            ret, frame = cap.read()
            if not ret:
                print(f"摄像头 {self.source} 读取失败或断开")
                self.stop_flag = True
                break
            
            if self.frame_queue.full():
                try:
                    _ = self.frame_queue.get_nowait()
                except:
                    pass
            
            self.frame_queue.put(frame)

            elapsed = time.time() - start_time
            if elapsed < frame_interval:
                time.sleep(frame_interval - elapsed)

        cap.release()

    def camera_infer(self):
        while not self.stop_flag:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get()
                img_small = cv2.resize(frame, (640, 640))

                results = self.model(img_small)
                result = results[0]

                no_helmet_detected = False

                for box, conf, cls in zip(result.boxes.xyxy, result.boxes.conf, result.boxes.cls):
                    x1, y1, x2, y2 = map(int, box)
                    cls_id = int(cls)
                    label = 'helmet' if cls_id == 0 else 'no helmet'
                    color = (0, 255, 0) if cls_id == 0 else (0, 0, 255)
                    # 字体：不支持中文，转为 UTF-8 带编码符很难显示，可以用图片方式显示#暂时不用中文
                    #cv2.rectangle(img_small, (x1, y1), (x2, y2), color, 2)
                    #不支持中文，下部更换支持中文显示
                    cv2.rectangle(img_small, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(img_small, f"{label}: {conf:.2f}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    if cls_id == 1:
                        no_helmet_detected = True

                # 警告文字
                if no_helmet_detected:
                    cv2.putText(img_small, "WARNING: No helmet detected!", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                    if not self.alert_triggered:
                        threading.Thread(target=play_alert_sound, daemon=True).start()
                        self.alert_triggered = True
                else:
                    self.alert_triggered = False

                cv2.imshow(self.window_name, img_small)

                key = cv2.waitKey(1)
                if key == ord('q'):
                    self.stop_flag = True
                    break
            else:
                time.sleep(0.01)
                
        try:
            cv2.destroyWindow(self.window_name)
        except cv2.error as e:
            print(f"[Warning] 关闭窗口失败: {e}")

        #cv2.destroyWindow(self.window_name)

    def run(self):
        t1 = threading.Thread(target=self.camera_reader, daemon=True)
        t2 = threading.Thread(target=self.camera_infer, daemon=True)
        t1.start()
        t2.start()
        return [t1, t2]
    
    def release(self):
        self.stop_flag = True
        if self.cap:
           self.cap.release()
        try:
            cv2.destroyWindow(self.window_name)
        except cv2.error as e:
            print(f"[Warning] destroyWindow 出错: {e}")


def main():
    model_path = "best.pt"  # 你的模型权重文件

    # 多摄像头地址（数字摄像头索引，或者IP流地址，支持RTSP/HTTP等）
    camera_sources = [
        0,  # 本地摄像头
        "rtsp://admin:password@192.168.1.100:554/stream1",
        "rtsp://admin:password@192.168.1.101:554/stream2",
        # 你可以添加更多地址
    ]

    handlers = []
    threads = []

    for i, src in enumerate(camera_sources):
        handler = CameraHandler(i, src, model_path)
        handlers.append(handler)
        ts = handler.run()
        threads.extend(ts)
        
    try:
        print("Press Q in any window to exit.")
        while True:
            if any(handler.stop_flag for handler in handlers):
                break
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("收到中断，退出程序。")

    # 主线程等待所有线程结束
    for handler in handlers:
        handler.release()

if __name__ == "__main__":
    main()