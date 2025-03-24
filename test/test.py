import cv2
import numpy as np

# 1. 读取图像
image = cv2.imread('img/chessboard_y1.jpg')

# 2. 转换颜色空间
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

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
        
        # 计算轮廓的中心点
        M = cv2.moments(contour)

        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            
            # 获取棋子的颜色（在轮廓的中心点位置）
            color = image[cY, cX]
            
            print(f"棋子位置: ({cX}, {cY}), 颜色: {color}")

            # 可视化
            cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)
            cv2.circle(image, (cX, cY), 7, (0, 255, 0), -1)
        
# 显示结果
cv2.namedWindow('Detected Go Pieces', cv2.WINDOW_NORMAL)
cv2.imshow('Detected Go Pieces', image)
cv2.waitKey(0)
cv2.destroyAllWindows()