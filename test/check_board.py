import re
from numpy import fix


def find_board_changes(state_before, state_after):
    # 检查输入是否合法
    if len(state_before) != 9 or len(state_after) != 9:
        raise ValueError("输入列表长度必须为9")
    
    changes = []  # 存储变化信息
    
    # 遍历每个位置
    for i in range(9):
        if state_before[i] != state_after[i]:
            changes.append((i, state_before[i], state_after[i]))
    
    return changes

# 示例输入
state_before =  [1, 0, 0, 
                1, -1, 0, 
                0, 0, 1]

state_after =  [1, 0, 0, 
                1, -1, 0, 
                1, 1, 0]

# 调用函数
changes = find_board_changes(state_before, state_after)

# 输出结果
print("变化的棋子：", changes)

def find_board_fix(changes):

    fix_changes = [0, 0]

    if len(changes) == 2:

        for pos in changes:
            if pos[2] == 1:    # 找到棋子被移动后的位置
                fix_changes[0] = pos[0]

            elif pos[2] == 0:  # 找到棋子被移动前的位置
                fix_changes[1] = pos[0]

        print("需要修正的变化：", fix_changes)
        return fix_changes
    
    print("棋子移动次数不为2, 无需修正")
    return None


find_board_fix(changes)