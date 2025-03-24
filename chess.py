import cv2
import numpy as np

from colors import YELLOW_LOWER, YELLOW_UPPER



def remove_background(img, lower, upper):
    
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # 转换为HSV格式

    lower_color = np.array(lower)  # 颜色范围下限
    upper_color = np.array(upper)  # 颜色颜色上限

    mask = cv2.inRange(hsv_img, lower_color, upper_color)  # 创建掩膜

    # kernel = np.ones((5, 5), np.uint8)             # 定义结构元素  
    # mask = cv2.erode(mask, kernel, iterations=5)   # 收缩操作
    # mask = cv2.dilate(mask, kernel, iterations=5)  # 膨胀操作
 
    cv2.bitwise_not(mask, mask)  # 翻转掩膜 

    cv2.namedWindow('Mask', cv2.WINDOW_NORMAL)   # 显示掩膜
    cv2.imshow('Mask', mask)

    return mask

def detect_chess_contours(img):
    """ 从背景识别棋子轮廓 """

    mask = remove_background(img, YELLOW_LOWER, YELLOW_UPPER)  # 移除黄色背景
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # 查找轮廓
    
    filtered_contours = []

    for contour in contours:  # 提取位置和颜色

        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)

        if perimeter < (50 * 4):  # 过滤小的轮廓 
            continue

        # circularity = (4 * np.pi * area) / (perimeter * perimeter)
        # print(f"圆形度: {circularity}")
        
        # 计算长宽比
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h
        # print(f"长宽比: {aspect_ratio}")
        
        # 计算 最小外接圆 与 轮廓 的面积之比
        (x, y), radius = cv2.minEnclosingCircle(contour)
        min_circle_area = np.pi * radius ** 2
        area_ratio = min_circle_area / area
        # cv2.circle(img, (int(x), int(y)), int(radius), (0, 0, 255), 2) # 绘制最小外接圆
        # print(f"最小外接圆面积与轮廓面积之比: {area_ratio}")
        
        # 过滤条件
        if (area_ratio < 1.5)  and (0.95 < aspect_ratio < 1.05):
            filtered_contours.append(contour)

    return filtered_contours      

def classify_background_chess_color(img, contours):
    """ 根据轮廓颜色分类棋子 """

    black_contours = []
    white_contours = []

    for contour in contours:
        # 计算轮廓的平均颜色
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, -1)  # 填充轮廓以获取颜色
        mean_val = cv2.mean(img, mask=mask)  # 计算平均色彩

        # 判断颜色是否接近黑色或白色
        if mean_val[0] < 100 and mean_val[1] < 100 and mean_val[2] < 100:  # 接近黑色
            black_contours.append(contour)
        elif mean_val[0] > 150 and mean_val[1] > 150 and mean_val[2] > 150:  # 接近白色
            white_contours.append(contour)

    return black_contours, white_contours

def contours_to_positom(contours):
    """ 将轮廓转换为棋子位置 """

    contours_positions = []

    for contour in contours:
        M = cv2.moments(contour)  # 计算轮廓的中心点
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            contours_positions.append((cX, cY))

    return contours_positions

