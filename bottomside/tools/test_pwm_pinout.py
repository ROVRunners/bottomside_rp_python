input("WARNING! Only continue if the ESCs are disconnected!")

import pigpio

gpio: pigpio.pi = pigpio.pi()

pin: int = int(input("Gimme pin number: "))
new_pin: int = pin

gpio.set_mode(pin, pigpio.OUTPUT)
gpio.write(pin, 1)

while True:
    new_pin = int(input("Gimme pin number: "))

    # Shut down the old pin.
    gpio.set_mode(pin, pigpio.OUTPUT)
    gpio.write(pin, 0)

    # Start up the new pin.
    pin = new_pin
    gpio.set_mode(pin, pigpio.OUTPUT)
    gpio.write(pin, 1)