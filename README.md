English
# Forza Horizon FSD Dashboard

🚗 **Bringing Tesla's FSD (Full Self-Driving) Vision Perception System into Forza Horizon6!**

This project is a simulated dashboard based on pure computer vision and deep learning. By capturing the gameplay footage and UDP telemetry data from *Forza Horizon*, combined with OpenCV and YOLO vision models, it recreates a 3D driving visualization interface in the browser. It features spatial depth perception, lane curvature detection, and a blind-spot radar system, mimicking the real Tesla FSD experience.

## ✨ Features
* **UDP & Physics Fusion**: Real-time extraction of speed, RPM, gear, pedal status, and steering wheel angle to eliminate high-frequency visual jitter.
* **BEV (Bird's Eye View) Perception**: Maps the 2D gameplay footage to a top-down view via Inverse Perspective Mapping (IPM) to extract accurate physical lane curvature and ego-vehicle offset.
* **Anti-Distortion YOLO Tracking**: Utilizes NPU/GPU for real-time leading vehicle detection. An original "tire-grounding depth algorithm" ensures that rendering background vehicles in the front-end scales proportionally, entirely eliminating visual stretching/distortion.
* **Holographic Sonar Radar**: Uses OpenCV to capture the in-game blind-spot radar, transforming it into a front-end 3D pulsating sonar wave synced with the vehicle's heading.

## 🛠️ Tech Stack
* **Back-end**: Python, OpenCV, OpenVINO (YOLOv8 NPU Inference), socket, DXcam
* **Front-end**: HTML5 Canvas, Vanilla JavaScript, SSE (Server-Sent Events)

## 🚀 How to Run
1. Install dependencies: `pip install opencv-python dxcam ultralytics openvino`
2. Prepare the model: Run `yolo export model=yolov8s.pt format=openvino` in the root directory to generate the NPU-accelerated model.
3. Start the backend: Run `python server.py` in your terminal.
4. Open the dashboard: Visit `http://localhost:8000` in your browser (Supports local network access via iPad).

## 🆘 Help Wanted!
Currently, the project struggles with traditional OpenCV lane detection on unpaved roads (dirt, gravel). 
I have successfully tested `yolov8n-seg.pt` (pixel-level segmentation), but I currently lack an efficient Python matrix processing logic to extract the AI's "Drivable Area Mask" and convert it into front-end Bezier curve coordinates. PRs and optimization ideas from the community are highly welcome!

---

## ⚠️ Disclaimer & Copyright
1. **Educational & Entertainment Purposes Only**: This project is strictly a programming learning exercise for Computer Vision (CV), Deep Learning, and Front-end rendering. **It DOES NOT represent real-world autonomous driving or ADAS technologies.** Please do not apply this to any real driving scenarios.
2. **Copyright (Take Down on Request)**: The vehicle texture model (Tesla Car Model) and certain UI elements used in the front-end display are inspired by Tesla, Inc. **This is a non-commercial, personal open-source toy and is not officially affiliated with Tesla.**
3. **Takedown Policy**: If you are the copyright owner of any models/assets and believe this project infringes upon your rights, please submit an Issue or contact me. I will remove the related files and code immediately upon notification.



Chinese
# Forza Horizon FSD Dashboard (地平线纯视觉自动驾驶仪表盘)

🚗 **将特斯拉 FSD (Full Self-Driving) 的视觉感知系统搬进《极限竞速：地平线6》！**

本项目是一个基于纯视觉识别和深度学习的模拟仪表盘。通过抓取《地平线 6》的游戏画面和 UDP 遥测数据，结合 OpenCV 与 YOLO 视觉模型，在浏览器前端实时复刻了拥有空间纵深感、车道曲率感知以及盲区雷达的 3D 驾驶可视化界面。

## ✨ 核心功能 (Features)
* **UDP 物理融合**：实时获取车速、RPM、挡位、踏板状态及方向盘物理转角，消除纯视觉高频抖动。
* **BEV 上帝视角感知**：通过逆透视变换（IPM）将 2D 游戏画面映射为鸟瞰图，提取真实的物理车道曲率和本车偏移量。
* **YOLO 目标防拉伸追踪**：利用 NPU/GPU 实时识别前车。独创“轮胎接地线纵深算法”，在前端渲染时保证路人车辆模型等比例缩放，彻底消除视觉拉伸变形。
* **全息雷达声呐**：利用 OpenCV 捕捉游戏内的盲区雷达，转换为前端跟随车头旋转的 3D 脉冲声呐波纹。

## 🛠️ 技术栈 (Tech Stack)
* **后端**: Python, OpenCV, OpenVINO (YOLOv8 NPU 推理), socket, DXcam
* **前端**: HTML5 Canvas, Vanilla JavaScript, SSE (Server-Sent Events)

## 🚀 如何运行 (How to Run)
1. 安装依赖：`pip install opencv-python dxcam ultralytics openvino`
2. 下载模型：在项目根目录运行 `yolo export model=yolov8s.pt format=openvino` 生成 NPU 加速模型。
3. 启动后端：在终端运行 `python server.py`。
4. 打开仪表盘：在浏览器访问 `http://localhost:8000`（支持 iPad 局域网访问）。

## 🆘 寻求社区大佬帮助 (Help Wanted!)
目前项目在非铺装路面（泥地、沙石路）的传统 OpenCV 寻线经常失效。
我尝试过跑通 `yolov8n-seg.pt` (像素级分割模型)，但目前缺乏一套高效的 Python 矩阵处理逻辑，将 AI 输出的“可行驶区域掩码 (Drivable Area Mask)”提取出来并转换为前端的贝塞尔曲线坐标。欢迎各位大佬提交 PR 或提出优化思路！

---

## ⚠️ 免责与版权声明 (Disclaimer & Copyright)
1. **仅供学习与娱乐**：本项目仅作为计算机视觉（CV）、深度学习与前端渲染技术的编程学习项目，**绝对不代表真实世界中的自动驾驶、辅助驾驶技术**。请勿将其用于任何真实的驾驶场景。
2. **版权声明 (Take Down on Request)**：本项目前端展示中使用的车辆贴图模型（Tesla Car Model）及部分 UI 元素的设计灵感来源于 特斯拉（Tesla, Inc.）。**本项目为非商业用途的个人开源玩具，与特斯拉公司无任何官方关联**。
3. **侵权即删**：如果您是相关模型的版权方，并认为本项目的使用侵犯了您的合法权益，请在此仓库提交 Issue 或联系我，我会在收到通知后第一时间删除相关模型文件和代码素材。
