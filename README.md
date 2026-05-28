# Forza Horizon FSD Dashboard (地平线特斯拉 FSD 驾驶仪表盘)

🚗 **将特斯拉 FSD (Full Self-Driving) 的视觉感知系统搬进《极限竞速：地平线6》！**

This project is a simulated dashboard based on pure computer vision and deep learning. By capturing the gameplay footage and UDP telemetry data from *Forza Horizon*, combined with OpenCV and YOLO vision models, it recreates a 3D driving visualization interface in the browser, featuring spatial depth perception, lane curvature detection, and a blind-spot radar system that mimics the Tesla FSD experience.

---

## 💡 创作动机 (Motivation)

**中文：** 灵感源于我一直无法在 *SimHub* 或其他现成仪表盘软件中找到完美的特斯拉 FSD 复刻风格。我想要的不仅仅是一个速度表，而是一个具有空间纵深感、BEV 路径视觉感知以及盲区雷达的全息驾驶系统。于是，我决定从零开始，打造属于自己的 FSD 仪表盘。

**English:** The inspiration came from my inability to find a perfect Tesla FSD-style dashboard in *SimHub* or other existing software. I wanted more than just a speedometer; I wanted a holographic driving system with spatial depth perception, BEV path visualization, and blind-spot radar. So, I decided to build my own from scratch.

---

## 🛠️ 核心功能 (Features)

* **UDP 物理融合**: 实时获取游戏车速、RPM、挡位、踏板状态及方向盘转角。
* **BEV (鸟瞰图) 感知**: 通过逆透视变换（IPM）提取真实的物理车道曲率和本车偏移量。
* **YOLO 智能目标追踪**: 实时识别前车。独创“轮胎接地线纵深算法”，消除视觉拉伸，让路人车辆模型在远近距离下保持完美比例。
* **全息雷达**: 将游戏内的盲区雷达实时转换为前端跟随车头旋转的 3D 脉冲声呐波纹。

---

## ⚙️ 游戏遥测设置 (Telemetry Setup) - 必看！

为了让仪表盘接收数据，请在游戏中进行以下设置：

1. 打开《极限竞速：地平线 6》游戏设置。
2. 进入 **设置 -> HUD 和游戏界面 (HUD and Gameplay)**。
3. 找到 **“数据输出 (Data Out)”**：
   - **数据输出**: 开 (On)
   - **IP 地址**: `127.0.0.1`
   - **端口 (Port)**: `5300` (必须与 `server.py` 中的 `udp_sock.bind` 端口一致)

---

## 🚀 如何运行 (How to Run)

1. **安装依赖**: `pip install opencv-python dxcam ultralytics openvino`
2. **准备模型**: 在根目录运行 `yolo export model=yolov8s.pt format=openvino` (自动生成 NPU 加速模型)。
3. **启动后端**: 在终端运行 `python server.py`。
4. **访问界面**: 在浏览器输入 `http://localhost:8000`。

---

## ⚠️ 免责与版权声明 (Disclaimer & Copyright)

**中文：**
1. **仅供学习与娱乐**: 本项目仅作为计算机视觉与深度学习的编程学习项目，**不代表任何真实的辅助驾驶技术**。
2. **版权声明**: 本项目前端使用的车辆模型及 UI 设计灵感来源于 特斯拉 (Tesla, Inc.)。本项目为非商业用途的个人开源项目，与特斯拉公司无官方关联。
3. **侵权即删**: 若您是相关资源的版权方并认为本项目侵犯了权益，请提交 Issue，我将第一时间删除相关素材。

**English:**
1. **Educational Purposes Only**: This project is strictly for programming learning purposes (Computer Vision & Deep Learning). **It DOES NOT represent real-world ADAS technologies.**
2. **Copyright**: The vehicle models and UI design are inspired by Tesla, Inc. This is a non-commercial, personal open-source project, not affiliated with Tesla, Inc.
3. **Takedown Policy**: If you are the copyright owner and believe this project infringes upon your rights, please submit an Issue, and I will remove the related files immediately.

---

## 🤖 关于 AI 辅助开发 (AI Collaboration)

本项目在 AI 辅助编程的加持下完成。通过与 Gemini 的深度协同，我将计算机视觉算法与前端 Web 渲染结合，实现了从零到一的 FSD 架构复刻。

This project was developed through collaborative AI programming. By leveraging Gemini's guidance, I integrated computer vision algorithms with front-end web rendering, achieving an FSD-like architecture from the ground up.
