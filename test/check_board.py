
# prev = [1, 1, 0, 1]
# current = [1, 1, -1, 1]

import numpy as np

# 初始棋盘状态列表
prev = [1, 1, 0, 1]
current = [1, 0, 1, 1]

# 将列表转换为numpy数组
prev_array = np.array(prev)
current_array = np.array(current)

# 矩阵减法
board_changes = current_array + prev_array

# 打印结果
print("prev_array:", prev_array)
print("current_array:", current_array)
print("board_changes:", board_changes)

# 检查棋子是否增加
if sum(current_array - prev_array) == 0:
    print("棋子数量无变化了, 检查棋子位置是否有篡改")
else:
    print("棋子数量或颜色变化了")

prev_pos = board_changes - prev_array
current_pos = board_changes - current_array

p = np.where(prev_pos == 0)[0]
c = np.where(current_pos == 0)[0]

print("prev_pos:", p)
print("current_pos:", c)
