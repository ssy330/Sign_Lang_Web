from flask import Flask, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import pickle
import cv2
import mediapipe as mp
import numpy as np
import time

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Load the trained model
with open("voting_cross_validated.p", "rb") as f:
    model = pickle.load(f)

# Mediapipe settings
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# 카메라 열기
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

current_alphabet = None
last_detected_time = None
sentence = ""
last_added_time = None
reset_time = None
dot_added_time = None

def generate_frames():
    global current_alphabet, last_detected_time, sentence, last_added_time, reset_time, dot_added_time

    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to capture frame from camera")
            break

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)
        now = time.time()

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                data_point = []
                for landmark in hand_landmarks.landmark:
                    data_point.append(landmark.x)
                    data_point.append(landmark.y)

                data_point = np.array(data_point).reshape(1, -1)
                try:
                    prediction = model.predict(data_point)[0]
                except Exception as e:
                    print(f"Prediction error: {e}")
                    continue

                if prediction == current_alphabet:
                    if now - last_detected_time > 2:
                        if last_added_time is None or now - last_added_time > 2:
                            sentence += prediction
                            last_added_time = now
                            dot_added_time = None
                            socketio.emit('sentence_update', {'sentence': sentence})  # WebSocket으로 전송
                else:
                    current_alphabet = prediction
                    last_detected_time = now

                reset_time = now
                cv2.putText(frame, f'Current: {current_alphabet}', (10, frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        else:
            if sentence != "" and reset_time and now - reset_time > 2:
                if  dot_added_time is None:
                    sentence += "."
                    dot_added_time = now
                    socketio.emit('sentence_update', {'sentence': sentence})  # WebSocket으로 전송
                elif now - dot_added_time > 2:
                    socketio.emit('add_textbox', {'content': sentence})
                    sentence = ""
                    reset_time = None
                    dot_added_time = None
                    current_alphabet = None
                    socketio.emit('sentence_update', {'sentence': sentence})  # WebSocket으로 전송

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    import threading
    threading.Thread(target=generate_frames, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000)
