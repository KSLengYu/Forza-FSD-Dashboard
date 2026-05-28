import json
import socket
import struct
import threading
import time
import math
import cv2
import dxcam
import numpy as np
import openvino as ov
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ==========================================
# 雷达校准区 (需与你游戏内雷达位置匹配)
# ==========================================
RADAR_LEFT = 500   
RADAR_TOP = 800    
RADAR_SIZE = 200   

latest_telemetry = {
    "speed": 0, "rpm": 0, "gearStr": "P", 
    "abs": False, "tcs": False, "p": True,
    "cars": [], "curve": 0.0, "steer": 0.0,
    "radar": {"active": False, "angle": 0} 
}

class TeslaServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            try:
                with open('index.html', 'rb') as f:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_error(404, "index.html missing")
        elif self.path in ['/car.svg', '/car_back.svg', '/car_side.svg', '/p.svg', '/abs.svg', '/tcs.svg']:
            filename = self.path[1:]
            try:
                with open(filename, 'rb') as f:
                    self.send_response(200)
                    self.send_header('Content-type', 'image/svg+xml')
                    self.end_headers()
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_error(404, f"{filename} not found")
        elif self.path == '/stream':
            self.send_response(200)
            self.send_header('Content-type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            while True:
                try:
                    self.wfile.write(f"data: {json.dumps(latest_telemetry)}\n\n".encode('utf-8'))
                    self.wfile.flush()
                    time.sleep(0.033)
                except (ConnectionResetError, BrokenPipeError):
                    break 
        else:
            self.send_error(404)

    def log_message(self, format, *args): pass

def fh_udp_listener():
    global latest_telemetry
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('0.0.0.0', 5300))
    while True:
        try:
            data, addr = udp_sock.recvfrom(1024)
            if len(data) >= 324:
                current_rpm = struct.unpack('<f', data[16:20])[0]
                vx, vy, vz = struct.unpack('<fff', data[32:44])
                speed_kmh = max(0, round(math.sqrt(vx**2 + vy**2 + vz**2) * 3.6))
                
                accel = struct.unpack('<B', data[315:316])[0]
                brake = struct.unpack('<B', data[316:317])[0]
                handbrake = struct.unpack('<B', data[318:319])[0]
                raw_gear = struct.unpack('<B', data[319:320])[0]
                
                raw_steer = struct.unpack('<b', data[320:321])[0]
                steer_normalized = raw_steer / 127.0 
                
                slip_fl, slip_fr, slip_rl, slip_rr = struct.unpack('<ffff', data[84:100])
                
                is_abs_active = bool(speed_kmh > 2 and brake > 25 and max(abs(slip_fl), abs(slip_fr), abs(slip_rl), abs(slip_rr)) > 1.2)
                is_tcs_active = bool(speed_kmh > 2 and accel > 50 and max(abs(slip_rl), abs(slip_rr)) > 1.2)
                is_p_active = bool(handbrake > 25)
                
                if is_p_active and speed_kmh < 2: tesla_gear = "P"
                elif raw_gear == 0: tesla_gear = "R"
                elif raw_gear == 1: tesla_gear = "D" if (speed_kmh > 1 or accel > 0) else "N"
                else: tesla_gear = "D"
                    
                latest_telemetry["speed"] = speed_kmh
                latest_telemetry["rpm"] = int(current_rpm)
                latest_telemetry["gearStr"] = tesla_gear
                latest_telemetry["abs"] = is_abs_active
                latest_telemetry["tcs"] = is_tcs_active
                latest_telemetry["p"] = is_p_active
                latest_telemetry["steer"] = float(steer_normalized)
        except Exception:
            pass

def http_server_runner():
    server = ThreadingHTTPServer(('0.0.0.0', 8000), TeslaServerHandler)
    server.serve_forever()

