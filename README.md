# pid-controller-pico

---

## Setup

### Mosquitto (MQTT Broker)

Install mosquitto:

` sudo apt install mosquitto `

To run mosquitto in verbose mode:

` mosquitto -c mosquitto.conf -v `

To ensure it runs on startup (and run it now):

` sudo systemctl enable mosquitto && sudo systemctl start mosquitto `

You also have to copy the `mosquitto.conf`:

` sudo cp mosquitto.conf /etc/mosquitto/mosquitto.conf `

### RPi Pico

To setup the pico fresh, hold down the bootsel button and plug it into the computer. Download the latest adafruit circuitpython uf2 and the latest circuitpython library bundle. (Make sure the versions match, a new major revision is coming out soon, I used the old one, version 6.x.x). Then, drag and drop the circuitpython uf2 to the pico, it'll then remount itself. Now the pico will show up as a drive. Drag and drop the following files to the `lib` folder:

Folders:
* `adafruit_bus_device`
* `adafruit_minimqtt`
* `adafruit_wiznet5k`
Files:
* `adafruit_requests.mpy`

As for wiring, the ethernet is wired as follows:

![eth wiring](docs/eth_wiring.png)

The i2c bus is wired: pin 26 (GP20) - SDA, pin 27 (GP21) - SCL, and of course, ground to ground and 3v3 to 3v3.

In order to program the pico, all you have to do is copy the code.py to the pico, and it will then run that code on boot. One can also install the Thonny editor or the Mu editor. To one can then set Thonny to "Micropython" and point it at the correct serial port (com4 for me) and then you get a REPL running on the pico!


## Notes:

* printing (which prints to serial) puts a lot of delay
* you might have to reconfigure the IP and gatway of the pico depending on network architecture. Run `ipconfig` on windows or `ip addr` on linux to find the relevant details
