import board
import busio
import digitalio
import time
from adafruit_wiznet5k.adafruit_wiznet5k import WIZNET5K
import adafruit_wiznet5k.adafruit_wiznet5k_socket as socket
from busio import I2C
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import json

##### Constants ############################

# I2C bus stuff (dac/lcd)
i2c_scl = board.GP21
i2c_sda = board.GP20
dac_addr = 0x60
lcd_addr = 0x72

# SPI bus stuff (eth)
SPI1_SCK = board.GP10
SPI1_TX = board.GP11
SPI1_RX = board.GP12
SPI1_CSn = board.GP13
W5500_RSTn = board.GP15

# eth config
MY_MAC = (0x00, 0x01, 0x02, 0x03, 0x04, 0x05)
IP_ADDRESS = (192, 168, 0, 111)
SUBNET_MASK = (255, 255, 255, 0)
GATEWAY_ADDRESS = (192, 168, 0, 1)
DNS_SERVER = (8, 8, 8, 8)
REMOTE_IP = "192.168.0.118"
REMOTE_PORT = 5005

# Some pin setup
led = digitalio.DigitalInOut(board.GP25)
led.direction = digitalio.Direction.OUTPUT

ethernetRst = digitalio.DigitalInOut(W5500_RSTn)
ethernetRst.direction = digitalio.Direction.OUTPUT

cs = digitalio.DigitalInOut(SPI1_CSn)
spi_bus = busio.SPI(SPI1_SCK, MOSI=SPI1_TX, MISO=SPI1_RX)


##### Functions ############################

# LCD clear screen
def lcd_clr(i2c_bus):
    # Lock the i2c bus
    while not i2c_bus.try_lock():
        pass
    try:
        i2c_bus.writeto(lcd_addr, bytes([0x7C, 0x2D]))  # clear screen
        time.sleep(1. / 1000.)  # 1ms in between writes
    finally:
        i2c_bus.unlock()


# Writing a string to the LCD
def lcd_str(i2c_bus, outs, clear=True):
    # Lock the i2c bus
    while not i2c_bus.try_lock():
        pass
    try:
        if clear: i2c_bus.writeto(lcd_addr, bytes([0x7C, 0x2D]))  # clear screen
        time.sleep(1. / 1000.)  # 1ms in between writes
        i2c_bus.writeto(lcd_addr, bytes([ord(i) for i in list(outs)]))
    finally:
        i2c_bus.unlock()


# Writing a bytelist to the LCD
def i2c_bytes(i2c_bus, outb, addr):
    # Lock the i2c bus
    while not i2c_bus.try_lock():
        pass
    try:
        i2c_bus.writeto(addr, bytes(outb))
        time.sleep(1./1000.)
    finally:
        i2c_bus.unlock()


def do_command(client, topic, message):
    #lcd_str(i2c_bus, message)
    
    jc = json.loads(message)
    
    if jc['command'] == "ping":
        client.publish("pico/feeds/ack", "PONG")
        
    elif jc['command'] == "settemp":
        set_temp(jc['temp'])
    
    # probably do something and then conditionally ack?
    client.publish("pico/feeds/ack", "ACK")

def set_temp(new_temp):
    pass

##### Setup ############################

# i2c bus and lcd init, show splash
i2c_bus = I2C(i2c_scl, i2c_sda)
lcd_str(i2c_bus, "PID Temp Control V0.01")
# lcd_bytes(i2c_bus, [0x0A]) # Sets text as splash
time.sleep(1)
lcd_clr(i2c_bus)

# Reset W5500 first
ethernetRst.value = False
time.sleep(0.1)
ethernetRst.value = True

# Initialize ethernet interface without DHCP
eth = WIZNET5K(spi_bus, cs, is_dhcp=False, mac=MY_MAC)

# Set network configuration
eth.ifconfig = (IP_ADDRESS, SUBNET_MASK, GATEWAY_ADDRESS, DNS_SERVER)

# Configure UDP
socket.set_interface(eth)
# sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock_udp.settimeout(0.1)

# Display IP
space = ''.join([" " for i in range(8)])
lcd_str(i2c_bus, f"INET OK {space}{eth.pretty_ip(eth.ip_address)}")

#eth._debug = True
MQTT.set_socket(socket, eth)
time.sleep(1)
mqtt_client = MQTT.MQTT("192.168.0.103", username='pico', password='password', is_ssl=False, port=5005)
#mqtt_client = MQTT.MQTT('io.adafruit.com', username='afogal', password='', is_ssl=False, port=1883)
mqtt_client.on_message = do_command

try:
    mqtt_client.connect(clean_session=False)
    time.sleep(0.01)
    mqtt_client.subscribe("server/feeds/commands", qos=1)
    time.sleep(0.01)
    conn = True
except RuntimeError:
    conn = False

counter = 0
t_last = time.monotonic_ns()
t_conn = time.monotonic_ns()
while True:
    t_curr = time.monotonic_ns()
    t_delta = t_curr - t_last
   
    meas = 0
    
    if t_delta > 50e8:  # Half a second
        try: # I think this throws socket.timeout error
            mqtt_client.loop(timeout=0.01)
            mqtt_client.publish('pico/feeds/therm', meas)
            conn = True
        except:
            conn = False
            
        led.value = not led.value
        #mqtt_client.publish('afogal/feeds/therm', meas)
        #sock_udp.sendto(b"Hello World!", ('192.168.0.255', REMOTE_PORT))
        t_last = t_curr
        
    if t_curr - t_conn > 300e8 and not conn: # 30s
        try:
            mqtt_client.connect(clean_session=False)
            time.sleep(0.01)
            mqtt_client.subscribe("server/feeds/commands", qos=1)
            time.sleep(0.01)
            conn = True
            t_conn = t_curr
        except:
            conn = False

    voltage = counter & 511
    msg = voltage  >> 4
    msg = [ msg, (voltage & 15) << 4]
    i2c_bytes(i2c_bus, msg, dac_addr)
    counter += 1

    
    time.sleep(0.01)






