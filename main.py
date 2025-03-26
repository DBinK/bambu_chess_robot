import threading
import time
from camera import USBCamera

camera = USBCamera()

cam_thread = threading.Thread(target=camera.loop)
cam_thread.start()

while cam_thread.is_alive():

    print("开始测试视觉")
    print(camera.center_points)
    print(camera.borad_chess_colors)
    print(camera.black_coords)
    print(camera.white_coords)
    time.sleep(3)


print("结束所有")