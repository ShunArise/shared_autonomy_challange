import socket
import pygame
import threading
import math
from io import BytesIO
from PIL import Image
import threading

from src.naobackend.robot_jpeg_image_stream import RobotJpegImageStream
import src.naoshow.SPLStandartMessage as SPL

class NaoControl(threading.Thread):
    def __init__(self, robot_addr, running, window_size=(1040, 740)):
        threading.Thread.__init__(self)

        self.robot_addr = robot_addr
        self.window_size = window_size
        self.field_width = 900
        self.field_height = 600
        self.margin = 70
        self.img_width = 640
        self.img_height = 960
        self.robots = {}
        self.ball = None
        self.needs_update = True
        self.running = running
        self.camera_thread = self.CameraStream(self.robot_addr)
        self.camera_thread.start()
        self.thread_udp = self.UDPReceiver(self)
        self.thread_udp.start()


        pygame.init()
        pygame.display.set_caption("NaoControl")
        self.window = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Draw the field and robots
            width, height = pygame.display.get_window_size()
            self.draw_field(width, height)

            if self.camera_thread.image:
                self.display_camera_feed(width, height)

        pygame.quit()
        self.camera_thread.join()
        self.thread_udp.join()

    def draw_field(self, width, height):
        color_green = (0, 255, 0)
        color_blue = (0, 0, 255)
        color_white = (255, 255, 255)
        color_orange = (255, 165, 0)

        # Calculate total dimensions including margins
        total_width = self.field_width + 2 * self.margin
        total_height = self.field_height + 2 * self.margin

        # Calculate scaling factors
        scale = min((width - self.img_width) / total_width, height / total_height)
        scaled_field_width = self.field_width * scale
        scaled_field_height = self.field_height * scale
        scaled_margin = self.margin * scale
        margin_x = self.img_width + (width - self.img_width - scaled_field_width - 2 * scaled_margin) // 2
        margin_y = (height - scaled_field_height - 2 * scaled_margin) // 2

        # Draw the field
        self.window.fill(color_green)
        pygame.draw.rect(self.window, color_white,
                         [margin_x + scaled_margin, margin_y + scaled_margin, scaled_field_width, scaled_field_height], 5)
        pygame.draw.line(self.window, color_white, [margin_x + scaled_margin + scaled_field_width / 2, margin_y + scaled_margin],
                         [margin_x + scaled_margin + scaled_field_width / 2,
                          margin_y + scaled_margin + scaled_field_height], 5)
        pygame.draw.line(self.window, color_white, [margin_x + scaled_margin + scaled_field_width / 2 - 5,
                                                   margin_y + scaled_margin + scaled_field_height / 2],
                         [margin_x + scaled_margin + scaled_field_width / 2 + 5,
                          margin_y + scaled_margin + scaled_field_height / 2], 5)
        pygame.draw.circle(self.window, color_white, [int(margin_x + scaled_margin + scaled_field_width / 2),
                                                     int(margin_y + scaled_margin + scaled_field_height / 2)], int(75 * scale),
                           5)
        pygame.draw.rect(self.window, color_white,
                         [margin_x + scaled_margin, margin_y + scaled_margin + scaled_field_height / 6, 165 * scale,
                          400 * scale], 5)
        pygame.draw.rect(self.window, color_white,
                         [margin_x + scaled_margin, margin_y + scaled_margin + scaled_field_height / 3, 60 * scale,
                          220 * scale], 5)
        pygame.draw.line(self.window, color_white,
                         [margin_x + scaled_margin + 125 * scale, margin_y + scaled_margin + scaled_field_height / 2],
                         [margin_x + scaled_margin + 135 * scale, margin_y + scaled_margin + scaled_field_height / 2], 5)
        pygame.draw.line(self.window, color_white,
                         [margin_x + scaled_margin + 130 * scale, margin_y + scaled_margin + scaled_field_height / 2 - 5],
                         [margin_x + scaled_margin + 130 * scale, margin_y + scaled_margin + scaled_field_height / 2 + 5],
                         5)
        pygame.draw.rect(self.window, color_white, [margin_x + scaled_margin + scaled_field_width - 165 * scale,
                                                   margin_y + scaled_margin + scaled_field_height / 6, 165 * scale,
                                                   400 * scale], 5)
        pygame.draw.rect(self.window, color_white, [margin_x + scaled_margin + scaled_field_width - 60 * scale,
                                                   margin_y + scaled_margin + scaled_field_height / 3, 60 * scale, 220 * scale],
                         5)
        pygame.draw.line(self.window, color_white, [margin_x + scaled_margin + scaled_field_width - 135 * scale,
                                                   margin_y + scaled_margin + scaled_field_height / 2],
                         [margin_x + scaled_margin + scaled_field_width - 125 * scale,
                          margin_y + scaled_margin + scaled_field_height / 2], 5)
        pygame.draw.line(self.window, color_white, [margin_x + scaled_margin + scaled_field_width - 130 * scale,
                                                   margin_y + scaled_margin + scaled_field_height / 2 - 5],
                         [margin_x + scaled_margin + scaled_field_width - 130 * scale,
                          margin_y + scaled_margin + scaled_field_height / 2 + 5], 5)

        # Draw Robots with direction and IDs
        for id, pos in self.robots.items():
            x = margin_x + scaled_margin + (pos['x'] / 10) * scale + scaled_field_width / 2
            y = margin_y + scaled_margin + scaled_field_height / 2 - (pos['y'] / 10) * scale

            pygame.draw.circle(self.window, color_blue, [int(x), int(y)], 10, 0)

            angle = pos['a']
            length = 20 * scale
            end_x = x + length * math.cos(angle)
            end_y = y - length * math.sin(angle)

            pygame.draw.line(self.window, color_white, (x, y), (end_x, end_y), 2)

            font = pygame.font.SysFont("Arial", 15)
            text = font.render(str(id), True, color_white)
            textRect = text.get_rect()
            textRect.center = (int(x), int(y))
            self.window.blit(text, textRect)

        # Draw the ball
        if self.ball is not None:
            ball_x = margin_x + scaled_margin + (self.ball['x'] / 10) * scale + scaled_field_width / 2
            ball_y = margin_y + scaled_margin + scaled_field_height / 2 - (self.ball['y'] / 10) * scale
            pygame.draw.circle(self.window, color_orange, [int(ball_x), int(ball_y)], 5, 0)

        pygame.display.flip()

    def display_camera_feed(self, window_width, window_height):
        # Calculate the new size while maintaining the aspect ratio
        img_width, img_height = self.camera_thread.image.get_size()
        aspect_ratio = img_width / img_height

        if window_width / window_height > aspect_ratio:
            new_width = window_height * aspect_ratio
            new_height = window_height
        else:
            new_width = window_width
            new_height = window_width / aspect_ratio

        # Resize the image while maintaining aspect ratio
        resized_image = pygame.transform.scale(self.camera_thread.image, (int(new_width), int(new_height)))
        self.window.blit(resized_image, (0, 0))

    class UDPReceiver(threading.Thread):
        infocast_port = 20013

        def __init__(self, nao_control):
            threading.Thread.__init__(self)
            self.nao_control = nao_control

        def run(self):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(("", self.infocast_port))

            while self.nao_control.running:
                data, addr = sock.recvfrom(1024)
                robot_id = addr[0].split(".")[3]
                msg = SPL.SPLStandardMessage(data)
                if msg.position != {'x': 0, 'y': 0, 'a': 0}:
                    self.nao_control.robots[robot_id] = msg.position
                    self.nao_control.ball = {'x': msg.ball['x'], 'y': msg.ball['y']}
                    self.nao_control.needs_update = True

    class CameraStream(threading.Thread):
        def __init__(self, robot_addr):
            threading.Thread.__init__(self)
            self.stream = RobotJpegImageStream(robot_addr)
            self.image = None
            self.img_upper = None
            self.img_lower = None

        def run(self):
            global running
            # Fetch images from the robot
            try:
                self.img_upper = Image.open(BytesIO(self.stream.images_upper_cam.get_nowait()))
            except:
                pass

            try:
                self.img_lower = Image.open
            except:
                pass
