import pygame

pygame.init()

# Controller initialisieren
pygame.joystick.init()

# Überprüfe verfügbare Joysticks/Controller
print(f"Es sind {pygame.joystick.get_count()} Joysticks verbunden")

if pygame.joystick.get_count() > 0:
    # Wähle den ersten Controller aus
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print(f"Controller Name is: {joystick.get_name()}")

    while True:
        pygame.event.get()  # Wichtige Zeile für die Aktualisierung der Ereignisse

        # Lese die Achsen des Controllers aus (z.B. linkes und rechtes Steuerkreuz)
        axes = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
        print(f"Achsen: {axes}")
        print("")
        # Lese die Buttons des Controllers aus
        buttons = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]
        print(f"Buttons: {buttons}")


        pygame.time.delay(100)  # Kurze Pause, um die Ausgabe zu verlangsamen

pygame.quit()
