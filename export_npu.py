from ultralytics import YOLO

print("正在下载并加载 YOLOv8 Small 模型...")
# s版本兼顾了速度和准确率，最适合 NPU
model = YOLO('yolov8s.pt') 

print("正在将其编译为 Intel OpenVINO 专属格式，请耐心等待...")
# 这一步会生成一个 yolov8s_openvino_model 文件夹
model.export(format='openvino')
print("转换完成！")