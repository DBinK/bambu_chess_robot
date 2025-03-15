import random

class TicTacToe:
    def __init__(self):
        self.board = [[' ']*3 for _ in range(3)]
        self.players = ['X', 'O']
        self.current_player = self.players[0]
        self.ai_player = self.players[1]

    def print_board(self):
        """打印当前棋盘状态"""
        print("-------------")
        for row in self.board:
            print("|", end=' ')
            for cell in row:
                print(cell if cell != ' ' else '.', end=' | ')
            print("\n-------------")

    def get_empty_positions(self):
        """获取所有空位置坐标"""
        return [(i, j) for i in range(3) for j in range(3) if self.board[i][j] == ' ']

    def check_win(self, player):
        """检查指定玩家是否胜利"""
        # 检查行和列
        for i in range(3):
            if all(self.board[i][j] == player for j in range(3)):  # 检查行
                return True
            if all(self.board[j][i] == player for j in range(3)):  # 检查列
                return True
        # 检查对角线
        if all(self.board[i][i] == player for i in range(3)):  # 主对角线
            return True
        if all(self.board[i][2-i] == player for i in range(3)):  # 副对角线
            return True
        return False

    def switch_player(self):
        """切换玩家"""
        self.current_player = self.players[1] if self.current_player == self.players[0] else self.players[0]

    def evaluate_move(self, pos, player):
        """评估指定位置的得分"""
        temp_board = [row.copy() for row in self.board]
        temp_board[pos[0]][pos[1]] = player
        score = 0
        opponent = self.switch_player()

        # 立即胜利检查
        if self.check_win(temp_board, player):
            return float('inf')

        # 防御价值计算
        temp_opponent = [row.copy() for row in self.board]
        temp_opponent[pos[0]][pos[1]] = opponent
        if self.check_win(temp_opponent, opponent):
            return float('inf')  # 必须防御的位置优先级最高

        # 进攻得分（己方两子连线）
        for line in [[(i,j) for j in range(3)] for i in range(3)] + [[(j,i) for j in range(3)] for i in range(3)]:
            line_values = [temp_board[i][j] for (i,j) in line]
            if line_values.count(player) == 2 and ' ' in line_values:
                score += 10

        # 防御得分（对手两子连线）
        for line in [[(i,j) for j in range(3)] for i in range(3)] + [[(j,i) for j in range(3)] for i in range(3)]:
            line_values = [temp_board[i][j] for (i,j) in line]
            if line_values.count(opponent) == 2 and ' ' in line_values:
                score += 5

        # 位置权重（中心>角>边）
        if pos == (1,1):
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
            # 优先处理直接胜利或必须防御的情况
            temp_self = [row.copy() for row in self.board]
            temp_self[pos[0]][pos[1]] = player
            if self.check_win(temp_self, player):
                return pos

            temp_oppo = [row.copy() for row in self.board]
            temp_oppo[pos[0]][pos[1]] = self.switch_player()
            if self.check_win(temp_oppo, self.switch_player()):
                return pos  # 必须防御的位置

            # 常规评估
            score = self.evaluate_move(pos, player)
            if score > max_score:
                max_score = score
                best_pos = pos

        # 如果所有位置评估相同, 随机选择一个合法位置
        return best_pos if best_pos else random.choice(empty)

    def player_move(self):
        """处理玩家回合"""
        while True:
            try:
                move = int(input("请输入落子位置 (1-9): ")) - 1
                row, col = divmod(move, 3)
                if 0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == ' ':
                    return (row, col)
                print("位置无效, 请重新输入")
            except ValueError:
                print("请输入数字1-9")

    def play(self):
        print(f"游戏开始！玩家: {self.players[0]}, AI: {self.players[1]}")

        while True:
            self.print_board()
            if self.current_player == self.ai_player:
                print("AI正在思考...")
                pos = self.find_best_move(self.ai_player)  # 寻找最优落子位置
            else:
                pos = self.player_move()  # 处理玩家回合

            self.board[pos[0]][pos[1]] = self.current_player  # 落子到棋盘数组

            if self.check_win(self.current_player):
                self.print_board()
                print(f"{self.current_player} 获胜！")
                break

            if len(self.get_empty_positions()) == 0:
                self.print_board()
                print("平局！")
                break

            self.switch_player()  # 切换玩家

if __name__ == "__main__":
    game = TicTacToe()
    game.play()