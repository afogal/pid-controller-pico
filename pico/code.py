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
import adafruit_mcp4725
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.ads1x15 import Mode
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_bus_device.i2c_device import I2CDevice

##### Constants ############################

# I2C bus stuff (dac/lcd/adc)
i2c_scl = board.GP21
i2c_sda = board.GP20
dac_addr = 0x60
lcd_addr = 0x72
adc1_addr = 0x48
adc2_addr = 0x49

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
REMOTE_IP = "192.168.0.100"
REMOTE_PORT = 5005

# Some pin setup
led = digitalio.DigitalInOut(board.GP25)
led.direction = digitalio.Direction.OUTPUT

ethernetRst = digitalio.DigitalInOut(W5500_RSTn)
ethernetRst.direction = digitalio.Direction.OUTPUT

cs = digitalio.DigitalInOut(SPI1_CSn)
spi_bus = busio.SPI(SPI1_SCK, MOSI=SPI1_TX, MISO=SPI1_RX)

# Default settings (see README)
defaultSettings = {'setCurrent':0, 'setTemp' : 30, 'Kc': 16, 'Ti':100000000, 'Td':0, 'I_max':2, 'loadResist':1, 'maxTemp':150, 'maxCurr':2.0, 'maxResVolt':5, 'maxRes':13,
                   'maxSuppCurrVolt':5, 'maxSuppCurr':2, 'thermBeta':3380, 'thermR25':10, 'outputToggle':1, 'filterHz':1, 'period':16666667,
                   'constCurr':False, 'maxErrorLen':100 }
# Attempt to load last used settings
try:
    with open('settings.json', 'r') as settings_file:
        defaultSettings = json.load(settings_file)
        loaded = True
except:
    loaded = False
    

# PID variables
P_Signal = 0
I_Signal = 0
Erorr_Signal = 0
TemperatureDetents = 10 # gives a resolution of 0.1 DegC
CurrentDetents = 100 # gives a resolution of 0.01 A
Error_Sample_Value = []
Error_Sample_Time = []

##### Functions ############################

# Writing a string to the LCD
def lcd_str(device, outs, clear=True):
    with device as lcd:
        if clear: lcd.write(bytes([0x7C, 0x2D]))
        time.sleep(1. / 1000.)  # 1ms in between writes
        lcd.write(bytes([ord(i) for i in list(outs)]))
        time.sleep(1./1000.)


# Run automatically when an MQTT message is recieved
def do_command(client, topic, message):
    #lcd_str(lcd, message)
    
    jc = json.loads(message)
    
    if jc['command'] == "ping":
        client.publish("pico/feeds/ack", "PONG")
    elif jc['command'] == "settemp":
        defaultSettings['setTemp'] = math.floor(jc['temp'] * TemperatureDetents) / TemperatureDetents
        I_Signal = 0 #defaultSettings['setCurrent'] * defaultSettings['setCurrent'] * defaultSettings['loadResist']
        defaultSettings['constCurr'] = False
        saveSettings()
    elif jc['command'] == "setcurr":
        defaultSettings['setCurrent'] = math.floor(jc['curr'] * CurrentDetents) / CurrentDetents
        defaultSettings['constCurr'] = True
        saveSettings()
    elif jc['command'] == "toggleOutput":
        defaultSettings['outputToggle'] = not defaultSettings['outputToggle'] #jc['toggle']
        saveSettings()
        
    # probably do something and then conditionally ack?
    client.publish("pico/feeds/ack", "ACK")

def Kohm_to_Celsius (Thermistor_Resistance):
    if (Thermistor_Resistance <= 0):
        return 0
    Celsius = (defaultSettings['thermBeta'] / (math.log(Thermistor_Resistance / defaultSettings['thermR25']) + defaultSettings['thermBeta'] / 298)) - 273
    return Celsius
    
    
def saveSettings():
    try:
        with open("settings.json", "w") as outfile:
            json.dump(defaultSettings, outfile)
    except:
        pass

##### Setup ############################

