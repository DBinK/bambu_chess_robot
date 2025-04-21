from pupil_apriltags import Detector
import numpy as np
import cv2


# 初始化一个Detector实例，用于检测和解码Apriltag标记
at_detector = Detector(
    families="tag16h5",  # 指定使用的Apriltag家族，这里选择的是'tag16h5'
    nthreads=4,  # 设置用于加速计算的线程数，此处设置为1
    quad_decimate=1.0,  # 设置图像简化比例，用于加快处理速度，1.0表示不简化
    quad_sigma=0.0,  # 指定在检测标记前对图像进行高斯模糊的程度，0.0表示不进行模糊处理
    refine_edges=1,  # 设置是否对检测到的标记边缘进行精细化处理，以提高定位精度
    decode_sharpening=0.25,  # 设置解码过程中的图像锐化程度，以提高解码成功率
    debug=0,  # 设置调试模式级别，0表示不启用调试模式
)

def pre_process(img):
    # 预处理
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 将图像转换为灰度图像
    img_blur = cv2.GaussianBlur(img_gray, (3, 3), 0)  # 应用高斯滤波以平滑图像
    _, img_bin = cv2.threshold(img_blur, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # 二值化

    return img_bin


def detect_tags(img):
    def get_tag_size(corners):
        # 获取角点坐标的 NumPy 数组
        x_coords = corners[:, 0]
        y_coords = corners[:, 1]
        
        # 计算宽度和高度
        width = np.max(x_coords) - np.min(x_coords)
        height = np.max(y_coords) - np.min(y_coords)

        # print(f"Tag size: width={width}, height={height}.")

        return width, height

    def filter_by_size(detections, min_size=(30, 30), max_size=(200, 200)):
        valid_tags = []
        for detection in detections:
            tag_id = detection.tag_id  
            corners = detection.corners  
            x, y = detection.center.tolist()

            # 计算标签大小
            width, height = get_tag_size(corners)

            # 根据大小过滤标签
            if (min_size[0] <= width <= max_size[0]) and (min_size[1] <= height <= max_size[1]):
                # print(f"Tag {tag_id} , center={(x, y)}")
                valid_tags.append(detection)
            else:
                # print(f"Tag {tag_id} is filtered out due to size: width={width}, height={height}.")
                continue
        
        return valid_tags
    
    detections = at_detector.detect(img)      # 检测标记
    detections = filter_by_size(detections)   # 过滤掉不符合大小的标记

    return detections

def sort_corners(corners):
    """ 根据角度对四个角点进行排序，确保顺序为左上角、右上角、右下角、左下角。  """
    
    center_x = sum(x for x, y in corners) / 4  # 计算质心
    center_y = sum(y for x, y in corners) / 4

    def angle_from_center(point):  # 计算每个角点相对于质心的角度
        return np.arctan2(point[1] - center_y, point[0] - center_x)
    
    corners = sorted(corners, key=angle_from_center)  # 根据角度对角点进行排序

    corners = [corners[0], corners[1], corners[2], corners[3]]  # 重新排列顺序为左上角、右上角、右下角、左下角
    
    return corners

def tags_to_quad_vertices(detections):
    """ 将 Apriltag 标记的角点坐标 转换为 列表形式 """

    # 确保每个需要的 id 都存在
    tag_ids = [detection.tag_id for detection in detections]
    # required_ids = [4, 9, 19, 14]  # 需要的 id
    required_ids = [24, 26, 21, 29]  # 需要的 id

    if len(tag_ids) < 4 or not all(tag_id in tag_ids for tag_id in required_ids):
        # print(f"Apriltag 标记不全, 无法继续进行识别, 识别到: {tag_ids}")
        return None

    # 提取标记的角点坐标
    for detection in detections:

        detection.corners = sort_corners(detection.corners) # 对角点坐标排序

        if detection.tag_id == 24:                 
            x1, y1 = detection.corners[0].tolist()  # 左上
        elif detection.tag_id == 26:               
            x2, y2 = detection.corners[1].tolist()  # 右上
        elif detection.tag_id == 21:            
            x3, y3 = detection.corners[2].tolist()  # 右下
        elif detection.tag_id == 29:            
            x4, y4 = detection.corners[3].tolist()  # 左下

    quad_vertices = [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]

    # print(f"Apriltag 标记坐标: {quad_vertices}")

    return quad_vertices

def homo_trans(quad_vertices, width=int((2560-100)/2), height=int((2100-100)/2)):
# def homo_trans(quad_vertices, width=2560-100, height=2100-100):
    """ 计算 将图像中的特定四边形区域 变换为目标长方形区域 所需的矩阵 H """

    # 定义图像中的长方形四个顶点（根据你实际值设定）
    image_points = np.array(quad_vertices, dtype='float32')

    # 定义目标长方形的四个顶点
    object_points = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype='float32')

    # 计算同伦变换矩阵
    H_matrix , _ = cv2.findHomography(image_points, object_points)

    # 计算反向变换矩阵
    H_inv = np.linalg.inv(H_matrix)

    return H_matrix, H_inv

def transform_image_to_object(point_raw, H_matrix):
    # 输入图像坐标系坐标，输出长方形区域坐标系坐标
    point_homogeneous = np.array([point_raw[0], point_raw[1], 1])  # 转换为齐次坐标
    transformed_point = H_matrix @ point_homogeneous  # 进行变换
    return transformed_point[0] / transformed_point[2], transformed_point[1] / transformed_point[2]

def transform_object_to_image(point_obj, H_inv):
    # 输入长方形区域坐标系坐标，输出图像坐标系坐标
    point_homogeneous = np.array([point_obj[0], point_obj[1], 1])  # 转换为齐次坐标
    transformed_point = H_inv @ point_homogeneous  # 进行反向变换
    return transformed_point[0] / transformed_point[2], transformed_point[1] / transformed_point[2]

