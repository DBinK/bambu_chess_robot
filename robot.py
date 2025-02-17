import time
from motion import BambuMotion

class BambuRobot(BambuMotion):
    def __init__(self, reset=True):
        super().__init__(reset=reset)
        self.STANDBY_Z = 30   # 待机高度
        self.CHESS_Z = 10     # 棋子高度
        self.Z_SPEED = 48000  # Z轴速度

    def move_z(self, pz, speed=None):
        if speed is None:
            speed = self.Z_SPEED
        super().move_z(pz, speed)

    # def move(self, px, py, pz, speed=None, delay=0):

    #     px = px + 0
    #     py = py + 0
    #     pz = pz + 0

    #     return super().move(px, py, pz, speed, delay)

    def capture_piece(self, from_x, from_y):
        print("开始 捕获棋子")
        self.move(from_x, from_y, self.STANDBY_Z)  # 移动到棋子 起始位置
        self.move_z(self.CHESS_Z)                  # 下降 

        print("用电磁铁 拾取棋子")
        self.notice_finish()  
        pass                                       # 用电磁铁 拾取棋子
        #time.sleep(2)                              # 等待吸起棋子

        self.move_z(self.STANDBY_Z)                # 抬起 

        print(f"捕获棋子于 ({from_x}, {from_y}) \n")

    def release_piece(self, to_x, to_y):
        print("开始 释放棋子")
        self.move(to_x, to_y, self.STANDBY_Z)  # 移动到棋子 目标位置
        self.move_z(self.CHESS_Z)              # 下降 

        print("用电磁铁 释放棋子")
        self.notice_finish()
        pass                                   # 用电磁铁 释放棋子
        #time.sleep(2)                          # 等待放下棋子

        self.move_z(self.STANDBY_Z)            # 抬起

        print(f"释放棋子到 ({to_x}, {to_y}) \n")

    def show_chess_board(self):
        print("展示棋盘")
        self.move_z(self.STANDBY_Z)                 # 抬起
        self.move(273, 250, self.STANDBY_Z, 30000)  # 移动到待机处
        print("待机并展示棋盘 \n")

    def move_piece(self, from_x, from_y, to_x, to_y):
        self.capture_piece(from_x, from_y)
        self.release_piece(to_x, to_y)
        self.show_chess_board()

        print(f"棋子从 ({from_x}, {from_y}) 移动到 ({to_x}, {to_y}) \n")


if __name__ == "__main__":

    robot = BambuRobot(reset=False)
    
    # robot.hard_reset()

    
    # robot.move(0, 0 ,10)  # 1号点
    # time.sleep(5)

    # robot.move(16, 16 ,10)  # 1号点
    # time.sleep(5)

    # robot.move(16+224, 16 ,10)  # 2号点
    # time.sleep(5)
    
    # robot.move(16, 16+224 ,10)  # 3号点
    # time.sleep(5)
    
    # robot.move(16+224, 16+224 ,10)  # 4号点
    # time.sleep(5)

    robot.move(94, 170 ,10)  # 5号点
    time.sleep(5)

    robot.show_chess_board()

    #robot.move_piece(180, 180, 50, 50)

    # print("等待10秒后复位")
    # time.sleep(10)
    # robot.soft_reset(30000)
