import random

class TicTacToeAI:
    def __init__(self, player1=-1, player2=1, empty=0):
        """
        初始化游戏AI
        :param player1: 玩家1的标识（默认人类为-1）
        :param player2: 玩家2的标识（默认AI为1）
        :param empty: 空位置的标识（默认为0）
        """
        self.players = [player1, player2]
        self.empty = empty

    def get_empty_positions(self, board):
        """获取所有空位置坐标"""
        return [(i, j) for i in range(3) for j in range(3) if board[i][j] == self.empty]

    def check_win(self, board, player):
        """检查指定玩家是否胜利"""
        for i in range(3):
            if all(board[i][j] == player for j in range(3)):
                return True
            if all(board[j][i] == player for j in range(3)):
                return True
        if all(board[i][i] == player for i in range(3)):
            return True
        if all(board[i][2 - i] == player for i in range(3)):
            return True
        return False

    def evaluate_move(self, board, pos, player):
        """评估指定位置的得分"""
        temp_board = [row.copy() for row in board]
        temp_board[pos[0]][pos[1]] = player
        score = 0
        opponent = self.players[1] if player == self.players[0] else self.players[0]

        # 检查当前玩家是否直接胜利
        if self.check_win(temp_board, player):
            return float('inf')

        # 防御得分：检查是否阻挡对手的胜利机会
        for line in [[(i, j) for j in range(3)] for i in range(3)] + \
                    [[(j, i) for j in range(3)] for i in range(3)] + \
                    [[(i, i) for i in range(3)], [(i, 2-i) for i in range(3)]]:
            values = [board[i][j] for (i,j) in line]
            
            # 检查间隔两子情况（如X _ X）
            if values.count(opponent) == 2 and self.empty in values:
                empty_pos = next((line[idx] for idx, val in enumerate(values) if val == self.empty), None)
                if empty_pos == pos:
                    score += 50
            
            # 常规阻挡对手即将胜利的情况（如O O _）
            if values.count(opponent) == 2 and self.empty in values:
                empty_pos = next((line[idx] for idx, val in enumerate(values) if val == self.empty), None)
                if empty_pos == pos:
                    score += 100

        # 进攻得分
        for line in [[(i, j) for j in range(3)] for i in range(3)] + \
                    [[(j, i) for j in range(3)] for i in range(3)] + \
                    [[(i, i) for i in range(3)], [(i, 2-i) for i in range(3)]]:
            values = [temp_board[i][j] for (i,j) in line]
            if values.count(player) == 2 and self.empty in values:
                score += 10

        # 位置权重
        if pos == (1, 1):
            score += 3
        elif (pos[0] % 2 == 0 and pos[1] % 2 == 0):
            score += 2
        else:
            score += 1

        return score

    def find_best_move(self, board, current_player):
        """
        寻找最优落子位置
        :param board: 当前棋盘状态（3x3列表）
        :param current_player: 当前玩家标识
        :return: (row, col) 最优落子位置
        """
        empty = self.get_empty_positions(board)
        if not empty:
            return None

        best_pos = None
        max_score = -float('inf')

        for pos in empty:
            score = self.evaluate_move(board, pos, current_player)
            if score > max_score:
                max_score = score
                best_pos = pos
            elif score == max_score:
                best_pos = random.choice([best_pos, pos])

        return best_pos if best_pos else random.choice(empty)


class TicTacToeGame:
    """游戏交互界面，使用TicTacToeAI进行决策"""
    def __init__(self, player1=-1, player2=1, empty=0):
        self.ai = TicTacToeAI(player1, player2, empty)
        self.board = [[empty] * 3 for _ in range(3)]
        self.current_player = player1
        self.player1 = player1
        self.player2 = player2
        self.empty = empty

    def print_board(self):
        """打印当前棋盘状态"""
        print("-------------")
        for row in self.board:
            print("|", end=' ')
            for cell in row:
                print(cell if cell != self.empty else '.', end=' | ')
            print("\n-------------")

    def player_move(self):
        """处理玩家回合"""
        while True:
            try:
                move = int(input(f"请输入落子位置 (1-9), 你执{self.current_player}: ")) - 1
                row, col = divmod(move, 3)
                if 0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == self.empty:
                    return (row, col)
                print("位置无效, 请重新输入")
            except ValueError:
                print("请输入数字1-9")

    def play(self, first_move=0):
        """开始游戏
        :param first_move: 0=人类先手，1-9=AI先手并在对应位置下子
        """
        print(f"游戏开始！玩家: {self.player1}, AI: {self.player2}")
        
        # AI先手逻辑
        if first_move > 0:
            move = first_move - 1
            row, col = divmod(move, 3)
            if 0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == self.empty:
                self.board[row][col] = self.player2
                self.current_player = self.player1
                print(f"AI先手，选择位置: {first_move}")
            else:
                print(f"位置{first_move}无效，AI将随机选择位置")
                empty = self.ai.get_empty_positions(self.board)
                if empty:
                    pos = random.choice(empty)
                    self.board[pos[0]][pos[1]] = self.player2
                    self.current_player = self.player1
        
        while True:
            self.print_board()
            if self.current_player == self.player2:  # AI回合
                print("AI正在思考...")
                pos = self.ai.find_best_move(self.board, self.player2)
                print(f"AI选择位置: {pos[0]*3 + pos[1] + 1}")
            else:  # 玩家回合
                pos = self.player_move()

            self.board[pos[0]][pos[1]] = self.current_player

            # 检查游戏结束条件
            if self.ai.check_win(self.board, self.current_player):
                self.print_board()
                print(f"{self.current_player} 获胜！")
                break

            if not self.ai.get_empty_positions(self.board):
                self.print_board()
                print("平局！")
                break

            # 切换玩家
            self.current_player = self.player2 if self.current_player == self.player1 else self.player1


if __name__ == "__main__":
    # 示例用法
    game = TicTacToeGame(player1=-1, player2=1, empty=0)
    
    # 获取先手设置
    first_move = int(input("请输入先手设置(0=人类先手，1-9=AI先手并在对应位置下子): "))
    game.play(first_move)

"""
# 在其他文件中引用
from tictactoe import TicTacToeAI

# 创建AI实例
ai = TicTacToeAI(player1=-1, player2=1, empty=0)

# 获取AI决策
board = [
    [-1, 0, 1],
    [0, 1, 0],
    [0, 0, -1]
]
best_move = ai.find_best_move(board, player=1)  # 返回(row, col)

# 检查胜利
is_win = ai.check_win(board, player=-1)
"""
