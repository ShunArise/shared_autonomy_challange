import pygame
import pygame_gui
from src.walkcontrol.walk_control import *
from src.robotjpegimageStream.robot_jpeg_image_stream import *


class JoystickHandler:
    def __init__(self, walk_control):

        #self.callback = callback
        self.walk_control = walk_control


    def get_joystick_values(self, joystick):
        try:
            # Hauptereignisschleife
            running = True
            while running:
                # Ereignisse durchgehen
                for event in pygame.event.get():
                    if event.type == pygame.JOYAXISMOTION:
                        print("JOY_AXIS_MOTION")
                        # Skaliere die Joystick-Achswerte (im Bereich -1 bis 1)
                        x_value = joystick.get_axis(0)
                        y_value = joystick.get_axis(1)
                        x_value2 = joystick.get_axis(2)
                        y_value2 = joystick.get_axis(3)


                        # Ausgabe der Vektoren
                        self.callback(x_value, y_value, x_value2, y_value2)

                    elif event.type == pygame.JOYBUTTONDOWN:
                        # Behandle Knopfdruck-Ereignisse
                        print(f"Joystick {event.joy} Button {event.button} pressed.")

                        if event.button == 7:  # Shoot left
                            self.button_callback(event.button, "shootL")
                        elif event.button == 8:  # Shoot right
                            self.button_callback(event.button, "shootR")
                        elif event.button == 6:
                            self.button_callback(event.button, "align")

                    elif event.type == pygame.JOYBUTTONUP:
                        # Behandle Knopfloslass-Ereignisse
                        print(f"Joystick {event.joy} Button {event.button} released.")
                        if event.button in {7, 8}:
                            self.button_callback(event.button, "shootstop")
                        elif event.button == 6:
                            self.button_callback(event.button, "alignstop")

                    elif event.type == pygame.QUIT:
                        running = False # false to break While True

        finally:
            pygame.quit()
    def button_callback(self, button, action):
        print(f"Button {button} action: {action}")
        if button == 8 and action == "shootR":
            self.walk_control.walk_tuner.options["mode"].value = WalkModes.SHOOT_RIGHT.value

        elif button == 8 and action == "shootstop":
            self.walk_control.walk_tuner.options["mode"].value = WalkModes.WALK_STAND.value


    def joystick_callback(self, x1, y1, x2, y2):

        vx = y1 * 5  # Skalierung der Geschwindigkeit
        vy = x1 * 5  #  Test 5
        va = x2 * 5
        print(f"vx: ", {vx}, "vy: ", {vy}, "va: ", {va})
        self.walk_control.set_velocity(-vx, -vy, -va)


