import cv2
import numpy as np

# 图像预处理
def img_preprocess(img):
    blurred_img = cv2.GaussianBlur(img, (7, 7), 0)
    opened_img = cv2.morphologyEx(blurred_img, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    gray_img = cv2.cvtColor(opened_img, cv2.COLOR_BGR2GRAY)
    return gray_img    


# 棋子识别
# 在棋盘格外划定 ROI区域 并对图像进行色彩空间转换，由 BGR 转为 HSV 图像，
# 使颜色能够更好的分离，通过所需的黑白双色二值化阈值，
# 用这两个阈值分离出黑白两色即棋子颜色，再使用 findContours函数 进行轮廓检测，
# 若轮廓中心在 ROI区域 内则其为所需的棋子，记录其坐标
def detect_chess_position(img):
    # 2. 转换颜色空间
    hsv_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 3. 设置颜色范围（以黄色为例）
    lower_yellow = np.array([20, 100, 100])  # 黄色下限
    upper_yellow = np.array([30, 255, 255])  # 黄色上限

    # 4. 创建掩膜
    mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)

    # 收缩膨胀掩膜
    kernel = np.ones((5, 5), np.uint8)  # 定义结构元素
    mask = cv2.erode(mask, kernel, iterations=5)  # 收缩操作
    mask = cv2.dilate(mask, kernel, iterations=5)  # 膨胀操作

    # 翻转掩膜
    cv2.bitwise_not(mask, mask)
    cv2.namedWindow('Mask', cv2.WINDOW_NORMAL)
    cv2.imshow('Mask', mask)

    # 5. 查找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 6. 提取位置和颜色
    filtered_contours = []
    for contour in contours:

        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)

        if perimeter < (50 * 4): # 过滤小的轮廓 
            continue

        # circularity = (4 * np.pi * area) / (perimeter * perimeter)
        # print(f"圆形度: {circularity}")
        
        # 计算长宽比
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h
        print(f"长宽比: {aspect_ratio}")
        
        # 计算 最小外接圆 与 轮廓 的面积之比
        (x, y), radius = cv2.minEnclosingCircle(contour)
        # cv2.circle(image, (int(x), int(y)), int(radius), (0, 0, 255), 2) # 绘制最小外接圆
        min_circle_area = np.pi * radius ** 2
        area_ratio = min_circle_area / area
        
        # 过滤条件
        if (area_ratio < 1.5)  and (0.95 < aspect_ratio < 1.05):
            filtered_contours.append(contour)

    return filtered_contours      

def classify_chess_color(img, contours):
     # 初始化两个列表
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
    
    print(f"黑色棋子数量: {len(black_contours)}")
    print(f"白色棋子数量: {len(white_contours)}")

    return black_contours, white_contours

def draw_chess(img, contour):
    # 计算轮廓的中心点
    M = cv2.moments(contour)

    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        
        # 获取棋子的颜色（在轮廓的中心点位置）
        color = img[cY, cX]
        
        print(f"棋子位置: ({cX}, {cY}), 颜色: {color}")

        # 可视化
        cv2.drawContours(img, [contour], -1, (0, 255, 0), 2)
        cv2.circle(img, (cX, cY), 7, (0, 255, 0), -1)

def chess_detect(img):
    pass
    

# def chess_detect(img):
#     """ 棋子识别, 输入图像, 返回 黑色棋子坐标列表，白色棋子坐标列表  """
#     img_gray = img_preprocess(img)        # 转换为灰度图像
#     circles = cv2.HoughCircles(img_gray, cv2.HOUGH_GRADIENT, dp=1, minDist=25, param1=50, param2=55)
#     if circles is not None:
#         circles = np.uint16(np.around(circles))  # 对圆的圆心坐标和半径四舍五入取整
    
#     black_chess_coords = []
#     white_chess_coords = []

#     for i in circles[0, :]:
#         # 提取圆形区域
#         mask = np.zeros_like(img_gray)
#         cv2.circle(mask, (i[0], i[1]), i[2], (255, 255, 255), -1)
        
#         # 计算圆形区域的平均灰度值
#         mean_val = cv2.mean(img_gray, mask=mask)[0]
        
#         if mean_val < 128:  # 黑色棋子
#             black_chess_coords.append((i[0], i[1]))
#             cv2.circle(img, (i[0], i[1]), i[2], (0, 0, 255), 4)  # 用红色标记黑色棋子
#         else:  # 白色棋子
#             white_chess_coords.append((i[0], i[1]))
#             cv2.circle(img, (i[0], i[1]), i[2], (255, 0, 0), 4)  # 用蓝色标记白色棋子

#     print("Black Chess Coordinates:", black_chess_coords)
#     print("White Chess Coordinates:", white_chess_coords)
#     return black_chess_coords, white_chess_coords


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
    
    gray = img_preprocess(img)  # 预处理转换为灰度图像

    # 使用Canny边缘检测
    edges = cv2.Canny(gray, 50, 100, apertureSize=3)
    # cv2.namedWindow('edges', cv2.WINDOW_NORMAL)
    # cv2.imshow('edges', edges)

    # 查找轮廓
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 找到最大的轮廓
    if contours:
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
    print("棋盘网格的中心点:", center_points)
    return center_points


def draw_chess_borad(img, corners, center_points):
    """ 绘制棋盘格调试信息 """

    draw_img = img.copy()

    # 绘制棋盘顶点和连线    
    for i in range(len(corners)):
        cv2.line(draw_img, corners[i], corners[(i + 1) % len(corners)], (0, 255, 0), 10)
    for point in corners:
        cv2.circle(draw_img, point, 10, (255, 0, 0), -1)
        cv2.putText(draw_img, str(corners.index(point) + 1), point, cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 100, 0), 6)
    

    # 绘制棋盘中心点和号码
    for point in center_points:
        cv2.circle(draw_img, point, 10, (0, 255, 0), -1)
        cv2.putText(draw_img, str(center_points.index(point) + 1), point, cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 255, 0), 6)

    return draw_img


def chess_borad_detect(img, debug=False):
    """ 棋盘格识别总函数 """
    corners = detect_borad_corners(img)
    if corners is not None:
        H_matrix, H_inv = homo_trans(corners)
        center_points = get_center_points(H_inv)

        if debug:  # 调试模式
            draw_img = draw_chess_borad(img, corners, center_points)
            cv2.namedWindow('img_borad', cv2.WINDOW_NORMAL)
            cv2.imshow('img_borad', draw_img)

        return center_points
    else:
        print("No chessboard detected.")


if __name__ == '__main__':

    print("开始测试")
    img_load = 'img\chessboard_y1.jpg'
    # img_load = 'img\chessboard_f2.jpg'
    img_raw = cv2.imread(img_load)

    cv2.namedWindow('img_raw', cv2.WINDOW_NORMAL)
    cv2.imshow('img_raw', img_raw)
    
    # chess_detect(img0)
    chess_borad_detect(img_raw, True)

    # cv2.namedWindow('Detected Circles and Chessboard Corners', cv2.WINDOW_NORMAL)
    # cv2.imshow('Detected Circles and Chessboard Corners', img0)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
