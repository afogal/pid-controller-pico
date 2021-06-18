import board
import busio
import digitalio
import time
from adafruit_wiznet5k.adafruit_wiznet5k import WIZNET5K
import adafruit_wiznet5k.adafruit_wiznet5k_socket as socket
from busio import I2C
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import json
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.ads1x15 import Mode

from adafruit_ads1x15.analog_in import AnalogIn



##### Constants ############################

# I2C bus stuff (dac/lcd)
i2c_scl = board.GP21
i2c_sda = board.GP20
dac_addr = 0x60
lcd_addr = 0x72
adc_addr = 0x48

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



##### Setup ############################

# i2c bus and lcd init, show splash
i2c_bus = I2C(i2c_scl, i2c_sda)
lcd_str(i2c_bus, "PID Temp Control V0.01")



import adafruit_mcp4725
dac = adafruit_mcp4725.MCP4725(i2c_bus, address=96)
dac.raw_output = 2000 # for whatever reason doesnt work, have to use .value

ads = ADS.ADS1115(i2c_bus, address=adc_addr)
curr_adc = AnalogIn(ads, ADS.P3)
therm_adc = AnalogIn(ads, ADS.P0)
#ads.mode = Mode.CONTINUOUS
ads.data_rate = 860

# First ADC channel read in continuous mode configures device
# and waits 2 conversion cycle
_ = curr_adc.value
_ = therm_adc.value

counter = 200
t_last = time.monotonic_ns()
t_conn = time.monotonic_ns() 

#dac.raw_output = 4905 #*0.8
# voltage = counter & 255
# msg = voltage  >> 4
# msg = [ msg, (voltage & 15) << 4]
# i2c_bytes(i2c_bus, msg, dac_addr)


while True:
    
    lcd_str(i2c_bus, f"T_V: {therm_adc.voltage} C_V: {curr_adc.voltage}")
    time.sleep(1)





