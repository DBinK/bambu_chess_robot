from pupil_apriltags import Detector
import numpy as np
import cv2


# 初始化一个Detector实例，用于检测和解码Apriltag标记
at_detector = Detector(
    families="tag16h5",  # 指定使用的Apriltag家族，这里选择的是'tag16h5'
    nthreads=1,  # 设置用于加速计算的线程数，此处设置为1
    quad_decimate=1.0,  # 设置图像简化比例，用于加快处理速度，1.0表示不简化
    quad_sigma=0.0,  # 指定在检测标记前对图像进行高斯模糊的程度，0.0表示不进行模糊处理
    refine_edges=1,  # 设置是否对检测到的标记边缘进行精细化处理，以提高定位精度
    decode_sharpening=0.25,  # 设置解码过程中的图像锐化程度，以提高解码成功率
    debug=0,  # 设置调试模式级别，0表示不启用调试模式
)

def get_tag_size(corners):
    # 获取角点坐标的 NumPy 数组
    x_coords = corners[:, 0]
    y_coords = corners[:, 1]
    
    # 计算宽度和高度
    width = np.max(x_coords) - np.min(x_coords)
    height = np.max(y_coords) - np.min(y_coords)

    print(f"Tag size: width={width}, height={height}.")

    return width, height

def filter_by_size(detections, min_size=(30, 30), max_size=(100, 100)):
    valid_tags = []
    for detection in detections:
        tag_id = detection.tag_id  # 假设 tag_id 是一个属性
        corners = detection.corners  # 假设 corners 是一个 NumPy 数组

        # 计算标签大小
        width, height = get_tag_size(corners)

        # 根据大小过滤标签
        if (min_size[0] <= width <= max_size[0]) and (min_size[1] <= height <= max_size[1]):
            valid_tags.append(detection)
        else:
            print(f"Tag {tag_id} is filtered out due to size: width={width}, height={height}.")
    
    return valid_tags

def pre_process(img):
    # 预处理
    img_gary = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 将图像转换为灰度图像
    # img = cv2.GaussianBlur(img, (7, 7), 0)  # 应用高斯滤波以平滑图像
    _, img_bin = cv2.threshold(img_gary, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # 二值化

    return img_bin

def detect_tags(img):
    # 检测标记
    detections = at_detector.detect(img)
    # 过滤
    detections = filter_by_size(detections)

    # for detection in detections:
    #     print(f"Tag {detection.tag_id}, corners={detection.corners}")

    return detections

def persp_trans(img, detections):
    # 取出顶点坐标
    rect = np.zeros((4, 2), dtype="float32")

    for detection in detections:
        if detection.tag_id == 1:
            rect[0] = detection.center.tolist()
        elif detection.tag_id == 6:
            rect[1] = detection.center.tolist()
        elif detection.tag_id == 16:
            rect[2] = detection.center.tolist()
        elif detection.tag_id == 11:
            rect[3] = detection.center.tolist()
            
    height, width = img.shape[:2]  # 目标棋盘坐标系的高度和宽度
    # height, width = 2520, 2520  # 目标棋盘坐标系的高度和宽度

    # 定义变换后的棋盘坐标系高宽
    dst = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype="float32")

    # 计算透视变换矩阵
    M = cv2.getPerspectiveTransform(rect, dst)
    inv_M = np.linalg.inv(M)

    # 返回 变换矩阵 和 逆变换矩阵
    return M, inv_M

def draw_warped_image(img, M, inv_M):    # 用于检查变换效果
    """
    @param img: 输入图像
    @param M: 透视变换矩阵
    @param inv_M: 逆透视变换矩阵
    @return: 透视变换后的图像
    """
    height, width = img.shape[:2]  # 获取图像的高度和宽度
    # height, width = 2520, 2520  # 获取图像的高度和宽度

    # 应用透视变换到图像上
    warped_image = cv2.warpPerspective(img, M, (width, height))

    # 应用逆透视变换到图像
    inv_warped_image = cv2.warpPerspective(warped_image, inv_M,  (width, height))
    
    return warped_image, inv_warped_image

def Homo_trans(img, detections):

    for detection in detections:
        if detection.tag_id == 1:
            x1, y1 = detection.center.tolist()
        elif detection.tag_id == 6:
            x2, y2 = detection.center.tolist()
        elif detection.tag_id == 16:
            x3, y3 = detection.center.tolist()
        elif detection.tag_id == 11:
            x4, y4= detection.center.tolist()

    # 定义图像中的长方形四个顶点（根据你实际值设定）
    image_points = np.array([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], dtype='float32')

    # 定义目标长方形的四个顶点
    width = 2520  # 设置为你想要的宽度
    height = 2520  # 设置为你想要的高度
    object_points = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype='float32')

    # 计算同伦变换矩阵
    H, _ = cv2.findHomography(image_points, object_points)

    # 应用透视变换
    warped_image = cv2.warpPerspective(img, H, (width, height))

    # 计算反向变换矩阵
    H_inv = np.linalg.inv(H)

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
                2,
            )  # 绿色线条

        # 在中心绘制标签 ID
        center = int(detection.center[0]), int(detection.center[1])
        cv2.putText(
            img_draw,
            f"{detection.tag_id}",
            center,
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 222),
            2,
        )  # 红色文本

    return img_draw


if __name__ == "__main__":
    # 读取图像
    # img = cv2.imread("test/apriltag.jpg")
    # img = cv2.imread("test/tag_2.jpg")
    img = cv2.imread("test/tag_3.jpg")

    img_pre = pre_process(img)

    # 检测标记
    detections = detect_tags(img_pre)

    # 绘制检测结果
    img_draw = draw_tags(img, detections)

    # 透视变换
    # M, inv_M = persp_trans(img, detections)
    # warped_image, inv_warped_image = draw_warped_image(img, M, inv_M)

    # cv2.namedWindow("Warped Image", cv2.WINDOW_NORMAL)
    # cv2.imshow("Warped Image", warped_image)

    # cv2.namedWindow("Inv Warped Image", cv2.WINDOW_NORMAL)
    # cv2.imshow("Inv Warped Image", inv_warped_image)

    # 透视变换2
    img_trans, img_retrans = Homo_trans(img, detections)

    cv2.namedWindow("Warped Image", cv2.WINDOW_NORMAL)
    cv2.imshow("Warped Image", img_trans)

    cv2.namedWindow("Inv Warped Image", cv2.WINDOW_NORMAL)
    cv2.imshow("Inv Warped Image", img_retrans)

    # 显示结果
    cv2.namedWindow("Detected AprilTags", cv2.WINDOW_NORMAL)
    cv2.imshow("Detected AprilTags", img_draw)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
