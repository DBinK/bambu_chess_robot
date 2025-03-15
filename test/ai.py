import random

def print_board(board):
    """打印当前棋盘状态"""
    print("-------------")
    for row in board:
        print("|", end=' ')
        for cell in row:
            print(cell if cell != ' ' else '.', end=' | ')
        print("\n-------------")

def get_empty_positions(board):
    """获取所有空位置坐标"""
    return [(i, j) for i in range(3) for j in range(3) if board[i][j] == ' ']

def check_win(board, player):
    """检查指定玩家是否胜利"""
    # 检查行和列
    for i in range(3):
        if all(board[i][j] == player for j in range(3)):  # 检查行
            return True
        if all(board[j][i] == player for j in range(3)):  # 检查列
            return True
    # 检查对角线
    if all(board[i][i] == player for i in range(3)):  # 主对角线
        return True
    if all(board[i][2-i] == player for i in range(3)):  # 副对角线
        return True
    return False

def switch_player(player):
    """切换玩家"""
    return 'X' if player == 'O' else 'O'

def evaluate_move(board, pos, player):
    """评估指定位置的得分"""
    temp_board = [row.copy() for row in board]
    temp_board[pos[0]][pos[1]] = player
    score = 0
    opponent = switch_player(player)
    
    # 立即胜利检查
    if check_win(temp_board, player):
        return float('inf')
    
    # 防御价值计算
    temp_opponent = [row.copy() for row in board]
    temp_opponent[pos[0]][pos[1]] = opponent
    if check_win(temp_opponent, opponent):
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

def find_best_move(board, player):
    """寻找最优落子位置"""
    empty = get_empty_positions(board)
    if not empty:
        return None
    
    best_pos = None
    max_score = -float('inf')
    
    for pos in empty:
        # 优先处理直接胜利或必须防御的情况
        temp_self = [row.copy() for row in board]
        temp_self[pos[0]][pos[1]] = player
        if check_win(temp_self, player):
            return pos
        
        temp_oppo = [row.copy() for row in board]
        temp_oppo[pos[0]][pos[1]] = switch_player(player)
        if check_win(temp_oppo, switch_player(player)):
            return pos  # 必须防御的位置
        
        # 常规评估
        score = evaluate_move(board, pos, player)
        if score > max_score:
            max_score = score
            best_pos = pos
    
    # 如果所有位置评估相同，随机选择一个合法位置
    return best_pos if best_pos else random.choice(empty)

def player_move(board, player):
    """处理玩家回合"""
    while True:
        try:
            move = int(input("请输入落子位置 (1-9): ")) - 1
            row, col = divmod(move, 3)
            if 0 <= row < 3 and 0 <= col < 3 and board[row][col] == ' ':
                return (row, col)
            print("位置无效，请重新输入")
        except ValueError:
            print("请输入数字1-9")

def main():
    board = [[' ']*3 for _ in range(3)]
    players = ['X', 'O']
    random.shuffle(players)  # 随机先手
    current_player = players[0]
    ai_player = players[1]   # AI固定为第二个玩家
    
    print(f"游戏开始！玩家: {players[0]}，AI: {players[1]}")
    
    while True:
        print_board(board)
        
        if current_player == ai_player:
            print("AI正在思考...")
            pos = find_best_move(board, ai_player)
        else:
            pos = player_move(board, current_player)
        
        board[pos[0]][pos[1]] = current_player
        
        if check_win(board, current_player):
            print_board(board)
            print(f"{current_player} 获胜！")
            break
        
        if len(get_empty_positions(board)) == 0:
            print_board(board)
            print("平局！")
            break
        
        current_player = switch_player(current_player)

if __name__ == "__main__":
    main()