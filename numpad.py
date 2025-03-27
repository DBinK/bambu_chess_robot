import sys
import time
from loguru import logger

class ChessBot:
    def __init__(self):
        self.state = 'mode_1'  # 初始模式为模式 1
        self.BLACK = "-"
        self.WHITE = "+"

    def mode_1(self):
        logger.info("进入模式 1: 装置将任意 1 颗黑棋子放置到 5 号方格中。\n")
        grid_number = 5
        chess_color = self.WHITE  # 黑棋
        self.pick_and_place(chess_color, grid_number)  # 实现将任意 1 颗黑棋子放到方格 5 的逻辑

        logger.info("题目1 任务要求完成")
       

    def mode_2(self):
        logger.info("进入模式 2: 将任意 2 颗黑棋子和 2 颗白棋子依次放置到指定方格中。")

        placed_chess = 0  # 记录已经放置的棋子数量

        while placed_chess < 4:
            logger.info(f"\n正在放置第 {placed_chess + 1} 颗棋子:")
            chess_color = input(f"请输入要放置的棋子颜色 (+号白色, -号黑色): \n")

            if chess_color == self.BLACK:
                logger.info("放置白色棋子")
            elif chess_color == self.WHITE:
                logger.info("放置黑色棋子")
            else:
                logger.error("无效输入，请重新输入。")
                continue

            grid_number = input("请输入棋子要放置的位置: ")
            self.pick_and_place(chess_color, grid_number)
            placed_chess += 1  # 成功放置棋子后增加计数
        
        logger.info("题目2 任务要求完成")
    

    def mode_3(self):
        logger.info("进入模式 3: 人机对弈。")
        logger.info("\n若人先放置黑棋, 输入数字0回车, 人先手; \n输入1~9数字后回车, 机器执黑棋先手")

        init_board = False

        while not init_board:
            
            grid_number = input("请输入数字: ")

            if grid_number == '0':
                logger.info("人先手")
                bot_color = self.WHITE
                init_board = True

            elif grid_number in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                logger.info("机器先手")
                self.pick_and_place(self.WHITE, grid_number)
                bot_color = self.BLACK
                init_board = True
                
            else:
                logger.error("输入错误，请重新输入")
                continue
        
        logger.info("游戏正式开始")

        self.calculate_next_move()

    def pick_and_place(self, chess_color, grid_number):
        # 这里是拾取棋子的逻辑
        color_str = {
            self.BLACK: '白',
            self.WHITE: '黑'
        }
        logger.warning(f"正在拾取 {color_str[chess_color]} 棋，放置到 {grid_number} 号方格。")
        pass
        time.sleep(1)
        logger.warning(f"{color_str[chess_color]} 棋已放置到 {grid_number} 号方格。\n")

    def calculate_next_move(self):
        # 这里是计算装置下一步棋的逻辑
        logger.info("计算装置需要落子的位置...")

    def run(self):
        while True:
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