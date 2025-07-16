import cv2
import time
import numpy as np
import threading
import queue
import onnxruntime as ort
from ultralytics import YOLO
import torch
from ultralytics.utils.ops import non_max_suppression
import sounddevice as sd

# Azure OpenAI & Voice Assistant Imports
import os
import speech_recognition as sr
import pyttsx3
from openai import AzureOpenAI
import sys

# === Global Config ===
FRAME_QUEUE = queue.Queue(maxsize=5)
STOP_EVENT = threading.Event()
assistant_triggered = False  # Ensure assistant is only started once

# === Azure OpenAI Configuration ===
sys.stderr = open(os.devnull, 'w')  # Suppress ALSA stderr output
endpoint = "x"
model_name = "gpt-4o-mini"
deployment = "gpt-4o-mini"
subscription_key = "x"
api_version = "x"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

engine = pyttsx3.init()
engine.setProperty('rate', 160)  # Adjust TTS rate
recognizer = sr.Recognizer()

conversation = [
    {"role": "system", "content": "You are a helpful assistant. Give precise and to-the-point answers as a human would."}
]

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        time.sleep(1)
        audio = recognizer.listen(source, phrase_time_limit=5)
        time.sleep(2)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "I didn't catch that. Please repeat."
        except sr.RequestError:
            return "Sorry, speech service is unavailable."

def chat(user_input):
    conversation.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        messages=conversation,
        max_tokens=1024,
        temperature=1.0,
        top_p=1.0,
        model=deployment
    )
    reply = response.choices[0].message.content.strip()
    conversation.append({"role": "assistant", "content": reply})
    return reply

def start_voice_assistant():
    speak("Hello! I'm your voice assistant. What would you like to talk about?")
    while True:
        user_input = listen()
        print("You said:", user_input)

        if "goodbye" in user_input.lower():
            speak("Goodbye! Have a great day.")
            break

        reply = chat(user_input)
        print("Assistant:", reply)
        speak(reply)
        time.sleep(5)

# === Step 1: Export YOLO model to ONNX (once) ===
def export_to_onnx(pt_path):
    model = YOLO(pt_path)
    model.export(format="onnx", simplify=True, opset=12)
    print(f"Model exported to ONNX from {pt_path}")

# === Thread 1: Capture frames continuously ===
def frame_capture_thread(cap):
    while not STOP_EVENT.is_set():
        ret, frame = cap.read()
        if not ret:
            continue
        if not FRAME_QUEUE.full():
            FRAME_QUEUE.put(frame)
        time.sleep(0.01)

# === Thread 2: Run inference and show results ===
def inference_thread(onnx_model_path):
    global assistant_triggered
    session = ort.InferenceSession(onnx_model_path, providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    print("Starting threaded person detection... Press 'q' to quit.")
    while not STOP_EVENT.is_set():
        if FRAME_QUEUE.empty():
            continue

        frame = FRAME_QUEUE.get()
        start_time = time.time()

        # Preprocess for YOLO
        img = cv2.resize(frame, (640, 640))
        img_input = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_input = img_input.transpose(2, 0, 1)
        img_input = img_input.astype(np.float32) / 255.0
        img_input = np.expand_dims(img_input, axis=0)

        # Inference
        outputs = session.run([output_name], {input_name: img_input})[0]

        # Postprocess: NMS
        pred = non_max_suppression(torch.tensor(outputs), conf_thres=0.25, iou_thres=0.45)[0]

        for det in pred:
            x1, y1, x2, y2, conf, cls = det
            if int(cls.item()) == 0:  # Person
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                conf = float(conf.item())

                if conf >= 0.80 and not assistant_triggered:
                    assistant_triggered = True
                    threading.Thread(target=start_voice_assistant).start()

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f'Person {conf:.2f}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # FPS display
        fps = 1.0 / (time.time() - start_time)
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("YOLOv8 ONNX - Person Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            STOP_EVENT.set()
            break

    cv2.destroyAllWindows()

# === Main Execution ===
def main():
    pt_model_path = "yolov8n.pt"
    onnx_model_path = "yolov8n.onnx"

    # Export ONNX model if needed
    if not os.path.exists(onnx_model_path):
        export_to_onnx(pt_model_path)

    # Open webcam (0 or 1 depending on your camera index)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Camera not accessible")
        return

    # Start threads
    t1 = threading.Thread(target=frame_capture_thread, args=(cap,))
    t2 = threading.Thread(target=inference_thread, args=(onnx_model_path,))
    t1.start()
    t2.start()

    # Wait for threads to complete
    t1.join()
    t2.join()
    cap.release()

if __name__ == "__main__":
    main()