def draw_chess(img, contours, color):
    """ 在图像上绘制棋子轮廓 """

    img_chess = img.copy()

    for contour in contours:
        cv2.drawContours(img_chess, [contour], -1, color, 2)

    chess_positions = contours_to_positom(contours)
    for chess_position in chess_positions:
        cv2.circle(img_chess, chess_position, 7, color, -1)
        cv2.putText(img_chess, f" {chess_position[0], chess_position[1]}", chess_position, cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    return img_chess

def chess_detect(img, debug=False):
    """ 从背景识别棋子位置 """

    chess_contours = detect_chess_contours(img)  # 获取所有棋子轮廓

    if len(chess_contours) == 0:  # 如果没有找到任何棋子轮廓，则返回空列表
        return [], []
    
    black_contours, white_contours = classify_background_chess_color(img, chess_contours)  # 按颜色分类
    black_coords = contours_to_positom(black_contours)  # 获取黑棋子位置
    white_coords = contours_to_positom(white_contours)  # 获取白棋子位置

    print(f"黑色棋子数量: {len(black_coords)}, 位置: {black_coords}")
    print(f"白色棋子数量: {len(white_coords)}, 位置: {white_coords}")
 
    if debug:  # 调试模式
        img_chess = draw_chess(img, black_contours, (255, 0, 0))
        img_chess = draw_chess(img_chess, white_contours, (0, 0, 255))
        cv2.namedWindow("img_chess", cv2.WINDOW_NORMAL)
        cv2.imshow("img_chess", img_chess)

    return black_coords, white_coords


##############################################################################################


def sort_corners(corners):
    """ 根据角度对四个角点进行排序，确保顺序为左上角、右上角、右下角、左下角。  """
    
    center_x = sum(x for x, y in corners) / 4  # 计算质心
    center_y = sum(y for x, y in corners) / 4

    def angle_from_center(point):  # 计算每个角点相对于质心的角度
        return np.arctan2(point[1] - center_y, point[0] - center_x)
    
    corners = sorted(corners, key=angle_from_center)  # 根据角度对角点进行排序

    corners = [corners[0], corners[1], corners[2], corners[3]]  # 重新排列顺序为左上角、右上角、右下角、左下角
    
    return corners

def detect_borad_corners(img):
    """ 从背景识别棋盘角点 """
    
    # blurred_img = cv2.GaussianBlur(img, (7, 7), 0)
    # opened_img = cv2.morphologyEx(blurred_img, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 100, apertureSize=3)    # 使用Canny边缘检测
    # cv2.namedWindow('edges', cv2.WINDOW_NORMAL)
    # cv2.imshow('edges', edges)

    contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)   # 查找轮廓
  
    if contours:  # 找到最大的轮廓
        largest_contour = max(contours, key=cv2.contourArea)
        
        # 对轮廓进行多边形逼近
        epsilon = 0.1 * cv2.arcLength(largest_contour, True)
        approx = cv2.approxPolyDP(largest_contour, epsilon, True)
        
        if len(approx) == 4:  # 确保是四边形
            # 获取四个角点的坐标
            corners = [(int(point[0][0]), int(point[0][1])) for point in approx]
            corners = sort_corners(corners)

            print("棋盘角点:", corners)

            return corners
        
        else:
            print("没有找到合适的轮廓")
            return []
    else:
        print("没有找到合适的轮廓")
        return []
        

def homo_trans(corners, w=300, h=300):
    """ 计算 将图像中的特定四边形区域 变换为目标长方形区域 所需的矩阵 H """

    image_points  = np.array(corners, dtype='float32')  # 定义图像中的长方形四个顶点（根据你实际值设定) 
    object_points = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype='float32')  # 定义目标长方形的四个顶点
    H_matrix , _  = cv2.findHomography(image_points, object_points)  # 计算同伦变换矩阵

    H_inv = np.linalg.inv(H_matrix)  # 计算反向变换矩阵

    return H_matrix, H_inv


def trans_coord(point, matrix):
    """ 输入一个坐标，输出经过矩阵变换后的坐标 """
    point_homogeneous = np.array([point[0], point[1], 1])
    transformed_point = matrix @ point_homogeneous
    return int(transformed_point[0] / transformed_point[2]), \
           int(transformed_point[1] / transformed_point[2])


def get_center_points(H_inv, w=300, h=300):
    """ 获取棋盘格中心点坐标 """
    center_points = []
    raw_points = [(1/6*w, 1/6*h), (3/6*w, 1/6*h), (5/6*w, 1/6*h), \
                  (1/6*w, 3/6*h), (3/6*w, 3/6*h), (5/6*w, 3/6*h), \
                  (1/6*w, 5/6*h), (3/6*w, 5/6*h), (5/6*w, 5/6*h)]
    for point in raw_points:
        center_points.append(trans_coord(point, H_inv))

    # print("棋盘网格的中心点:", center_points)
    return center_points

