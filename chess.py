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
def chess_detect(img):
    """ 棋子识别 
    img: 输入图像
    return: 黑色棋子坐标列表，白色棋子坐标列表
    """
    img_gray = img_preprocess(img)        # 转换为灰度图像
    circles = cv2.HoughCircles(img_gray, cv2.HOUGH_GRADIENT, dp=1, minDist=25, param1=50, param2=55)
    if circles is not None:
        circles = np.uint16(np.around(circles))  # 对圆的圆心坐标和半径四舍五入取整
    
    black_chess_coords = []
    white_chess_coords = []

    for i in circles[0, :]:
        # 提取圆形区域
        mask = np.zeros_like(img_gray)
        cv2.circle(mask, (i[0], i[1]), i[2], (255, 255, 255), -1)
        
        # 计算圆形区域的平均灰度值
        mean_val = cv2.mean(img_gray, mask=mask)[0]
        
        if mean_val < 128:  # 黑色棋子
            black_chess_coords.append((i[0], i[1]))
            cv2.circle(img, (i[0], i[1]), i[2], (0, 0, 255), 4)  # 用红色标记黑色棋子
        else:  # 白色棋子
            white_chess_coords.append((i[0], i[1]))
            cv2.circle(img, (i[0], i[1]), i[2], (255, 0, 0), 4)  # 用蓝色标记白色棋子

    print("Black Chess Coordinates:", black_chess_coords)
    print("White Chess Coordinates:", white_chess_coords)
    return black_chess_coords, white_chess_coords


def detect_borad_corners(img):
    # 转换为灰度图像
    gray = img_preprocess(img)

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
            
            # 计算质心
            center_x = sum(x for x, y in corners) / 4
            center_y = sum(y for x, y in corners) / 4
            
            # 计算每个角点相对于质心的角度
            def angle_from_center(point):
                return np.arctan2(point[1] - center_y, point[0] - center_x)
            
            # 根据角度对角点进行排序
            corners = sorted(corners, key=angle_from_center)
            
            # 重新排列顺序为左上角、右上角、右下角、左下角
            corners = [corners[0], corners[1], corners[2], corners[3]]

            print("棋盘角点:", corners)

            return corners
        

def homo_trans(corners, w=300, h=300):
    """ 计算 将图像中的特定四边形区域 变换为目标长方形区域 所需的矩阵 H """

    # 定义图像中的长方形四个顶点（根据你实际值设定）
    image_points = np.array(corners, dtype='float32')

    # 定义目标长方形的四个顶点
    object_points = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype='float32')

    # 计算同伦变换矩阵
    H_matrix , _ = cv2.findHomography(image_points, object_points)

    # 计算反向变换矩阵
    H_inv = np.linalg.inv(H_matrix)

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

        if debug: 
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
