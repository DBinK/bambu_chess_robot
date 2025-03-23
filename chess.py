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
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)        # 转换为灰度图像
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
            cv2.circle(img, (i[0], i[1]), i[2], (0, 0, 255), 2)  # 用红色标记黑色棋子
        else:  # 白色棋子
            white_chess_coords.append((i[0], i[1]))
            cv2.circle(img, (i[0], i[1]), i[2], (255, 0, 0), 2)  # 用蓝色标记白色棋子

    print("Black Chess Coordinates:", black_chess_coords)
    print("White Chess Coordinates:", white_chess_coords)
    return black_chess_coords, white_chess_coords

def chess_borad_detect(img):
    """
    棋盘格识别
    img: 输入图像
    return: 棋盘格中心点坐标列表
    """
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
            corners = [tuple(point[0]) for point in approx]
            
            print("Chessboard Corners:", corners)
            
            # 在原图像上绘制角点
            for i in range(len(corners)):
                cv2.circle(img, corners[i], 5, (0, 255, 0), -1)
                cv2.line(img, corners[i], corners[(i+1) % 4], (0, 255, 0), 2)
            
            # 定义目标正方形的四个角点
            target_corners = np.float32([[0, 0], [300, 0], [300, 300], [0, 300]])

            # src_corners = np.float32(corners)

            # 确定四个角点坐标顺序)
            src_corners = np.float32([corners[0], corners[3], corners[2], corners[1]])
            
            # 计算透视变换矩阵
            M = cv2.getPerspectiveTransform(src_corners, target_corners)
            
            # 应用透视变换
            warped_img = cv2.warpPerspective(img, M, (300, 300))

            
            # 计算正方形区域内每个小格子的边界和中心点
            width = 100
            height = 100
            grid_boundaries = []
            center_points_warped = []
            for i in range(3):
                for j in range(3):
                    x_start = j * width
                    y_start = i * height
                    x_end = (j + 1) * width
                    y_end = (i + 1) * height
                    grid_boundaries.append(((x_start, y_start), (x_end, y_end)))
                    
                    x_center = int(j * width + width / 2)
                    y_center = int(i * height + height / 2)
                    center_points_warped.append((x_center, y_center))
                    cv2.circle(warped_img, (x_center, y_center), 3, (255, 255, 0), -1)  # 绘制中心点

            cv2.namedWindow('warped_img', cv2.WINDOW_NORMAL)
            cv2.imshow('warped_img', warped_img)
            
            # 将中心点逆变换回原始图像坐标系
            center_points = []
            index = 1  # 序号从1开始
            for point in center_points_warped:
                x, y = point
                src_point = np.array([[x, y]], dtype=np.float32)
                dst_point = cv2.perspectiveTransform(src_point.reshape(-1, 1, 2), np.linalg.inv(M))[0][0]
                center_points.append((int(dst_point[0]), int(dst_point[1])))
                cv2.circle(img, (int(dst_point[0]), int(dst_point[1])), 3, (255, 255, 0), -1)  # 绘制中心点
                cv2.putText(img, str(index), (int(dst_point[0]) - 10, int(dst_point[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (200, 100, 0), 4)  # 标注序号
                index += 1
            
            print("Center Points of Chessboard Grids:", center_points)
            return center_points
        

if __name__ == '__main__':
    print("开始测试")
    img_load = 'img\chessboard_y1.jpg'
    img0 = cv2.imread(img_load)
    img_ori = cv2.resize(img0, None, fx=1/8, fy=1/8)

    cv2.namedWindow('chessboard_y1', cv2.WINDOW_NORMAL)
    cv2.imshow('chessboard_y1', img0)
    
    #chess_detect(img0)
    chess_borad_detect(img0)

    cv2.namedWindow('Detected Circles and Chessboard Corners', cv2.WINDOW_NORMAL)
    cv2.imshow('Detected Circles and Chessboard Corners', img0)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