def get_point_color(img, center_point, radius):
    """ 获取指定点周围区域的平均颜色 """

    x, y = center_point     # 定义周围区域的坐标
    x1 = max(0, x - radius)
    x2 = min(img.shape[1], x + radius)
    y1 = max(0, y - radius)
    y2 = min(img.shape[0], y + radius)
    
    region = img[y1:y2, x1:x2]            # 获取周围区域并计算平均颜色
    average_color = cv2.mean(region)[:3]  # 获取 BGR 平均值并忽略 alpha 通道
 
    average_color = tuple(int(c) for c in average_color)  # 对平均颜色进行取整

    # cv2.circle(img, center_point, radius, (255, 0, 0), 2)  # 检查指定点采样半径用

    return average_color

def classify_borad_chess_color(img, center_points):
    """ 获取棋盘格上棋子的颜色 """

    chess_colors = []

    for point in center_points:
        color = get_point_color(img, point, 20)

        # 判断颜色
        if color > (200, 200, 200):  # 白色棋子
            color = 1
        elif color < (50, 50, 50):  # 黑色棋子
            color = -1
        else:  # 其他颜色
            color = 0

        chess_colors.append(color)
        # print(f"棋子: {center_points.index(point)+1}, 颜色: {color}")

    print("棋盘格颜色:", chess_colors)

    return chess_colors

def draw_chess_borad(img, corners, center_points, chess_colors):
    """ 绘制棋盘格调试信息 """

    draw_img = img.copy()

    for i in range(len(corners)):  # 绘制棋盘顶点和连线   
        cv2.line(draw_img, corners[i], corners[(i + 1) % len(corners)], (0, 255, 0), 5)
    for point in corners:
        cv2.circle(draw_img, point, 10, (255, 0, 0), -1)
        cv2.putText(draw_img, f" P{str(corners.index(point) + 1)}: {point}", point, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 100, 0), 1)
    
    for point in center_points:    # 绘制棋盘中心点和号码
        
        if chess_colors[center_points.index(point)] == 1:       # 白色棋子
            cv2.circle(draw_img, point, 4, (150, 150, 150), -1)
            cv2.putText(draw_img, str(center_points.index(point) + 1), point, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        elif chess_colors[center_points.index(point)] == -1:    # 黑色棋子
            cv2.circle(draw_img, point, 4, (150, 150, 150), -1)
            cv2.putText(draw_img, str(center_points.index(point) + 1), point, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        else:
            cv2.circle(draw_img, point, 3, (0, 200, 0), -1)     # 无棋子

    return draw_img


def chess_borad_detect(img, debug=False):
    """ 棋盘格识别总函数 """

    corners = detect_borad_corners(img)  # 获取棋盘格角点

    if len(corners) == 0:
        print("没有检测到棋盘")
        return [], []
    
    H_matrix, H_inv = homo_trans(corners)     # 计算透视变换矩阵
    center_points = get_center_points(H_inv)  # 获取棋盘格中心点
    chess_colors = classify_borad_chess_color(img, center_points)

    if debug:  # 调试模式
        draw_img = draw_chess_borad(img, corners, center_points, chess_colors)
        cv2.namedWindow('img_borad', cv2.WINDOW_NORMAL)
        cv2.imshow('img_borad', draw_img)

    return center_points, chess_colors


if __name__ == '__main__':

    print("开始测试")
    # img_load = 'img\chessboard_y1.jpg'
    img_load = 'img\chessboard_f2.jpg'
    img_raw = cv2.imread(img_load)

    cv2.namedWindow('img_raw', cv2.WINDOW_NORMAL)
    cv2.imshow('img_raw', img_raw)
    
    center_points, chess_colors = chess_borad_detect(img_raw, True)

    black_coords, white_coords = chess_detect(img_raw, True)

    # cv2.namedWindow('Detected Circles and Chessboard Corners', cv2.WINDOW_NORMAL)
    # cv2.imshow('Detected Circles and Chessboard Corners', img0)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
