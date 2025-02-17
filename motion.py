import time
import math
from bambu_connect import BambuClient

from config import hostname, access_code, serial

class BambuMotion:
    def __init__(self, reset=True):
        self.bambu_client = BambuClient(hostname, access_code, serial)
        self.position_x = 128  # 默认位置
        self.position_y = 128
        self.position_z = 10

        self.MOTOR_SPEED = 18000  # 默认速度

        self.PX_LIMIT = [0, 280]
        self.PY_LIMIT = [0, 256]
        self.PZ_LIMIT = [0, 200]

        self.EXTRA_DELAY = 0.5

        if reset:
            self.hard_reset()

    def send_gcode(self, gcode_command):
        self.bambu_client.send_gcode(gcode_command)
        # print(f"发送了 G-code 命令: {gcode_command}")

    def hard_reset(self):
        print("正在执行硬复位...")
        self.send_gcode("G28")  # 回原点
        print("硬复位需要较长时间, 请耐心等待...")

    def soft_reset(self, speed=None):
        if speed is None:
            speed = self.MOTOR_SPEED
        print("正在执行软复位...")
        self.move(128, 128, 10, speed)  # 回原点
        print("软复位完成")

    def lock_motor(self):
        self.send_gcode("M17 ; 锁定所有电机")

    def unlock_motor(self):
        self.send_gcode("M18 ; 解锁所有电机")

    def _check_limits(self, px, py, pz):
        if px < self.PX_LIMIT[0] or px > self.PX_LIMIT[1]:
            print(f"px: {px} 不在合理范围内")
            return False

        if py < self.PY_LIMIT[0] or py > self.PY_LIMIT[1]:
            print(f"py: {py} 不在合理范围内")
            return False

        if pz < self.PZ_LIMIT[0] or pz > self.PZ_LIMIT[1]:
            print(f"pz: {pz} 不在合理范围内")
            return False

        return True
    
    def move(self, px, py, pz, speed=None, delay=0):
        if not self._check_limits(px, py, pz):
            return False
        
        dx, dy, dz = px - self.position_x, py - self.position_y, pz - self.position_z
        distance = math.sqrt(dx**2 + dy**2 + dz**2)

        self.position_x, self.position_y, self.position_z = px, py, pz

        speed = self.MOTOR_SPEED if speed is None else speed  # 设置速度

        self.send_gcode("G90 ; 设置为绝对坐标")
        self.send_gcode(f"G0 X{px} Y{py} Z{pz} F{speed}")
        self.send_gcode("M400 ; 等待 所有命令执行完毕")

        if delay == 0:
            delay = (distance / (speed/60)) + self.EXTRA_DELAY  # 计算需要等待的时间 + 额外延时
            print(f"等待 {delay} s")
            time.sleep(delay)
        else:
            time.sleep(delay)  # 手动暂停等待

        print(f"已移动到 ({self.position_x}, {self.position_y}, {self.position_z})")
        return True

    def move_relative(self, dx, dy, dz, speed=None, delay=0):
        px, py, pz = self.position_x + dx, self.position_y + dy, self.position_z + dz

        if not self._check_limits(px, py, pz):
            return False
        
        distance = math.sqrt(dx**2 + dy**2 + dz**2)  # 计算位移

        self.position_x, self.position_y, self.position_z = px, py, pz

        speed = self.MOTOR_SPEED if speed is None else speed  # 设置速度

        self.send_gcode("G91 ; 设置为相对坐标")
        self.send_gcode(f"G0 X{dx} Y{dy} Z{dz} F{speed}")
        self.send_gcode("M400 ; 等待所有命令执行完毕")
        self.send_gcode("G90 ; 设置回绝对坐标")

        print(f"已移动到 ({self.position_x}, {self.position_y}, {self.position_z})")

        if delay == 0:
            delay = (distance / (speed/60)) + self.EXTRA_DELAY  # 计算需要等待的时间 + 额外延时
            print(f"等待 {delay} s")
            time.sleep(delay)
        else:
            time.sleep(delay)

        return True

    def move_x(self, x, speed=None):
        return self.move(x, self.position_y, self.position_z, speed)

    def move_y(self, y, speed=None):
        return self.move(self.position_x, y, self.position_z, speed)

    def move_z(self, z, speed=None):
        return self.move(self.position_x, self.position_y, z, speed)

    def move_relative_x(self, dx, speed=None):
        return self.move_relative(dx, 0, 0, speed)

    def move_relative_y(self, dy, speed=None):
        return self.move_relative(0, dy, 0, speed)

    def move_relative_z(self, dz, speed=None):
        return self.move_relative(0, 0, dz, speed)

    def notice_finish(self):
        self.bambu_client.send_gcode("""
            M1006 S1
            M1006 C37 D25 M69 
            M1006 W
                   """)
        time.sleep(2)


if __name__ == "__main__":

    robot = BambuMotion(reset=False)

    robot.soft_reset()