# i2c bus and lcd init, show splash
i2c_bus = I2C(i2c_scl, i2c_sda)
lcd = I2CDevice(i2c_bus, lcd_addr)
lcd_str(lcd, "PID Temp Control V0.01")
# lcd_bytes(i2c_bus, [0x0A]) # Sets text as splash
time.sleep(0.5)

# DAC and ADC setup
dac = adafruit_mcp4725.MCP4725(i2c_bus, address=dac_addr)
dac.value = 0
time.sleep(0.01)
ads = ADS.ADS1115(i2c_bus, address=adc1_addr)
curr_adc = AnalogIn(ads, ADS.P3)
therm_adc = AnalogIn(ads, ADS.P0)
#ads.mode = Mode.CONTINUOUS # this breaks everything
ads.data_rate = 860 # Max rate is 860

# ads2 = ADS.ADS1115(i2c_bus, address=adc2_addr)
# curr_adc = AnalogIn(ads2, ADS.P0)
# ads2.data_rate = 860

# First ADC channel read in continuous mode configures device
# and waits 2 conversion cycle
_ = curr_adc.value
_ = therm_adc.value

# Reset W5500 first
ethernetRst.value = False
time.sleep(0.1)
ethernetRst.value = True

# Initialize ethernet interface without DHCP
eth = WIZNET5K(spi_bus, cs, is_dhcp=False, mac=MY_MAC)

# Set network configuration
eth.ifconfig = (IP_ADDRESS, SUBNET_MASK, GATEWAY_ADDRESS, DNS_SERVER)
socket.set_interface(eth)

#eth._debug = True
MQTT.set_socket(socket, eth)
time.sleep(1)
mqtt_client = MQTT.MQTT("192.168.0.100", username='pico', password='password', is_ssl=False, port=5005, keep_alive=5)
mqtt_client.on_message = do_command

try:
    mqtt_client.connect(clean_session=False)
    time.sleep(0.01)
    mqtt_client.subscribe("server/feeds/commands", qos=1)
    time.sleep(0.01)
    conn = True
    ethi = True
except RuntimeError: # broker not online
    conn = False
    ethi = True
except AssertionError: # no cable
    conn = False
    ethi = False

# Display IP if everything ok
space = ''.join([" " for i in range(8)])
if conn:
    lcd_str(lcd, f"INET OK {space}{eth.pretty_ip(eth.ip_address)}")
elif ethi:
    lcd_str(lcd, "No Broker!")
else:
    lcd_str(lcd, "No eth!")
time.sleep(0.8)

if loaded:
    lcd_str(lcd, "Loaded Last Settings")
else:
    lcd_str(lcd, "Didn't load last settings")
time.sleep(0.5)

