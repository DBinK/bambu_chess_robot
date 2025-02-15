from motion import BambuMotion

class BambuRobot:
    def __init__(self, reset=True):
        self.robot = BambuMotion(reset=reset)
        self.STANDBY_Z = 50  # 待机高度
        self.CHESS_Z   = 10  # 棋子高度

    def capture_piece(self, from_x, from_y):
        self.robot.move(from_x, from_y, self.STANDBY_Z)  # 移动到棋子 起始位置
        self.robot.move_z(self.CHESS_Z)                  # 下降 
        pass                                             # 用电磁铁 拾取棋子
        self.robot.move_z(self.STANDBY_Z)                # 抬起 

        print(f"捕获棋子于 ({from_x}, {from_y})")

    def relese_piece(self, to_x, to_y):

        self.robot.move(to_x, to_y, self.STANDBY_Z) # 移动到棋子 目标位置
        self.robot.move_z(self.CHESS_Z)             # 下降 
        pass                                        # 用电磁铁 拾取棋子
        self.robot.move_z(self.STANDBY_Z)           # 抬起 

        print(f"释放棋子于 ({to_x}, {to_y})")

    def show_hotbed(self):
        self.robot.move_z(self.STANDBY_Z)           # 抬起
        self.robot.move(273, 240, self.STANDBY_Z)   # 移动到待机处

    def move_piece(self, from_x, from_y, to_x, to_y):
        
        self.capture_piece(from_x, from_y)
        self.relese_piece(to_x, to_y)
        self.show_hotbed()

        print(f"棋子从 ({from_x}, {from_y}) 移动到 ({to_x}, {to_y})")


if __name__ == "__main__":
    robot = BambuRobot(reset=False)
    robot.move_piece(128, 128, 50, 50)



