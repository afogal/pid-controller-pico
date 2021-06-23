EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L New_Library:Pico U?
U 1 1 60D3B9DA
P 6800 1950
F 0 "U?" H 6800 3165 50  0000 C CNN
F 1 "Pico" H 6800 3074 50  0000 C CNN
F 2 "RPi_Pico:RPi_Pico_SMD_TH" V 6800 1950 50  0001 C CNN
F 3 "" H 6800 1950 50  0001 C CNN
	1    6800 1950
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_Coaxial_x2_Isolated J?
U 1 1 60D4852C
P 8300 1000
F 0 "J?" H 8400 975 50  0000 L CNN
F 1 "CurrOut_BNC" H 8400 884 50  0000 L CNN
F 2 "" H 8300 1000 50  0001 C CNN
F 3 " ~" H 8300 1000 50  0001 C CNN
	1    8300 1000
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_Coaxial_x2_Isolated J?
U 1 1 60D49DE5
P 9100 1000
F 0 "J?" H 9200 975 50  0000 L CNN
F 1 "CurrIn_BNC" H 9200 884 50  0000 L CNN
F 2 "" H 9100 1000 50  0001 C CNN
F 3 " ~" H 9100 1000 50  0001 C CNN
	1    9100 1000
	1    0    0    -1  
$EndComp
$Comp
L New_Library:SparkFun_MCP4725 U?
U 1 1 60D4F4A6
P 6300 4000
F 0 "U?" V 6446 3938 50  0000 L CNN
F 1 "SparkFun_MCP4725" V 6537 3938 50  0000 L CNN
F 2 "" H 6600 3150 50  0001 C CNN
F 3 "" H 6600 3150 50  0001 C CNN
	1    6300 4000
	0    1    1    0   
$EndComp
$Comp
L New_Library:Ada_ADS1115 U?
U 1 1 60D51AE3
P 7700 4000
F 0 "U?" V 7571 4538 50  0000 L CNN
F 1 "Ada_ADS1115" V 7662 4538 50  0000 L CNN
F 2 "" H 7650 3350 50  0001 C CNN
F 3 "" H 7650 3350 50  0001 C CNN
	1    7700 4000
	0    1    1    0   
$EndComp
$Comp
L New_Library:QWIIK_Adapter U?
U 1 1 60D537CB
P 9500 2850
F 0 "U?" H 9392 2485 50  0000 C CNN
F 1 "QWIIK_Adapter" H 9392 2576 50  0000 C CNN
F 2 "" H 9300 3100 50  0001 C CNN
F 3 "" H 9300 3100 50  0001 C CNN
	1    9500 2850
	1    0    0    1   
$EndComp
$Comp
L New_Library:Wiz820IO U?
U 1 1 60D555AF
P 4950 1250
F 0 "U?" H 4975 1725 50  0000 C CNN
F 1 "Wiz820IO" H 4975 1634 50  0000 C CNN
F 2 "" H 4950 1600 50  0001 C CNN
F 3 "" H 4950 1600 50  0001 C CNN
	1    4950 1250
	1    0    0    -1  
$EndComp
Text GLabel 5500 1000 2    50   Input ~ 0
GND
Wire Wire Line
	5350 1000 5500 1000
Text GLabel 5500 1100 2    50   Input ~ 0
3V3
Wire Wire Line
	5350 1100 5500 1100
Text GLabel 5500 1400 2    50   Input ~ 0
GP15
Text GLabel 5500 1500 2    50   Input ~ 0
GP12
Text GLabel 5900 2900 0    50   Input ~ 0
nReset
Text GLabel 5900 2500 0    50   Input ~ 0
MISO
Wire Wire Line
	5900 2500 6100 2500
Wire Wire Line
	5350 1500 5500 1500
Wire Wire Line
	5350 1400 5500 1400
NoConn ~ 5350 1300
NoConn ~ 5350 1200
NoConn ~ 4600 1500
NoConn ~ 4600 1000
NoConn ~ 4600 1100
Text GLabel 4350 1200 0    50   Input ~ 0
GP11
Text GLabel 5900 2400 0    50   Input ~ 0
MOSI
Text GLabel 4350 1300 0    50   Input ~ 0
GP10
Text GLabel 5900 2300 0    50   Input ~ 0
SCLK
Text GLabel 5900 2600 0    50   Input ~ 0
nSS
Wire Wire Line
	5900 2900 6100 2900
Wire Wire Line
	6100 2600 5900 2600
Wire Wire Line
	6100 2400 5900 2400
