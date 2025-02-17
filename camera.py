import time
import cv2
import os

import vision


# 摄像头参数
camera_params = {
    'camera_id': 0,
    'image_width': 1280,
    'image_height': 720,
    'auto_exposure': 1,
    'exposure_time': 200,
    'fps': 60,
    'gain': 100,
}

def time_diff(last_time=[None]):
    """计算两次调用之间的时间差，单位为ns。"""
    current_time = time.time_ns()     # 获取当前时间（单位：ns）

    if last_time[0] is None:          # 如果是第一次调用，更新 last_time
        last_time[0] = current_time
        return 0.000_000_1            # 防止第一次调用时的除零错误
    
    else: # 计算时间差
        diff = current_time - last_time[0]  # 计算时间差
        last_time[0] = current_time         # 更新上次调用时间
        return diff                         # 返回时间差 ns

class USBCamera:
    def __init__(self):
        # 获取相机参数
        self.fps = camera_params.get('fps', 60)
        self.camera_id = camera_params.get('camera_id', 0)
        self.image_width = camera_params.get('image_width', 1280)
        self.image_height = camera_params.get('image_height', 720)
        self.auto_exposure = camera_params.get('auto_exposure', 1)
        self.exposure_time = camera_params.get('exposure_time', 100)
        self.gain = camera_params.get('gain', 0)

        # 初始化相机
        print(f'开始初始化 {self.camera_id} 号相机相机...')
        self.cap = cv2.VideoCapture(self.camera_id)

        print(f'初始化了 {self.camera_id} 号相机, 开始设置参数...')
        self.set_camera_parameters() # 设置相机参数

        # print('启动USB相机图像捕捉循环')
        # self.cam_thread = threading.Thread(target=self.loop)
        # self.cam_thread.start()

    def set_camera_parameters(self):
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.image_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.image_height)
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, self.auto_exposure)
        self.cap.set(cv2.CAP_PROP_EXPOSURE, self.exposure_time)
        self.cap.set(cv2.CAP_PROP_GAIN, self.gain)

        print(f"设置的相机: {self.camera_id} 号相机")
        print(f"设置的分辨率: {self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)} x {self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
        print(f"设置的帧率: {self.cap.get(cv2.CAP_PROP_FPS)}")

    def loop(self):
        print("进入 loop 线程")

        cnt = 0
        while not self.cap.isOpened():
            cnt += 1
            print(f"摄像头打开失败，请检查摄像头是否正常连接！{cnt}")
            time.sleep(0.1)
            continue

        while True:
            ret, frame = self.cap.read()
            
            img_pre = vision.pre_process(frame)
            detections = vision.detect_tags(img_pre)

            # 绘制检测结果
            img_draw = vision.draw_tags(frame, detections)

            if ret:
                # if os.environ.get('DISPLAY') and os.isatty(0):  # 检查有无图形界面
                if os.isatty(0):
                    cv2.namedWindow("raw", cv2.WINDOW_NORMAL)
                    cv2.imshow("raw", frame)

                    cv2.namedWindow("img_draw", cv2.WINDOW_NORMAL)
                    cv2.imshow("img_draw", img_draw)
                
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        self.destroy()
                        break 

                dt = time_diff()         

                print(f"图像大小: {frame.shape}, 帧率 FPS: {1 / (dt/1e9) }, 帧时间: {dt/1e6}")    
                
            time.sleep(0.001)

        print("结束了 loop 线程")

    def destroy(self):
        self.cap.release()  # 释放摄像头资源

if __name__ == '__main__':
    camera = USBCamera()
    camera.loop()