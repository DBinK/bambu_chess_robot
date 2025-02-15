from bambu_connect import BambuClient
from config import hostname, access_code, serial

bambu_client = BambuClient(hostname, access_code, serial)

# 默认位置
position_x  = 128
position_y  = 128
position_z  = 10

def send_gcode(gcode_command):
    # 发送 G-code 命令
    bambu_client.send_gcode(gcode_command)
    print(f"发送了 G-code 命令: {gcode_command}")

def reset():
    send_gcode("G28") # 回原点

def lock_motor():
    send_gcode("M17 ; 锁定所有电机")

def unlock_motor():
    send_gcode("M18 ; 解锁所有电机")

# 绝对坐标移动
def move(px, py, pz, speed=None):
    global position_x, position_y, position_z

    # 确保 x, y, z 在 [10, 200] 范围内
    for distance in [px, py, pz]:
        if distance < 10 or distance > 200:
            print(f"{distance} 不在 [10, 200] 范围内")
            return False
    
    # 更新到全局变量
    position_x, position_y, position_z = px, py, pz
    
    send_gcode("G90 ; 设置为绝对坐标") 
    send_gcode(f"G0 X{px} Y{py} Z{pz} {'F' + str(speed) if speed else ''}")
    send_gcode("M400 ; 等待所有命令执行完毕") 

    print(f"已移动到 ({position_x}, {position_y}, {position_z})")

    notice_finish()

    return True

def move_relative(dx, dy, dz, speed=None):
    global position_x, position_y, position_z

    px, py, pz = position_x, position_y, position_z

    # 更新位置
    px += dx
    py += dy
    pz += dz

    # 确保 x, y, z 在 [10, 200] 范围内
    for distance in [px, py, pz]:
        if distance < 10 or distance > 200:
            print(f"{distance} 不在 [10, 200] 范围内")
            return False
    
    # 更新到全局变量
    position_x, position_y, position_z = px, py, pz
    
    send_gcode("G91 ; 设置为相对坐标") 
    send_gcode(f"G0 X{dx} Y{dy} Z{dz} {'F' + str(speed) if speed else ''}")
    send_gcode("M400 ; 等待所有命令执行完毕")
    send_gcode("G90 ; 设置回绝对坐标") 

    print(f"已移动到 ({position_x}, {position_y}, {position_z})")

    notice_finish()
    return True

def move_x(x, speed=None):
    return move(x, position_y, position_z, speed)

def move_y(y, speed=None):
    return move(position_x, y, position_z, speed)

def move_z(z, speed=None):
    return move(position_x, position_y, z, speed)

def move_relative_x(dx, speed=None):
    return move_relative(dx, 0, 0, speed)

def move_relative_y(dy, speed=None):
    return move_relative(0, dy, 0, speed)

def move_relative_z(dz, speed=None):
    return move_relative(0, 0, dz, speed)

def notice_finish():
    bambu_client.send_gcode("""
        ;
        ;music_long: 15
        M17
        M400 S1
        M1006 S1
        M1006 L70 M70 N99
        M1006 C37 D25 M69 
        M1006 W
               """)



if __name__ == "__main__":

    # gcode_command = "G28"   # 回原点

    # gcode_command = "G0 X50 Y50 Z10 F3000 ; 以 300 mm/min 的速度移动到 (50, 50, 10)"
    # gcode_command = "G1 X128 Y128 Z10 F3000 ; 以 300 mm/min 的速度移动到 (50, 50, 10)"

    # send_gcode(gcode_command)

    # move(50, 50, 10, 12000)

    reset()

    # move(128, 128, 10, 12000)
    # move_relative(-50, -50, 10, 12000)
    # move_relative(-50, -50, 10, 12000)
    # move_relative(-50, -50, 10, 12000)
    # move_relative(50, 50, 50, 12000)
    # move_relative(50, 50, 50, 12000)
    # move_relative(50, 50, 50, 12000)
    # move_relative(50, 50, 50, 12000)
    
    # move_relative(0, 0, 50, 12000)
    # move_relative(0, 0, 50, 12000)
    # move_relative(0, 0, 50, 12000)
    # move_relative(0, 0, 50, 12000)
