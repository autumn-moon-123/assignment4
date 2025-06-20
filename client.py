
import socket
import sys
import os
import base64
import random


class UDPClient:
    def __init__(self, server_host, server_port, filelist):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_host = server_host
        self.server_port = server_port
        self.filelist = filelist
        self.download_dir = os.getcwd()
    def download_file(self, filename):
        self.client_socket.sendto(f"DOWNLOAD {filename}".encode(), (self.server_host, self.server_port))
        response, _ = self.client_socket.recvfrom(1024)
        response = response.decode()

        if response.startswith("ERR"):
            print(f"ERR {filename} NOT_FOUND")
            return False
        
        parts = response.split()
        filename = parts[1]
        file_size = int(parts[3])
        data_port = int(parts[5])

        data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
        client_port = random.randint(51000, 52000)
        data_socket.bind(('0.0.0.0', client_port))

        file_path = os.path.join(self.download_dir, f"downloaded_{filename}")
        bytes_received = 0
        block_size = 512  

        with open(file_path, 'wb') as f:
            while bytes_received < file_size:
                start = bytes_received
                end = min(bytes_received + block_size - 1, file_size - 1)
                data_socket.sendto(f"FILE {filename} GET START {start} END {end}".encode(),
                                   (self.server_host, data_port))

                response, _ = data_socket.recvfrom(65536)
                response = response.decode()

                if response.startswith(f"FILE {filename} OK"):
                    data = base64.b64decode(response.split("DATA ")[1].encode())
                    f.write(data)
                    bytes_received += len(data)
                    print(f"Received {bytes_received}/{file_size} bytes")

            data_socket.sendto(f"FILE {filename} CLOSE".encode(), (self.server_host, data_port))
            data_socket.recvfrom(1024)  

        return bytes_received == file_size
