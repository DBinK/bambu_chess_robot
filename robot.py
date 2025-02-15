import time
from motion import BambuMotion

class BambuRobot(BambuMotion):
    def __init__(self, reset=True):
        super().__init__(reset=reset)
        self.STANDBY_Z = 30  # 待机高度
        self.CHESS_Z = 10    # 棋子高度
        self.Z_SPEED = 48000

    def move_z(self, z, speed=None):
        if speed is None:
            speed = self.Z_SPEED
        super().move_z(z, speed)

    def capture_piece(self, from_x, from_y):
        self.move(from_x, from_y, self.STANDBY_Z)  # 移动到棋子 起始位置
        self.move_z(self.CHESS_Z)                  # 下降 
        time.sleep(1)  # 估计时间, 函数是非阻塞的, 需要手动暂停等待

        pass                                       # 用电磁铁 拾取棋子
        time.sleep(1)                              # 等待吸起棋子

        self.move_z(self.STANDBY_Z)                # 抬起 
        time.sleep(1)  # 手动暂停等待

        print(f"捕获棋子于 ({from_x}, {from_y}) \n")

    def release_piece(self, to_x, to_y):
        self.move(to_x, to_y, self.STANDBY_Z)  # 移动到棋子 目标位置
        self.move_z(self.CHESS_Z)              # 下降 
        time.sleep(1)  # 估计时间, 函数是非阻塞的, 需要手动暂停等待

        pass                                   # 用电磁铁 释放棋子
        time.sleep(1)                          # 等待放下棋子

        self.move_z(self.STANDBY_Z)            # 抬起
        time.sleep(1)  # 手动暂停等待 

        print(f"释放棋子于 ({to_x}, {to_y}) \n")

    def show_chess_board(self):
        self.move_z(self.STANDBY_Z)          # 抬起
        self.move(273, 240, self.STANDBY_Z, 20000)  # 移动到待机处
        print("待机并展示棋盘 \n")

    def move_piece(self, from_x, from_y, to_x, to_y):
        self.capture_piece(from_x, from_y)
        self.release_piece(to_x, to_y)
        self.show_chess_board()

        print(f"棋子从 ({from_x}, {from_y}) 移动到 ({to_x}, {to_y}) \n")


if __name__ == "__main__":

    robot = BambuRobot(reset=False)
    # robot = BambuRobot(reset=True)

    robot.move_piece(150, 150, 50, 50)
