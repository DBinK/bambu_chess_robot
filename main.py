import time
import threading
import subprocess

from loguru import logger

from camera import USBCamera
from robot import BambuRobot
from ai import TicTacToeAI

# 运行一个命令并等待其完成
result = subprocess.run(['gpio', 'mode', '3', 'out'])

cam = USBCamera()
cam.start_loop_thread()  # 启动摄像头线程

bot = BambuRobot(reset=False)

reset = input("是否硬重置位置, 第一次上电一定要重置位置, 1是, 0否:")

if reset == '1':
    bot.hard_reset()  # 第一次上电一定要重置位置
    bot.show_chess_board()  # 展示棋盘
else:
    bot.show_chess_board()  # 展示棋盘

while not cam.cam_thread.is_alive() and len(cam.center_points) < 4:
    print("等待摄像头线程启动中...")
    time.sleep(1)

class ChessBot:
    def __init__(self):
        self.state = 'mode_1'   # 初始模式为模式 1
        self.BLACK = -1
        self.WHITE = 1
        self.center_points = []
        self.board_chess_colors = []
        self.last_board_chess_colors = []
        self.black_coords = []
        self.white_coords = []
        self.PX_OFFSET = -3
        self.PY_OFFSET = 43
        self.update_board()     # 第一次启动更新self
    

    def update_board(self):   # 更新棋盘状态    
        def print_board(board):
            print("-------------")
            for i in range(0, 9, 3):
                print("|", end=' ')
                for j in range(3):
                    print(board[i+j] if board[i+j] != 0 else '.', end=' | ')
                print("\n-------------")

        time.sleep(2)  # 等待棋盘稳定
        self.center_points      = cam.get_center_points()
        self.board_chess_colors = cam.get_board_chess_colors()
        logger.info(f"更新棋盘状态")

        if self.center_points:
            logger.info(f"棋盘格中心点: {self.center_points}")
            logger.info(f"棋盘格颜色分布: {self.board_chess_colors}")
            print_board(self.board_chess_colors)
            return self.center_points
        else:
            logger.error("没有找到棋盘的位置信息")
            return False

    def update_chess_pos(self):  # 更新背景棋子位置
        time.sleep(2)  # 等待棋盘稳定
        self.black_coords = cam.get_black_coords()
        self.white_coords = cam.get_white_coords()
        logger.info("更新背景棋子位置")
        logger.info(f"黑色棋子数量: {len(self.black_coords)}, 位置: {self.black_coords}")
        logger.info(f"白色棋子数量: {len(self.white_coords)}, 位置: {self.white_coords}")
        
        if len(self.black_coords) < 1 or len(self.white_coords) < 1:
            logger.error("没有找到棋子的位置信息。")
            return False

    def to_printer_coord(self, img_coord):
        printer_coord = [0, 0]
        logger.info(f"转换坐标: {img_coord}")
        printer_coord[0] = int(img_coord[0] / 10 * 2) + 10 + self.PX_OFFSET
        printer_coord[1] = 251 - int(img_coord[1] / 10 * 2) - 60 + self.PY_OFFSET # 翻转y轴
        return printer_coord
    
    def pick_and_place(self, chess_color, grid_number):  # 抓取棋子并放置

        bot = BambuRobot(reset=False)    # 重新初始化机器人, 以防掉线

        color_str = {self.BLACK: "黑色", self.WHITE: "白色" }

        logger.warning(f"正在拾取 {color_str[chess_color]} 棋，放置到 {grid_number} 号方格。")

        if chess_color == self.BLACK:
            if len(self.black_coords) < 1:
                logger.error("没有找到黑色棋子的位置信息。")
                return False
            from_x, from_y = self.to_printer_coord(self.black_coords[0])

        elif chess_color == self.WHITE:
            if len(self.white_coords) < 1:
                logger.error("没有找到白色棋子的位置信息。")
                return False
            from_x, from_y = self.to_printer_coord(self.white_coords[0])

        if len(self.center_points) < 9:
            logger.error(f"棋盘上没有 {grid_number} 号方格的位置信息。")
            return False

        to_x, to_y = self.to_printer_coord(self.center_points[grid_number-1])

        logger.info(f"正在将 {color_str[chess_color]} 棋从 {from_x} , {from_y} 移动到 {to_x} , {to_y}")
        
        bot.capture_piece(from_x, from_y)  # 放置棋子
        bot.release_piece(to_x, to_y)

        bot.show_chess_board()

        return True

    def mode_1(self):
        
        logger.info("进入模式 1: 装置将任意 1 颗黑棋子放置到 5 号方格中。\n")

        bot.show_chess_board()  # 展示棋盘

        self.update_chess_pos()  # 更新背景棋子位置
        self.update_board()

        self.pick_and_place(chess_color=self.BLACK, grid_number=5) # 放置棋子 5 号方格
        
        time.sleep(1)

        logger.info("题目1 任务要求完成")
       

    def mode_2(self):
        bot = BambuRobot(reset=False)    # 重新初始化机器人, 以防掉线
   
        logger.info("进入模式 2: 将任意 2 颗黑棋子和 2 颗白棋子依次放置到指定方格中。")

        bot.show_chess_board()  # 展示棋盘

        placed_chess = 0  # 记录已经放置的棋子数量

        while placed_chess < 4:
            bot = BambuRobot(reset=False)    # 重新初始化机器人, 以防掉线
             
            self.update_chess_pos()  # 更新背景棋子位置
            self.update_board()

            logger.info(f"\n正在放置第 {placed_chess + 1} 颗棋子:")
            chess_color = int(input(f"请输入要放置的棋子颜色 (1白色, -1黑色): \n"))

            if chess_color == self.BLACK:
                logger.info("放置黑色棋子")
            elif chess_color == self.WHITE:
                logger.info("放置白色棋子") 
            else:
                logger.error("无效输入，请重新输入。")
                continue

            grid_number = int(input("请输入棋子要放置的位置: "))

            ret = self.pick_and_place(chess_color, grid_number)

            if not ret:
                logger.error("放置棋子失败，请重新尝试。")
                self.update_chess_pos()  # 更新背景棋子位置
                continue

            placed_chess += 1  # 成功放置棋子后增加计数
        
        logger.info("题目2 任务要求完成")

    

    def mode_3(self):
        while True:
            self.update_chess_pos()        
            logger.info("进入模式 3: 人机对弈。")
            logger.info("\n若人先放置黑棋, 输入数字0回车, 人先手; \n输入1~9数字后回车, 机器执黑棋先手")

            grid_number = input("请输入数字: ")

            if grid_number == '0':
                logger.info("人先手执黑棋 (-1)")
                human_color = -1
                bot_color   = 1
                self.last_board_chess_colors = self.update_board() # 初始化上一次的棋盘
                break

            elif grid_number in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                logger.info("机器先手, 人执白棋 (1)")
                bot_color   = -1
                human_color = 1
                self.pick_and_place(bot_color, int(grid_number))
                self.last_board_chess_colors = self.update_board() # 初始化上一次的棋盘
                break

            else:
                logger.error("输入错误，请重新输入")
                continue

       
        ttt_ai = TicTacToeAI(bot_color, human_color, 0)
        logger.info("游戏正式开始")

        while True:
            done = input("人执完棋后, 请输入数字 0 继续: \n")
            if done == '0':
                # 更新棋盘
                self.update_board()
                self.update_chess_pos()

                # 检查棋子变化
                changes_list = ttt_ai.find_changes(self.last_board_chess_colors, self.board_chess_colors)
                fix_changes = ttt_ai.find_board_fix(changes_list)

                if fix_changes is not None:  # 如果需要修复, 进行修复
                    from_x, from_y = self.to_printer_coord(self.center_points[fix_changes[0]])
                    to_x, to_y     = self.to_printer_coord(self.center_points[fix_changes[1]])
                    
                    bot.capture_piece(from_x, from_y)  # 放置棋子
                    bot.release_piece(to_x, to_y)

                    bot.show_chess_board()
                    logger.info("修复完成, 继续游戏")
                    continue
                
                # 机器人计算最佳落点并下棋
                best_pos = ttt_ai.find_best_move(self.board_chess_colors, bot_color)
                self.pick_and_place(bot_color, best_pos+1)  # 是因为python的数组索引从0开始
                
                # 检查游戏是否结束
                is_win = ttt_ai.check_game_over(self.board_chess_colors)
                if is_win:
                    if is_win == 99:
                        logger.info("游戏结束, 双方 平局") 
                    else:
                        logger.info(f"游戏结束, 获胜方为: {is_win}")
                    break
            else:
                logger.error("输入错误，请重新输入")
                continue

            

 
    def run(self):
        while True:
            bot.show_chess_board()  # 展示棋盘  
            print("\n--------------------------------------")
            print("选择模式：")
            print("1: 模式 1 - 放置 1 颗黑棋到 5 号方格")
            print("2: 模式 2 - 放置 2 颗黑棋和 2 颗白棋")
            print("3: 模式 3 - 人机对弈")
            print("q: 退出")
            choice = input("输入你的选择: ")
            print("--------------------------------------")

            if choice == '1':
                self.mode_1()
            elif choice == '2':
                self.mode_2()
            elif choice == '3':
                self.mode_3()
            elif choice == 'q':
                logger.info("退出程序。")
                break
            else:
                logger.error("无效选择，请重新输入。")


if __name__ == "__main__":
    chess_bot = ChessBot()
    chess_bot.run()

print("结束所有")