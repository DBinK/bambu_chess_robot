from pupil_apriltags import Detector
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


def detect(img):
    # 预处理
    img_gary = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 将图像转换为灰度图像
    # img = cv2.GaussianBlur(img, (7, 7), 0)  # 应用高斯滤波以平滑图像
    img_bin = cv2.threshold(img_gary, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]  # 二值化

    # 检测标记
    detections = at_detector.detect(img_bin)

    for detection in detections:
        print(detection.tag_id)

    return detections


def draw(img, detections):

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
            f"ID: {detection.tag_id}",
            center,
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 222),
            2,
        )  # 红色文本

    return img_draw


if __name__ == "__main__":
    # 读取图像
    img = cv2.imread("test/apriltag.jpg")

    # 检测标记
    detections = detect(img)

    # 绘制检测结果
    img_draw = draw(img, detections)

    # 显示结果
    cv2.imshow("Detected AprilTags", img_draw)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
