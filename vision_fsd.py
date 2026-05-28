import mss
import numpy as np
import cv2
from ultralytics import YOLO

# 1. 初始化 YOLOv8 模型
# yolov8n.pt 是最轻量级版本，占用显存极小，速度飞快
# 第一次运行会自动从网络下载模型文件（大概 6MB）
print("正在加载 YOLO 模型...")
model = YOLO('yolov8n.pt') 

# 2. 初始化屏幕抓取器
sct = mss.mss()

# 获取你的主屏幕分辨率信息
monitor = sct.monitors[1]
print(f"检测到主屏幕分辨率: {monitor['width']}x{monitor['height']}")

# 创建一个窗口用来显示结果
cv2.namedWindow("FSD Vision (Press Q to quit)", cv2.WINDOW_NORMAL)
# 你可以调整窗口大小，免得全屏显示挡住游戏
cv2.resizeWindow("FSD Vision (Press Q to quit)", 800, 450)

print("引擎启动！切换到游戏画面...")

while True:
    # 3. 极速全屏抓取
    img_mss = sct.grab(monitor)
    
    # 将 mss 格式转换为 OpenCV 能处理的 Numpy 矩阵
    # 并且把 BGRA 颜色格式转换为 BGR格式
    frame = np.array(img_mss)
    # 将 BGRA 转为 BGR（修复：使用正确的 OpenCV 常量）
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    # 4. 让 YOLO 识别画面
    # verbose=False 可以关闭控制台里烦人的刷屏日志
    # classes=[2, 5, 7] 告诉 YOLO：我只要汽车(2), 巴士(5), 卡车(7)，忽略人和猫狗
    results = model(frame, verbose=False, classes=[2, 5, 7])
    
    # 5. 在画面上画出识别结果
    # YOLO 已经帮我们做好了画框的工具，直接调用
    annotated_frame = results[0].plot()

    # 6. 显示画面
    cv2.imshow("FSD Vision (Press Q to quit)", annotated_frame)

    # 7. 按下键盘上的 'q' 键退出程序
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 清理资源
cv2.destroyAllWindows()