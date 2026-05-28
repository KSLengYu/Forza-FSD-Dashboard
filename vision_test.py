import cv2
import dxcam
import numpy as np
import openvino as ov
import os

print("正在初始化 Intel OpenVINO 核心引擎...")
core = ov.Core()

model_dir = "yolov8s_openvino_model"
xml_file = None
for f in os.listdir(model_dir):
    if f.endswith(".xml"):
        xml_file = os.path.join(model_dir, f)
        break

if not xml_file:
    print("找不到 XML 模型文件！")
    exit()

print(f"找到模型: {xml_file}")
model = core.read_model(xml_file)
compiled_model = core.compile_model(model, "NPU")
input_layer = compiled_model.input(0)
output_layer = compiled_model.output(0)

camera = dxcam.create(output_color="BGR")
camera.start(target_fps=60)

cv2.namedWindow("Intel NPU Direct Vision", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Intel NPU Direct Vision", 800, 450)

print("✅ 引擎启动！全彩车辆识别已激活！")

# --- 新增：定义车辆类型字典和专属颜色 ---
# COCO数据集标准: 2=汽车(Car), 5=大巴(Bus), 7=卡车(Truck)
CLASS_NAMES = {2: "Car", 5: "Bus", 7: "Truck"}
# BGR 格式的颜色: 汽车为青色，大巴为橙色，卡车为紫色
CLASS_COLORS = {2: (255, 255, 0), 5: (0, 165, 255), 7: (255, 0, 255)}

while True:
    frame = camera.get_latest_frame()
    if frame is None:
        continue

    h_orig, w_orig = frame.shape[:2]

    img = cv2.resize(frame, (640, 640))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0
    img = img.transpose(2, 0, 1)
    img = np.expand_dims(img, axis=0)

    results = compiled_model([img])[output_layer]
    predictions = np.squeeze(results).T 
    
    boxes = []
    confidences = []
    class_ids = [] # 新增：用来记录每个框属于什么车
    
    for row in predictions:
        classes_scores = row[4:]
        max_score = np.max(classes_scores)
        if max_score > 0.4:
            class_id = int(np.argmax(classes_scores))
            if class_id in [2, 5, 7]:
                cx, cy, w, h = row[0:4]
                x1 = int((cx - w / 2) * (w_orig / 640))
                y1 = int((cy - h / 2) * (h_orig / 640))
                width = int(w * (w_orig / 640))
                height = int(h * (h_orig / 640))
                
                boxes.append([x1, y1, width, height])
                confidences.append(float(max_score))
                class_ids.append(class_id) # 把识别到的车型ID存下来
                
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.4, 0.4)
    
    if len(indices) > 0:
        for i in np.array(indices).flatten():
            x, y, w, h = boxes[i]
            c_id = class_ids[i] # 获取这辆车的 ID
            
            # 提取名字和颜色
            label_name = CLASS_NAMES[c_id]
            box_color = CLASS_COLORS[c_id]
            
            # 画框和文字，颜色会根据车型自动变化
            cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
            cv2.putText(frame, f"{label_name} {int(confidences[i]*100)}%", (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)

    cv2.imshow("Intel NPU Direct Vision", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.stop()
cv2.destroyAllWindows()