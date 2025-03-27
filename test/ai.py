# 我希望这个类的游玩功能和计算决策分开, 便于我在其他py文件引用时, 可以在类初始化时设置代表双方玩家的变量, 空位置变量(比如:人类 -1, 机器人 1, 棋盘空位置 0); 露出里面的 输入棋盘状态, 当前玩家, 计算当前玩家的最优落点功能函数; 输入棋盘状态检测是否胜利的功能函数
import random

class TicTacToe:
    def __init__(self, player1='X', player2='O', empty=0):
        # 初始化棋盘状态
        self.board = [[empty] * 3 for _ in range(3)]
        self.players = [player1, player2]  # 玩家设置
        self.current_player = self.players[0]  # 当前玩家
        self.ai_player = self.players[1]  # AI 玩家

    def print_board(self):
        """打印当前棋盘状态"""
        print("-------------")
        for row in self.board:
            print("|", end=' ')
            for cell in row:
                print(cell if cell != 0 else '.', end=' | ')  # 空位置用 '.' 表示
            print("\n-------------")

    def get_empty_positions(self):
        """获取所有空位置坐标"""
        return [(i, j) for i in range(3) for j in range(3) if self.board[i][j] == 0]

    def check_win(self, player):
        """检查指定玩家是否胜利"""
        for i in range(3):
            if all(self.board[i][j] == player for j in range(3)):  # 检查行
                return True
            if all(self.board[j][i] == player for j in range(3)):  # 检查列
                return True
        if all(self.board[i][i] == player for i in range(3)):  # 主对角线
            return True
        if all(self.board[i][2 - i] == player for i in range(3)):  # 副对角线
            return True
        return False

    def switch_player(self):
        """切换玩家"""
        self.current_player = self.players[1] if self.current_player == self.players[0] else self.players[0]

    def evaluate_move(self, pos, player):
        """评估指定位置的得分"""
        temp_board = [row.copy() for row in self.board]  # 复制当前棋盘
        temp_board[pos[0]][pos[1]] = player  # 落子
        score = 0
        opponent = self.players[1] if player == self.players[0] else self.players[0]  # 获取对手

        if self.check_win(player):  # 检查是否胜利
            return float('inf')

        # 防御得分
        temp_opponent = [row.copy() for row in self.board]
        temp_opponent[pos[0]][pos[1]] = opponent
        if self.check_win(opponent):  # 如果对手胜利
            return float('inf')

        # 进攻得分
        for line in [[(i, j) for j in range(3)] for i in range(3)] + [[(j, i) for j in range(3)] for i in range(3)]:
            line_values = [temp_board[i][j] for (i, j) in line]
            if line_values.count(player) == 2 and 0 in line_values:
                score += 10

        # 防御得分
        for line in [[(i, j) for j in range(3)] for i in range(3)] + [[(j, i) for j in range(3)] for i in range(3)]:
            line_values = [temp_board[i][j] for (i, j) in line]
            if line_values.count(opponent) == 2 and 0 in line_values:
                score += 5

        # 位置权重
        if pos == (1, 1):
            score += 3
        elif (pos[0] % 2 == 0 and pos[1] % 2 == 0):
            score += 2
        else:
            score += 1

        return score

    def find_best_move(self, player):
        """寻找最优落子位置"""
        empty = self.get_empty_positions()
        if not empty:
            return None

        best_pos = None
        max_score = -float('inf')

        for pos in empty:
            score = self.evaluate_move(pos, player)  # 评估得分
            if score > max_score:
                max_score = score
                best_pos = pos

        return best_pos if best_pos else random.choice(empty)  # 随机选择一个位置

    def player_move(self):
        """处理玩家回合"""
        while True:
            try:
                move = int(input("请输入落子位置 (1-9): ")) - 1
                row, col = divmod(move, 3)
                if 0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == 0:
                    return (row, col)
                print("位置无效, 请重新输入")
            except ValueError:
                print("请输入数字1-9")

    def play(self):
        """开始游戏"""
        print(f"游戏开始！玩家: {self.players[0]}, AI: {self.players[1]}")
        while True:
            self.print_board()
            if self.current_player == self.ai_player:
                print("AI正在思考...")
                pos = self.find_best_move(self.ai_player)  # 寻找最优落子位置
            else:
                pos = self.player_move()  # 处理玩家回合

            self.board[pos[0]][pos[1]] = self.current_player  # 落子到棋盘

            if self.check_win(self.current_player):  # 检查胜利
                self.print_board()
                print(f"{self.current_player} 获胜！")
                break

            if len(self.get_empty_positions()) == 0:  # 检查平局
                self.print_board()
                print("平局！")
                break

            self.switch_player()  # 切换玩家

if __name__ == "__main__":
    game = TicTacToe(player1=1, player2=-1, empty=0)  # 使用 -1 和 1 代表玩家
    game.play()