def find_changes(state_before, state_after):
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
                0, 0, 1]

# 调用函数
result = find_changes(state_before, state_after)

# 输出结果
print("变化的棋子：", result)