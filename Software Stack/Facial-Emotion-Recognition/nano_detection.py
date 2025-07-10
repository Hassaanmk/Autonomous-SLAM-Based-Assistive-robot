import cv2
import time
import numpy as np
import onnxruntime as ort
from ultralytics import YOLO
import torch # Required for non_max_suppression
from ultralytics.utils.ops import non_max_suppression  # NMS decoder

# Step 1: Export YOLO model to ONNX
def export_to_onnx(pt_path):
    model = YOLO(pt_path)
    model.export(format="onnx", simplify=True, opset=12)
    print(f"Model exported to ONNX from {pt_path}")

# Step 2: Decode and visualize ONNX output
def run_onnx_inference(onnx_model_path):
    # Load ONNX model
    session = ort.InferenceSession(onnx_model_path, providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not accessible")
        return

    print("Starting person detection... Press 'q' to quit.")
    while True:
        start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break

        orig_h, orig_w = frame.shape[:2]

        # Preprocess
        img = cv2.resize(frame, (640, 640))
        img_input = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_input = img_input.transpose(2, 0, 1)  # HWC to CHW
        img_input = img_input.astype(np.float32) / 255.0
        img_input = np.expand_dims(img_input, axis=0)

        # Inference
        outputs = session.run([output_name], {input_name: img_input})[0]

        # Apply NMS using Ultralytics helper
        pred = non_max_suppression(torch.tensor(outputs), conf_thres=0.25, iou_thres=0.45)[0]

        # Draw boxes (only for 'person')
        for det in pred:
            x1, y1, x2, y2, conf, cls = det
            cls = int(cls.item())
            conf = float(conf.item())

            if cls == 0:  # 0 = person in COCO
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f'Person {conf:.2f}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # FPS
        fps = 1.0 / (time.time() - start_time)
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Display
        cv2.imshow("YOLOv8 ONNX - Person Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# === Main Execution ===
  

pt_model_path = "yolov8n.pt"  # You can change this to your custom model
onnx_model_path = "yolov8n.onnx"

# Export model (only needed once)
export_to_onnx(pt_model_path)

# Run inference
run_onnx_inference(onnx_model_path)