def transform_object_to_printer(point_obj):
    # 长方形区域坐标系 转换为 打印机坐标系
    point_printer = [0, 0]
    point_printer[0] = (point_obj[0] / 10) + 16
    point_printer[1] = 224 - (point_obj[1] / 10) + 16  # 翻转y轴

    return point_printer

def draw_homo_trans(img, H_matrix, width=int((2560-100)/2), height=int((2100-100)/2)):
# def draw_homo_trans(img, H_matrix, width=2560-100, height=2100-100):

    # 应用透视变换
    warped_image = cv2.warpPerspective(img, H_matrix , (width, height))

    # 计算反向变换矩阵
    H_inv = np.linalg.inv(H_matrix)

    # 反向变换回原图像空间
    height_original, width_original = img.shape[:2]
    reversed_warped_image = cv2.warpPerspective(warped_image, H_inv, (width_original, height_original))

    return warped_image, reversed_warped_image

def draw_tags(img, detections):

    img_draw = img.copy()

    # 绘制检测结果
    for detection in detections:
        corners = detection.corners

        # 绘制边界框
        for i in range(4):
            cv2.line(
                img_draw,
                tuple(corners[i].astype(int)),
                tuple(corners[(i + 1) % 4].astype(int)),
                (0, 255, 0),
                3,
            )  # 绿色线条

        # 在中心绘制标签 ID
        center = int(detection.center[0]-15), int(detection.center[1]+12)
        cv2.putText(
            img_draw,
            f"{detection.tag_id}",
            center,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 222),
            2,
        )  # 红色文本

    return img_draw

def draw_chess(img_trans, circles):
    img_chess = img_trans.copy()
    for i in range(len(circles[0])):
        x, y, r = circles[0][i]
        cv2.circle(img_chess, (x, y), r, (0, 255, 0), 2)
        cv2.circle(img_chess, (x, y), 2, (0, 0, 255), 3)

    return img_chess

# 鼠标回调函数
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # 检测左键点击事件
        
        #p_raw = [x, y]
        #p_obj = transform_image_to_object(p_raw, H_matrix)
        #p_obj_fix = [(p_obj[0]/10)-20, (p_obj[1]/10)-20]

        print(f'点击坐标: ({x}, {y})')  # 打印点击的坐标
        # print(f'转换坐标: ({p_obj[0]}, {p_obj[1]})')
        # print(f'转换坐标fix: ({p_obj_fix[0]}, {p_obj_fix[1]})')

        # cv2.putText(img_trans, f"{int(p_obj_fix[0])},{int(p_obj_fix[1])}", (int(p_obj[0]+100), int(p_obj[1])), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
        # cv2.circle(img_trans, (int(p_obj[0]), int(p_obj[1])), 50, (0, 0, 255), -1)
        # cv2.imshow('Warped Image', img_raw)  # 重新显示图像


if __name__ == "__main__":
    # 读取图像
    # img = cv2.imread("test/apriltag.jpg")
    # img = cv2.imread("test/tag_2.jpg")
    img = cv2.imread("img/tag_4.png")

    # 预处理
    img_pre = pre_process(img)

    # 检测标记
    detections = detect_tags(img_pre)
    quad_vertices = tags_to_quad_vertices(detections)

    # 绘制tag检测结果
    img_draw = draw_tags(img, detections)

    # 透视变换
    H_matrix, H_inv = homo_trans(quad_vertices)
    img_trans, img_retrans = draw_homo_trans(img, H_matrix)

    # # 棋子检测
    # print("开始检测棋子")
    # circles = detect_chess(img_trans)
    # img_chess = draw_chess(img_trans, circles)

    # cv2.namedWindow('chess Image', cv2.WINDOW_NORMAL)
    # cv2.imshow('chess Image', img_chess)

    # 坐标系转换
    # p_raw = [508, 373]  # 1号点
    # p_raw = [349, 925]  # 3号点
    # p_raw = [1128, 942]  # 4号点

    p_raw = [685, 509]  # 6号点
    
    p_obj = transform_image_to_object(p_raw, H_matrix)
    p_prt = transform_object_to_printer(p_obj)          # 翻转y轴, 转换为打印机坐标系

    print(f"raw: {int(p_raw[0])}, {int(p_raw[1])}")
    print(f"obj: {int(p_obj[0])}, {int(p_obj[1])}")
    print(f"prt: {int(p_prt[0])}, {int(p_prt[1])}")

    # 标记点
    cv2.putText(img_trans, f"{int(p_prt[0])},{int(p_prt[1])}", (int(p_obj[0]+100), int(p_obj[1])), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
    cv2.circle(img_trans, (int(p_obj[0]), int(p_obj[1])), 50, (0, 0, 255), -1)

    cv2.putText(img_retrans, f"{int(p_raw[0])},{int(p_raw[1])}", (int(p_raw[0]+10), int(p_raw[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    cv2.circle(img_retrans, (int(p_raw[0]), int(p_raw[1])), 10, (0, 0, 255), -1)

    cv2.namedWindow("Warped Image", cv2.WINDOW_NORMAL)
    cv2.imshow("Warped Image", img_trans)

    cv2.namedWindow("Inv Warped Image", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('Inv Warped Image', click_event)  # 绑定鼠标回调函数到窗口
    cv2.imshow("Inv Warped Image", img_retrans)

    # 显示结果
    cv2.namedWindow("Detected AprilTags", cv2.WINDOW_NORMAL)
    cv2.imshow("Detected AprilTags", img_draw)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