Wire Wire Line
	6100 2300 5900 2300
Wire Wire Line
	4350 1200 4600 1200
Wire Wire Line
	4350 1300 4600 1300
Text GLabel 4350 1400 0    50   Input ~ 0
GP13
Wire Wire Line
	4350 1400 4600 1400
Text GLabel 6050 3500 1    50   Input ~ 0
GND
Text GLabel 6150 3500 1    50   Input ~ 0
5V
Text GLabel 6250 3500 1    50   Input ~ 0
SDA
Text GLabel 6350 3500 1    50   Input ~ 0
SCL
Text GLabel 6450 3500 1    50   Input ~ 0
GND
Text GLabel 6550 3500 1    50   Input ~ 0
BNC1
Wire Wire Line
	6050 3500 6050 3600
Wire Wire Line
	6150 3500 6150 3600
Wire Wire Line
	6250 3500 6250 3600
Wire Wire Line
	6350 3500 6350 3600
Wire Wire Line
	6450 3500 6450 3600
Wire Wire Line
	6550 3500 6550 3600
Text GLabel 8100 1300 3    50   Input ~ 0
DAC_OUT
Wire Wire Line
	8100 1000 8100 1300
Text GLabel 8300 1300 3    50   Input ~ 0
GND
Text GLabel 9100 1300 3    50   Input ~ 0
GND
Text GLabel 9950 1300 3    50   Input ~ 0
GND
Wire Wire Line
	9100 1300 9100 1200
Wire Wire Line
	9950 1300 9950 1200
Text GLabel 7250 3500 1    50   Input ~ 0
BNC2
Text GLabel 7550 3500 1    50   Input ~ 0
BNC3
Text GLabel 7750 3500 1    50   Input ~ 0
GND
NoConn ~ 7350 3600
NoConn ~ 7450 3600
NoConn ~ 7650 3600
Text GLabel 7850 3500 1    50   Input ~ 0
SDA
Text GLabel 7950 3500 1    50   Input ~ 0
SCL
Text GLabel 8050 3500 1    50   Input ~ 0
GND
Text GLabel 8150 3500 1    50   Input ~ 0
5V
Wire Wire Line
	7250 3500 7250 3600
Wire Wire Line
	7550 3500 7550 3600
Wire Wire Line
	7750 3500 7750 3600
Wire Wire Line
	7850 3500 7850 3600
Wire Wire Line
	7950 3500 7950 3600
Wire Wire Line
	8050 3500 8050 3600
Wire Wire Line
	8150 3500 8150 3600
Wire Wire Line
	8300 1300 8300 1200
Text GLabel 7700 2300 2    50   Input ~ 0
SCL
Text GLabel 7700 2400 2    50   Input ~ 0
SDA
Wire Wire Line
	7700 2300 7500 2300
Wire Wire Line
	7700 2400 7500 2400
Text GLabel 7700 1400 2    50   Input ~ 0
3V3
Text GLabel 7700 1000 2    50   Input ~ 0
5V
Text GLabel 7700 1200 2    50   Input ~ 0
GND
Wire Wire Line
	7500 1000 7700 1000
Wire Wire Line
	7500 1200 7700 1200
Wire Wire Line
	7500 1400 7700 1400
Text GLabel 8900 1300 3    50   Input ~ 0
ADC_A3
Text GLabel 9750 1300 3    50   Input ~ 0
ADC_A0
Wire Wire Line
	8900 1000 8900 1300
Wire Wire Line
	9750 1000 9750 1300
$Comp
L Connector:Conn_Coaxial_x2_Isolated J?
U 1 1 60D4A901
P 9950 1000
F 0 "J?" H 10050 975 50  0000 L CNN
F 1 "ThermIn_BNC" H 10050 884 50  0000 L CNN
F 2 "" H 9950 1000 50  0001 C CNN
F 3 " ~" H 9950 1000 50  0001 C CNN
	1    9950 1000
	1    0    0    -1  
$EndComp
Text GLabel 9050 2700 0    50   Input ~ 0
GND
Text GLabel 9050 2800 0    50   Input ~ 0
3V3
Text GLabel 9050 2900 0    50   Input ~ 0
SDA
Text GLabel 9050 3000 0    50   Input ~ 0
SCL
Wire Wire Line
	9050 2700 9200 2700
Wire Wire Line
	9050 2800 9200 2800
Wire Wire Line
	9050 2900 9200 2900
Wire Wire Line
	9050 3000 9200 3000
$EndSCHEMATC