counter = 0
Bad_Frame_Counter = 0
updateLcd = 1
Last_Temperature = -999
t_last = time.monotonic_ns()
t_conn = time.monotonic_ns()
t_frame = time.monotonic_ns()
t_lcd = time.monotonic_ns()
while True:
    
    # time variables
    t_curr = time.monotonic_ns()
    t_delta = t_curr - t_last
    frame_duration = t_curr - t_frame
    
    if t_delta > 5e8 and conn:  # 5 sec
        try: # I think this throws socket.timeout error
            mqtt_client.loop(timeout=0.01) # polling for commands
            mqtt_client.publish('pico/feeds/state', json.dumps({"temp" :Actual_Temperature, "curr":Control_Signal_Amps, "state":defaultSettings }))
            conn = True
            ethi = True
            t_conn = t_curr
        except MQTT.MMQTTException: # broker offline
            conn = False
            ethi = True
            t_conn = t_curr
        except AssertionError: # no cable
            conn = False
            ethi = False
            t_conn = t_curr
            
        t_last = t_curr
        
    # retries connection every 30s, can take a very long time
    if t_curr - t_conn > 300e8 and not conn: # 30s
        try:
            mqtt_client.connect(clean_session=False)
            time.sleep(0.01)
            mqtt_client.subscribe("server/feeds/commands", qos=1)
            time.sleep(0.01)
            conn = True
            ethi = True
            t_conn = t_curr
        except RuntimeError: # broker offline
            conn = False
            ethi = True
            t_conn = t_curr
        except AssertionError: # no cable
            conn = False
            ethi = False
            t_conn = t_curr
            
    if frame_duration >= defaultSettings['period']:
        # read inputs:
        Supply_Current_Voltage = curr_adc.voltage
        actResVolt = therm_adc.voltage

        # Get current state
        #Actual_Resistance = defaultSettings['maxRes'] * actResVolt / defaultSettings['maxResVolt']
        #if (Actual_Resistance == defaultSettings['thermR25']):
        #    Actual_Temperature = 25
        #elif ((Actual_Resistance <= 0) or (Actual_Resistance > defaultSettings['maxRes'])):
        #    Actual_Temperature = 0
        #else:
        #    Actual_Temperature = Kohm_to_Celsius(Actual_Resistance)
        
        # for lm335 in the little box
        Actual_Temperature = actResVolt * 100

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
            Control_Signal_Amps = defaultSettings['setCurrent']
        else: # PID stuff goes here
            P_Signal = defaultSettings['Kc'] * Error_Signal
            I_Signal += (defaultSettings['Kc'] / defaultSettings['Ti']) * Error_Signal * frame_duration
            
            # Integral clamping/anti-windup
            if I_Signal > defaultSettings['I_max']:
                I_Signal = defaultSettings['I_max']
            elif I_Signal < -1*defaultSettings['I_max']:
                I_Signal = -1*defaultSettings['I_max']
            
            if not (Last_Temperature > -998):
                D_Signal = -(defaultSettings['Kc'] * defaultSettings['Td']) * (Actual_Temperature - Last_Temperature) / frame_duration
            else:
                D_Signal = 0

            Control_Signal_Watts = P_Signal + I_Signal + D_Signal
            if (Control_Signal_Watts < 0):
                Control_Signal_Watts = 0

            Control_Signal_Amps = math.sqrt(Control_Signal_Watts / defaultSettings['loadResist'])
            Raw_amps = Control_Signal_Amps

            if (Control_Signal_Amps > defaultSettings['maxCurr']):
                Control_Signal_Amps = defaultSettings['maxCurr']
            if (Control_Signal_Amps > defaultSettings['maxSuppCurr']):
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
                lcd_str(lcd, "Current Error!  Output disabled.")
                updateLcd = 0
                dac.value = 0
                Control_Signal_Amps = 0

        # if the current signal is activated, and the temperature is within
        # range such that we are allowed to apply a current, then output the
        # current signal to the DAC
        if ((Actual_Temperature > defaultSettings['maxTemp']) or ( not defaultSettings['outputToggle'])):
           dac.value = 0
           Control_Signal_Amps = 0
        else:
            vout = defaultSettings['maxSuppCurrVolt'] * Control_Signal_Amps / defaultSettings['maxSuppCurr']
            raw_out = (vout * 65535 / 5)
            if raw_out > 65535: raw_out = 65535
            if raw_out < 0: raw_out = 0
            dac.value = math.floor(raw_out)
            time.sleep(1./1000.)


        # update LCD
        if t_curr - t_lcd > 2.5e8 and updateLcd: #update once per second
            space = ''.join([" " for i in range(3)])
            tog = 1 if defaultSettings['outputToggle'] else 0
            #lcd_str(lcd, f"Temp: {actResVolt} {tog}Curr: {Supply_Current_Voltage:05.2f}")
            #lcd_str(lcd, f"Temp: {Actual_Temperature:06.2f}{space}{tog}Curr: {Control_Signal_Amps:05.2f}")
            lcd_str(lcd, f"Temp: {Actual_Temperature:06.2f}{space}{tog}Raw{Raw_amps:5.2f} I{I_Signal:5.2f}")
            if not conn and not ethi :
                lcd_str(lcd, "   NC", clear=False) # no connection / no cable
            elif not conn and ethi:
                lcd_str(lcd, "   NB", clear=False) # no broker
                
            t_lcd = t_curr
            led.value = not led.value

        
        Last_Temperature = Actual_Temperature
        t_frame = time.monotonic_ns()
        


    #time.sleep(0.01)