if __name__ == '__main__':
    print("====== FSD (性能纯净版) 启动 ======")
    
    threading.Thread(target=fh_udp_listener, daemon=True).start()
    threading.Thread(target=http_server_runner, daemon=True).start()
    
    core = ov.Core()
    model_dir = "yolov8s_openvino_model"
    xml_file = next((os.path.join(model_dir, f) for f in os.listdir(model_dir) if f.endswith(".xml")), None)
    
    model = core.read_model(xml_file)
    compiled_model = core.compile_model(model, "NPU")
    input_layer = compiled_model.input(0)
    output_layer = compiled_model.output(0)

    camera = dxcam.create(output_color="BGR")
    camera.start(target_fps=60)

    cv2.namedWindow("FSD Vision", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("FSD Vision", 640, 360)
    CLASS_NAMES = {2: "Car", 5: "Bus", 7: "Truck"}

    while True:
        frame = camera.get_latest_frame()
        if frame is None: continue

        h_orig, w_orig = frame.shape[:2]

        # 1. 提取小地图导航曲率 (去除一切路面杂波干扰)
        try:
            roi_h, roi_w = int(h_orig * 0.35), int(w_orig * 0.25)
            minimap = frame[h_orig-roi_h:h_orig, 0:roi_w]
            hsv = cv2.cvtColor(minimap, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, np.array([80, 100, 150]), np.array([130, 255, 255]))
            top_half_mask = mask[0:int(roi_h/2), :]
            M = cv2.moments(top_half_mask)
            if M['m00'] > 50:
                cx = int(M['m10']/M['m00'])
                latest_telemetry["curve"] = float((cx - (roi_w / 2)) / (roi_w / 2))
            else:
                latest_telemetry["curve"] = 0.0
        except Exception:
            pass

        # 2. 盲区雷达方位锁定
        try:
            radar_roi = frame[RADAR_TOP:RADAR_TOP+RADAR_SIZE, RADAR_LEFT:RADAR_LEFT+RADAR_SIZE]
            hsv_radar = cv2.cvtColor(radar_roi, cv2.COLOR_BGR2HSV)
            red_mask = cv2.inRange(hsv_radar, np.array([0, 150, 100]), np.array([10, 255, 255])) + cv2.inRange(hsv_radar, np.array([170, 150, 100]), np.array([180, 255, 255]))
            M = cv2.moments(red_mask)
            if M["m00"] > 150: 
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                angle = math.degrees(math.atan2(cX - (RADAR_SIZE/2), (RADAR_SIZE/2) - cY))
                latest_telemetry["radar"] = {"active": True, "angle": angle}
            else:
                latest_telemetry["radar"] = {"active": False, "angle": 0}
        except Exception:
            pass

        # 3. AI 车辆识别
        img = cv2.resize(frame, (640, 640))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        img = np.expand_dims(img.transpose(2, 0, 1), axis=0)

        results = compiled_model([img])[output_layer]
        predictions = np.squeeze(results).T 
        
        boxes, confidences, class_ids = [], [], []
        for row in predictions:
            classes_scores = row[4:]
            max_score = np.max(classes_scores)
            if max_score > 0.25:
                class_id = int(np.argmax(classes_scores))
                if class_id in [2, 5, 7]:
                    cx, cy, w, h = row[0:4]
                    x1 = int((cx - w / 2) * (w_orig / 640))
                    y1 = int((cy - h / 2) * (h_orig / 640))
                    
                    bottom_edge = y1 + int(h * h_orig / 640)
                    center_x = x1 + int(w * w_orig / 640) / 2
                    if bottom_edge > h_orig * 0.85 and (w_orig * 0.3 < center_x < w_orig * 0.7): continue 
                        
                    boxes.append([x1, y1, int(w * w_orig / 640), int(h * h_orig / 640)])
                    confidences.append(float(max_score))
                    class_ids.append(class_id)
                    
        indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.4, 0.4)
        
        detected_cars = []
        horizon_y = h_orig * 0.45 
        
        if len(indices) > 0:
            for i in np.array(indices).flatten():
                x, y, w, h = boxes[i]
                aspect_ratio = w / h
                orientation = "side" if aspect_ratio > 1.6 else "back"
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
                
                bottom_edge = y + h
                raw_dist = (bottom_edge - horizon_y) / (h_orig - horizon_y)
                raw_dist = max(0.01, min(1.0, raw_dist))
                dist_ratio = math.pow(raw_dist, 0.7) 
                
                center_x = x + w / 2
                screen_offset = (center_x - w_orig / 2) / (w_orig / 2) 
                
                detected_cars.append({
                    "type": CLASS_NAMES[class_ids[i]],
                    "distance": float(dist_ratio),
                    "offset": float(screen_offset),
                    "orientation": orientation
                })

        latest_telemetry["cars"] = detected_cars

        cv2.imshow("FSD Vision", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    camera.stop()
    cv2.destroyAllWindows()