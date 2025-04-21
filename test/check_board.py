
prev = [1, 1, 0, 1]
current = [1, 0, 1, 1]
ls = []

for i in range(len(prev)):
    prev_val = prev[i]
    curr_val = current[i]
    
    dx =  curr_val - prev_val
    ls.append(dx)

print(ls)

if sum(ls) == 0:
    print("没有棋子被篡改")
else:
    print("有棋子被篡改")