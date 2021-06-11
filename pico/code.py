import board
import busio
import digitalio
import time
from adafruit_wiznet5k.adafruit_wiznet5k import WIZNET5K
import adafruit_wiznet5k.adafruit_wiznet5k_socket as socket
from busio import I2C
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import json
import math

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

# Default settings (see README)
defaultSettings = {'setCurrent':0, 'setTemp' : 25, 'Kc': 10, 'Ti':100, 'loadResist':5, 'maxTemp':150, 'maxCurr':2.5, 'maxResVolt':5, 'maxRes':13,
                   'maxSuppCurrVolt':5, 'maxSuppCurr':2, 'thermBeta':3380, 'thermR25':10, 'outputToggle':0, 'filterHz':1, 'period':16666667,
                   'constCurr':False, 'maxErrorLen':100 }

# PID variables
P_Signal = 0
I_Signal = 0
Erorr_Signal = 0
TemperatureDetents = 10 # gives a resolution of 0.1 DegC
CurrentDetents = 100 # gives a resolution of 0.01 A
Error_Sample_Value = []
Error_Sample_Time = []

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
        defaultSettings['setTemp'] = floor(jc['temp'] * TemperatureDetents) / TemperatureDetents
        I_Signal = defaultSettings['setCurrent'] * defaultSettings['setCurrent'] * defaultSettings['loadResist']
        defaultSettings['constCurr'] = False
    elif jc['command'] == "setcurr":
        defaultSettings['setCurrent'] = floor(jc['curr'] * CurrentDetents) / CurrentDetents
        defaultSettings['constCurr'] = True
    elif jc['command'] == "toggle":
        defaultSettings['outputToggle'] = not jc['toggle']
    
    # probably do something and then conditionally ack?
    client.publish("pico/feeds/ack", "ACK")

def Kohm_to_Celsius (Thermistor_Resistance):
    if (Thermistor_Resistance <= 0):
   	    return 0
    Celsius = (defaultSettings['thermBeta'] / (math.log(Thermistor_Resistance / defaultSettings['thermR25']) + defaultSettings['thermBeta'] / 298)) - 273
    return Celsius

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
    ethi = True
except RuntimeError:
    conn = False
    ethi = True
except AssertionError: # no cable
    conn = False
    ethi = False

# Display IP
space = ''.join([" " for i in range(8)])
if conn:
    lcd_str(i2c_bus, f"INET OK {space}{eth.pretty_ip(eth.ip_address)}")
elif ethi:
    lcd_str(i2c_bus, "No Broker!")
else:
    lcd_str(i2c_bus, "No eth!")

counter = 0
Bad_Frame_Counter = 0
t_last = time.monotonic_ns()
t_conn = time.monotonic_ns()
t_frame = time.monotonic_ns()
while True:
    
    # time variables
    t_curr = time.monotonic_ns()
    t_delta = t_curr - t_last
    frame_duration = t_curr - t_frame
    
    if t_delta > 50e8:  # 5 sec
        try: # I think this throws socket.timeout error
            mqtt_client.loop(timeout=0.01)
            mqtt_client.publish('pico/feeds/state', json.dumps({"temp" :Actual_Temperature, "curr":Control_Signal_Amps, "state":defaultSettings }))
            #mqtt_client.publish('pico/feeds/settings', json.dumps(defaultSettings))
            conn = True
        except:
            conn = False
            
        led.value = not led.value
        #mqtt_client.publish('afogal/feeds/therm', meas)
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
            t_conn = t_curr
            
    if frame_duration >= defaultSettings['period']:
        # read inputs:
        supplyCurrVolt = 0
        actResVolt = 0

        # Get current state
        Actual_Resistance = defaultSettings['maxRes'] * actResVolt / defaultSettings['maxResVolt']
        if (Actual_Resistance == defaultSettings['thermR25']):
            Actual_Temperature = 25
        elif ((Actual_Resistance <= 0) or (Actual_Resistance > defaultSettings['maxRes'])):
            Actual_Temperature = 0
        else:
            Actual_Temperature = Kohm_to_Celsius(Actual_Resistance)

        Supply_Current = defaultSettings['maxSuppCurr'] * Supply_Current_Voltage / defaultSettings['maxSuppCurrVolt']

        Error_Sample_Value.append(defaultSettings['setTemp'] - Actual_Temperature)
        Error_Sample_Time.append(time.monotonic_ns())

        # Now go through the list and add up the values with an exponential weighting function
        Error_Signal = 0
        Total_Weight = 0
        for i in range(len(Error_Sample_Value)):
            # find the time in seconds between when this data point was acquired, and present time
            Relative_Time = (Error_Sample_Time[-1] - Error_Sample_Time[i]) / 1e9
            Sample_Weight = math.exp(- Relative_Time / defaultSettings['filterHz'])
            Error_Signal += Sample_Weight * Error_Sample_Value[i]
        Total_Weight += Sample_Weight
        Error_Signal /= Total_Weight

        if (len(Error_Sample_Value) >= defaultSettings['maxErrorLen']):
            del Error_Sample_Value[0]
            del Error_Sample_Time[0]



        if defaultSettings['constCurr']:
            Control_Signal_Amps = defaultSettings['setCurrent'])
        else: # PID stuff goes here
            P_Signal = defaultSettings['Kc'] * Error_Signal
            I_Signal += (defaultSettings['Kc'] / defaultSettings['Ti']) * Error_Signal * Frame_Duration

            Control_Signal_Watts = P_Signal + I_Signal
            if (Control_Signal_Watts < 0):
                Control_Signal_Watts = 0

            Control_Signal_Amps = sqrt(Control_Signal_Watts / defaultSettings['loadResist'])

            if (Control_Signal_Amps > Settings.Max_Load_Current):
                Control_Signal_Amps = defaultSettings['maxCurr']
            if (Control_Signal_Amps > Settings.Max_Supply_Current):
                Control_Signal_Amps = defaultSettings['maxSuppCurr']

        # if the current being monitored is less than a half
        # of the current control signal, then increment a counter.
        # when this counter indicates that the actual current is so far from
        # desired current for over ten frames, then turn off the output and
        # print an error message.
        if (defaultSettings['outputToggle'] and Control_Signal_Amps > 0):
            if ((Supply_Current / Control_Signal_Amps < 0.5) or (Supply_Current / Control_Signal_Amps > 1.5)):
                Bad_Frame_Counter += 1
            else:
                Bad_Frame_Counter = 0
            if (Bad_Frame_Counter > 200):
                Bad_Frame_Counter = 0
                defaultSettings['outputToggle'] = 0
                lcd_str(i2c_bus, "Current Error!")

        # if the current signal is activated, and the temperature is within
        # range such that we are allowed to apply a current, then output the
        # current signal to the DAC
        if ((Actual_Temperature > defaultSettings['maxTemp']) or ( not defaultSettings['outputToggle'])):
           DAC_Output(0)
           Control_Signal_Amps = 0
        else:
           DAC_Output(Control_Signal_Amps)

        space = ''.join([" " for i in range(4)])
        lcd_str(i2c_bus, f"Temp: {Actual_Temperature:06.2f}{space}Curr: {Control_Signal_Amps:05.2f}")
        t_frame = time.monotonic_ns()

    # voltage = counter & 255
    # msg = voltage  >> 4
    # msg = [ msg, (voltage & 15) << 4]
    # i2c_bytes(i2c_bus, msg, dac_addr)
    # counter += 1


    #time.sleep(0.01)





