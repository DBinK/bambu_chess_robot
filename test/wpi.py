import time
import subprocess


# # 运行一个命令并等待其完成
# result = subprocess.run(['gpio', 'mode', '3', 'out'], capture_output=True, text=True)

# # 打印输出
# print(result.stdout)

result = subprocess.run(['gpio', 'mode', '3', 'out'])

while True:
    result = subprocess.run(['gpio', 'write', '3', '0'])
    time.sleep(3)
    result = subprocess.run(['gpio', 'write', '3', '1'])
    time.sleep(3)