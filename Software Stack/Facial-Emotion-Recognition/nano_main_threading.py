import cv2
import time
import os
import pyttsx3
import numpy as np
import threading
import speech_recognition as sr
import onnxruntime as ort
import torch
from ultralytics.utils.ops import non_max_suppression
from conversation_handler import ConversationHandler
from groq import Groq

# ---------------- Config ----------------
os.environ['GROQ_KEY'] = 'x'
MAX_RETRIES = 3

# ---------------- Audio Setup ----------------
recognizer = sr.Recognizer()
mic = sr.Microphone()
engine = pyttsx3.init()
engine.setProperty('rate', 160)

def speak(text):
    print(f"Bot: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    with mic as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        speak("Sorry, I didn’t catch that.")
        return None
    except sr.RequestError:
        speak("Speech service is unavailable.")
        return None

# ---------------- Groq Chat Client ----------------
class LlamaRetriever:
    def __init__(self, model='llama3-70b-8192'):
        self.client = Groq(api_key=os.environ['GROQ_KEY'])
        self.model = model

    def call_api(self, prompt, system_message="You are a chatbot. Respond clearly and concisely."):
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        for _ in range(MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=self.model
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"[Groq API Error]: {e}")
                time.sleep(2)
        return "Sorry, I couldn't get a response right now."

# ---------------- Inference Setup ----------------
onnx_model_path = "C:/Users/Hassan Muhammad Khan/Desktop/YOLO script/yolov8n.onnx"
session = ort.InferenceSession(onnx_model_path, providers=['CPUExecutionProvider'])
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

def preprocess(image):
    img = cv2.resize(image, (640, 640))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.transpose(2, 0, 1).astype(np.float32) / 255.0
    return np.expand_dims(img, axis=0)

def postprocess(output, conf_thres=0.3, iou_thres=0.45):
    output = torch.tensor(output[0])
    pred = non_max_suppression(output, conf_thres=conf_thres, iou_thres=iou_thres)[0]
    boxes = []

    if pred is not None:
        for det in pred:
            x1, y1, x2, y2, conf, cls = det
            if int(cls.item()) == 0:  # Person class
                boxes.append((int(x1), int(y1), int(x2), int(y2), float(conf)))
    return boxes

# ---------------- Shared Variables for Threading ----------------
latest_frame = None
latest_boxes = []
frame_lock = threading.Lock()
stop_event = threading.Event()

# ---------------- Inference Worker Thread ----------------
def inference_worker(cap):
    global latest_frame, latest_boxes
    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            continue

        input_tensor = preprocess(frame)
        output = session.run([output_name], {input_name: input_tensor})
        boxes = postprocess(output)

        with frame_lock:
            latest_frame = frame.copy()
            latest_boxes = boxes

# ---------------- Main ----------------
print("Starting ONNX YOLOv8 ChatBot with Threading")
cap = cv2.VideoCapture(0)
llama = LlamaRetriever()
conv = ConversationHandler(speak_fn=speak, listen_fn=listen, llama_fn=lambda prompt: llama.call_api(prompt))

# Start inference thread
thread = threading.Thread(target=inference_worker, args=(cap,))
thread.start()

while True:
    start = time.time()
    with frame_lock:
        frame = latest_frame.copy() if latest_frame is not None else None
        boxes = latest_boxes.copy()

    if frame is not None:
        for x1, y1, x2, y2, conf in boxes:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f'Person {conf:.2f}', (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Handle interaction when a person is detected
            should_exit = conv.handle_interaction()
            if should_exit:
                stop_event.set()
                cap.release()
                thread.join()
                cv2.destroyAllWindows()
                exit(0)
            break

        #fps = 1.0 / (time.time() - start)
        #cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.imshow("ONNX - Person Detection ChatBot", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        stop_event.set()
        break

cap.release()
thread.join()
cv2.destroyAllWindows()

