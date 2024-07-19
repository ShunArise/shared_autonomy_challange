import socket
import time

class UDPReceiver(threading.Thread):
    infocast_port = 20013
    
    def __init__(self, running, fps):
        threading.Thread.__init__(self)
        self.running = running
        self.fps = fps
        self.robots = {}
        
    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", self.infocast_port))

        while self.running:
            data, addr = sock.recvfrom(1024)
            robot_id = addr[0].split(".")[3]
            msg = SPL.SPLStandardMessage(data)
            if msg.position != {'x': 0, 'y': 0, 'a': 0}:
                self.robots[robot_id] = msg
            time.sleep(self.fps)
