import random

class TicTacToe:
    def __init__(self, player1='X', player2='O', empty=0):
        self.board = [[empty] * 3 for _ in range(3)]
        self.players = [player1, player2]
        self.current_player = self.players[0]
        self.ai_player = self.players[1]

    def print_board(self):
        """打印当前棋盘状态"""
        print("-------------")
        for row in self.board:
            print("|", end=' ')
            for cell in row:
                print(cell if cell != 0 else '.', end=' | ')
            print("\n-------------")

    def get_empty_positions(self):
        """获取所有空位置坐标"""
        return [(i, j) for i in range(3) for j in range(3) if self.board[i][j] == 0]

    def check_win(self, player):
        """检查指定玩家是否胜利"""
        for i in range(3):
            if all(self.board[i][j] == player for j in range(3)):
                return True
            if all(self.board[j][i] == player for j in range(3)):
                return True
        if all(self.board[i][i] == player for i in range(3)):
            return True
        if all(self.board[i][2 - i] == player for i in range(3)):
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
        opponent = self.players[1] if player == self.players[0] else self.players[0]

        # 检查当前玩家是否直接胜利
        if self.check_win(player):
            return float('inf')

        # 防御得分：检查是否阻挡对手的胜利机会
        # 特别处理"间隔两子"的情况（如X _ X）
        for line in [[(i, j) for j in range(3)] for i in range(3)] + \
                    [[(j, i) for j in range(3)] for i in range(3)] + \
                    [[(i, i) for i in range(3)], [(i, 2-i) for i in range(3)]]:
            values = [self.board[i][j] for (i,j) in line]
            
            # 检查是否有间隔两子情况（如X _ X）
            if values.count(opponent) == 2 and 0 in values:
                # 找到空位
                empty_pos = None
                for idx, val in enumerate(values):
                    if val == 0:
                        empty_pos = line[idx]
                        break
                if empty_pos == pos:
                    score += 50  # 高优先级阻挡这种威胁
            
            # 常规阻挡对手即将胜利的情况（如O O _）
            if values.count(opponent) == 2 and 0 in values:
                empty_pos = None
                for idx, val in enumerate(values):
                    if val == 0:
                        empty_pos = line[idx]
                        break
                if empty_pos == pos:
                    score += 100  # 最高优先级阻挡直接胜利

        # 进攻得分：检查是否有潜在胜利机会
        for line in [[(i, j) for j in range(3)] for i in range(3)] + \
                    [[(j, i) for j in range(3)] for i in range(3)] + \
                    [[(i, i) for i in range(3)], [(i, 2-i) for i in range(3)]]:
            values = [temp_board[i][j] for (i,j) in line]
            if values.count(player) == 2 and 0 in values:
                score += 10  # 进攻机会

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
            score = self.evaluate_move(pos, player)
            if score > max_score:
                max_score = score
                best_pos = pos
            elif score == max_score:
                # 随机选择相同分数的位置
                best_pos = random.choice([best_pos, pos])

        return best_pos if best_pos else random.choice(empty)

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

    def play(self, first_move=0):
        """开始游戏
        first_move: 0表示人类先手，1-9表示AI先手并下在对应位置
        """
        print(f"游戏开始！玩家: {self.players[0]}, AI: {self.players[1]}")
        
        # 处理AI先手的情况
        if first_move > 0:
            move = first_move - 1
            row, col = divmod(move, 3)
            if 0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == 0:
                self.board[row][col] = self.ai_player
                self.current_player = self.players[0]  # 切换回人类玩家
                print(f"AI先手，选择位置: {first_move}")
            else:
                print(f"位置{first_move}无效，AI将随机选择位置")
                empty = self.get_empty_positions()
                if empty:
                    pos = random.choice(empty)
                    self.board[pos[0]][pos[1]] = self.ai_player
                    self.current_player = self.players[0]
        
        while True:
            self.print_board()
            if self.current_player == self.ai_player:
                print("AI正在思考...")
                pos = self.find_best_move(self.ai_player)
                print(f"AI选择位置: {pos[0]*3 + pos[1] + 1}")
            else:
                pos = self.player_move()

            self.board[pos[0]][pos[1]] = self.current_player

            if self.check_win(self.current_player):
                self.print_board()
                print(f"{self.current_player} 获胜！")
                break

            if len(self.get_empty_positions()) == 0:
                self.print_board()
                print("平局！")
                break

            self.switch_player()

if __name__ == "__main__":
    game = TicTacToe(player1=1, player2=-1, empty=0)
    
    # 示例用法：
    # game.play()          # 默认人类先手
    # game.play(0)         # 人类先手
    # game.play(5)         # AI先手并在中心位置(5)下子
    # game.play(1)         # AI先手并在左上角(1)下子
    
    first_move = int(input("请输入先手设置(0=人类先手，1-9=AI先手并在对应位置下子): "))
    game.play(first_move)