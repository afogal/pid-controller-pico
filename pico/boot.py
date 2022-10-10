"""Control access to storage

Paraphrasing: https://learn.adafruit.com/circuitpython-essentials/circuitpython-storage
"This "boot.py" file executes on a hard reset or powering up the board.
It is not run on soft reset, e.g., reloading the board from the serial console
or the REPL. This is in contrast to the code within code.py, which is executed after CircuitPython is already running."

Following the adafruit example (link above), we check the status of a digital
input.  If it is held low then circuitpython can write to storage.  Otherwise,
the computer connected via the usb serial port can write to storage.

Note that even if you cannot write to CIRCUITPY over USB, you will be able
to read.
"""

import board
import digitalio
import storage

switch = digitalio.DigitalInOut(board.GP0)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

# allow CircuitPython to write to drive if input is grounded:
if switch.value:
    print("circuitpython can NOT write to storage, USB CAN")
else:
    print("circuitpython can write to storage, USB can NOT")
storage.remount("/", switch.value)
