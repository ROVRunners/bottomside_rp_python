import pygame
import serial
import time
import keyboard

# Set the serial port names for your Arduinos
arduino1_port = 'COM3'  # Replace with the correct port for Arduino 1
baudrate = 19200
timeout = 0.02
deadzone = .075

# Initialize serial communication
arduino1 = serial.Serial(arduino1_port, baudrate, timeout=timeout)

# Initialize pygame
pygame.init()


joy_count = pygame.joystick.get_count()
while not joy_count:
    print("No controller detected.")

# Set up the Xbox controller
controller = pygame.joystick.Joystick(0)
controller.init()

# Set up the keyboard
pygame.key.set_repeat(1, 1)  # Enable key repeat with a delay of 1 ms and a repeat rate of 1 ms
keys = pygame.key.get_pressed()

try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        values = [0, 0, 0, 0, 0, 0]

        # Get keyboard input
        if keyboard.is_pressed("w"):
            values[0] = 255
        if keyboard.is_pressed("s"):
            values[1] = 255
        if keyboard.is_pressed("a"):
            values[2] = 255
        if keyboard.is_pressed("d"):
            values[3] = 255
        if keyboard.is_pressed("up"):
            values[4] = 255
        if keyboard.is_pressed("down"):
            values[5] = 255
        # forward_backward_value = int((keys[pygame.K_w] - keys[pygame.K_s]) * 255)
        # up_down_value = int((keys[pygame.K_UP] - keys[pygame.K_DOWN]) * 255)
        # pivot_value = int((keys[pygame.K_d] - keys[pygame.K_a]) * 255)

        # Scale values to fit within the range -255 to 255 (Arduino motor control range)
        up_down_value = max(-255, min(255, up_down_value))
        forward_backward_value = max(-255, min(255, forward_backward_value))
        pivot_value = max(-255, min(255, pivot_value))

        # Send commands via serial to Arduinos
        print("Read: ", arduino1.readline()[0:-2])
        # arduino1.write(up_down_value.to_bytes())
        # arduino1.write(forward_backward_value.to_bytes())
        # arduino1.write(pivot_value.to_bytes())
        # arduino1.write(300.to_bytes())
        arduino1.write(f'{up_down_value} {forward_backward_value} {pivot_value}'.encode())
        # print(f'{up_down_value} {forward_backward_value} {pivot_value}'.encode())
        print(f'{up_down_value} {forward_backward_value} {pivot_value}'.encode())

        # Add a delay to control the update rate (adjust as needed)
        time.sleep(0.02)

except KeyboardInterrupt:
    print("Program terminated by user.")
    arduino1.close()
    pygame.quit()
