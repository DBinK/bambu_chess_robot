import random

class TicTacToeAI:
    def __init__(self, player1=-1, player2=1, empty=0):
        self.players = [player1, player2]
        self.empty = empty
        self.win_lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # 行
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # 列
            [0, 4, 8], [2, 4, 6]              # 对角线
        ]

    def get_empty_positions(self, board):
        return [i for i in range(9) if board[i] == self.empty]

    def check_win(self, board, player):
        for line in self.win_lines:
            if all(board[i] == player for i in line):
                return True
        return False

    def check_game_over(self, board):
        """
        检查游戏是否结束
        返回值:
        - False: 游戏未结束
        - -1 / 1: 某玩家获胜
        - 99: 平局
        """
        for player in self.players:
            if self.check_win(board, player):
                return player  # 返回获胜玩家 ID
        
        if not self.get_empty_positions(board):
            return 99  # 平局返回99
        
        return False   # 未结束返回False

    def evaluate_move(self, board, pos, player):
        temp_board = board.copy()
        temp_board[pos] = player
        score = 0
        opponent = self.players[1] if player == self.players[0] else self.players[0]

        # 检查当前玩家是否直接胜利
        if self.check_win(temp_board, player):
            return float('inf')

        # 防御得分
        for line in self.win_lines:
            values = [board[i] for i in line]
            
            if values.count(opponent) == 2 and self.empty in values:
                empty_pos = next((line[idx] for idx, val in enumerate(values) if val == self.empty), None)
                if empty_pos == pos:
                    score += 50 if values.count(opponent) == 1 else 100

        # 进攻得分
        for line in self.win_lines:
            values = [temp_board[i] for i in line]
            if values.count(player) == 2 and self.empty in values:
                score += 10

        # 位置权重
        position_weights = [2, 1, 2, 
                           1, 3, 1, 
                           2, 1, 2]
        score += position_weights[pos]

        return score

    def find_best_move(self, board, current_player):
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
        
        print(f"AI选择位置: {best_pos}")

        return best_pos
    
    def find_changes(self, board_before, board_after):
        # 检查输入是否合法
        if len(board_before) != 9 or len(board_after) != 9:
            raise ValueError("输入列表长度必须为9")
        
        changes = []  # 存储变化信息
        
        # 遍历每个位置
        for i in range(9):
            if board_before[i] != board_after[i]:
                changes.append((i, board_before[i], board_after[i]))
        
        return changes


class TicTacToeGame:
    def __init__(self, player1=-1, player2=1, empty=0):
        self.ai = TicTacToeAI(player1, player2, empty)
        self.board = [empty] * 9
        self.current_player = player1
        self.player1 = player1
        self.player2 = player2
        self.empty = empty

    def print_board(self):
        print("-------------")
        for i in range(0, 9, 3):
            print("|", end=' ')
            for j in range(3):
                print(self.board[i+j] if self.board[i+j] != self.empty else '.', end=' | ')
            print("\n-------------")

    def player_move(self):
        while True:
            try:
                move = int(input(f"请输入落子位置 (1-9), 你执{self.current_player}: ")) - 1
                if 0 <= move < 9 and self.board[move] == self.empty:
                    return move
                print("位置无效, 请重新输入")
            except ValueError:
                print("请输入数字1-9")

    def play(self, first_move=0):
        print(f"游戏开始！玩家: {self.player1}, AI: {self.player2}")
        
        if first_move > 0:
            move = first_move - 1
            if 0 <= move < 9 and self.board[move] == self.empty:
                self.board[move] = self.player2
                self.current_player = self.player1
                print(f"AI先手，选择位置: {first_move}")
            else:
                print(f"位置{first_move}无效，AI将随机选择位置")
                empty = self.ai.get_empty_positions(self.board)
                if empty:
                    pos = random.choice(empty)
                    self.board[pos] = self.player2
                    self.current_player = self.player1
        
        while True:
            self.print_board()
            if self.current_player == self.player2:
                print("AI正在思考...")
                pos = self.ai.find_best_move(self.board, self.player2)
                print(f"AI选择位置: {pos + 1}")
            else:
                pos = self.player_move()

            self.board[pos] = self.current_player

            # 使用新的check_game_over函数判断游戏状态
            result = self.ai.check_game_over(self.board)
            if result:
                self.print_board()
                if result == 99:
                    print("平局！")
                else:
                    print(f"{result} 获胜！")
                break

            self.current_player = self.player2 if self.current_player == self.player1 else self.player1


if __name__ == "__main__":
    # game = TicTacToeGame(player1=-1, player2=1, empty=0)
    # first_move = int(input("请输入先手设置(0=人类先手，1-9=AI先手并在对应位置下子): "))
    # game.play(first_move)
    
    ai = TicTacToeAI()

    board = [0, 0, 0, 
             1, -1, 0, 
             0, 0, -1]
    
    best_move = ai.find_best_move(board, 1)  # 返回0-8的索引

    print(f"AI 选择位置: {best_move + 1}")

"""

# 在其他文件中引用

from tictactoe import TicTacToeAI

ai = TicTacToeAI()
board = [0]*9  # 空棋盘
best_move = ai.find_best_move(board, player=1)  # 返回0-8的索引


board = [-1, 1, -1,
         1, -1, 1,
         1, -1, 1]  # 平局示例

result = ai.check_game_over(board)
if result == 'draw':
    print("游戏结束，平局！")
elif result is not None:
    print(f"游戏结束，玩家{result}获胜！")
else:
    print("游戏继续")

"""
