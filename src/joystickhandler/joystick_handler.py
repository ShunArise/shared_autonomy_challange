import threading

import pygame
import pygame_gui
from src.walkcontrol.walk_control import WalkControl
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JoystickHandler(threading.Thread):
    def __init__(self, walk_control, joystick, running):
        threading.Thread.__init__(self)

        self.walk_control = walk_control
        self.joystick = joystick
        logger.info("JoystickHandler initialized and started :) I hope so")
        self.running = running

    def run(self):

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    self.handle_axis_motion(event, self.joystick)
                elif event.type == pygame.JOYBUTTONDOWN:
                    self.handle_button_down(event)
                elif event.type == pygame.JOYBUTTONUP:
                    self.handle_button_up(event)
                elif event.type == pygame.QUIT:
                    self.running = False
            pygame.time.delay(10)  # Reduce CPU usage
        pygame.quit()

    def handle_axis_motion(self, event, joystick):
        x_value = joystick.get_axis(0)
        y_value = joystick.get_axis(1)
        x_value2 = joystick.get_axis(2)
        y_value2 = joystick.get_axis(3)
        r1 = joystick.get_axis(4)  # ZL
        r2 = joystick.get_axis(5)  # ZR

        logger.debug(f"Axis values: {x_value}, {y_value}, {x_value2}, {y_value2}, {r1}, {r2}")
        self.joystick_callback(x_value, y_value, x_value2, y_value2, r1, r2)

    def handle_button_down(self, event):
        logger.info(f"Joystick {event.joy} Button {event.button} pressed.")
        action = "shoot" if event.button == 0 else "teamcomm_button" if event.button == 11 else None
        if action:
            self.button_callback(event.button, action)

    def handle_button_up(self, event):
        logger.info(f"Joystick {event.joy} Button {event.button} released.")
        action = "shootstop" if event.button in {7, 8} else "alignstop" if event.button == 6 else None
        if action:
            self.button_callback(event.button, action)

    def button_callback(self, button, action):
        logger.info(f"Button {button} action: {action}")
        if button == 11 and action == "teamcomm_button":
            self.walk_control.strategy.options["button_pressed"].value = True

    def deadband_filter(self, min_value, value, max_value):
        if value < 0:
            value -= min_value
            if value > 0:
                value = 0
        if value > 0:
            value -= max_value
            if value < 0:
                value = 0
        return value

    def joystick_callback(self, x1, y1, x2, y2, r1, r2):
        if r2 >= 0.5:
            logger.info("[INFO]: Button pressed MANUAL")
            self.walk_control.strategy.options["button_pressed_manual"].value = True
        if r1 >= 0.5:
            logger.info("[INFO]: Button pressed AUTONOM")
            self.walk_control.strategy.options["button_pressed_autonom"].value = True
        if r1 <= 0.5 and r2 <= 0.5:
            self.walk_control.strategy.options["button_pressed_autonom"].value = False
            self.walk_control.strategy.options["button_pressed_manual"].value = False

        x1 = self.deadband_filter(-0.25, x1, 0.25)
        y1 = self.deadband_filter(-0.25, y1, 0.25)
        x2 = self.deadband_filter(-0.25, x2, 0.25)

        vx = y1 * 0.5  # Scale velocity
        vy = x1 * 0.5
        va = x2 * 2

        logger.debug(f"vx: {vx}, vy: {vy}, va: {va}")
        self.walk_control.set_velocity(-vx, -vy, -va)
