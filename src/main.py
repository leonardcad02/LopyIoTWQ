from network import LoRa
from network import WLAN
from network import Bluetooth
from machine import I2C
from machine import ADC
from deepsleep import DeepSleep
import pycom
import socket
import binascii
import struct
import time
import atlasi2c
freq = 917600000

# LED Colors
off = 0x000000
red = 0xff0000
green = 0x00ff00
blue = 0x0000ff

# Turn off radios
wlan = WLAN()
bluetooth = Bluetooth()
#wlan.deinit() #disables WiFi radio
bluetooth.deinit() #disables bluetooth radio
# Turn off hearbeat LED
pycom.heartbeat(False)

# Creates a DeepSleep object (Deep Sleep Shield must be connected)
ds = DeepSleep()

# Initialize I2C sensors
i2c = I2C(0, I2C.MASTER, baudrate=100000)
ph_sensor = atlasi2c.ATLASI2C(i2c, addr=99)
do_sensor = atlasi2c.ATLASI2C(i2c, addr=97)
ec_sensor = atlasi2c.ATLASI2C(i2c, addr=100)

# Initilize ADC for battery voltage estimation
adc = ADC()
batt = adc.channel(attn=ADC.ATTN_2_5DB, pin='P16')

# get if restore the LoRaWAN state
loraSaved = pycom.nvs_get('loraSaved')
print(loraSaved)

if not loraSaved:
    # Initialize LoRa in LORAWAN mode.
    lora = LoRa(mode=LoRa.LORAWAN)

    #Setup the single channel for connection to the gateway 
    for channel in range(0, 72): 
        lora.remove_channel(channel) 
    for chan in range(0, 8): 
        lora.add_channel(chan,  frequency=freq,  dr_min=0,  dr_max=3) 

    # create an ABP authentication params
    dev_addr = struct.unpack(">l", binascii.unhexlify('2602199C'))[0]
    nwk_swkey = binascii.unhexlify('041C875AA7CC56BEAFC34E68E4F9991A')
    app_swkey = binascii.unhexlify('7C44521EFEA59716094339FD49E4FFC5')

    # join a network using ABP (Activation By Personalization)
    lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

    while not lora.has_joined():
        time.sleep(2)
        print('Not yet joined...')
        pycom.rgbled(red)
        
    if(lora.has_joined()):
        print("First Joined!")

    # create a LoRa socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

    # set the LoRaWAN data rate
    #   US Data Rates Max Payload (bytes)
    #   DR0 (SF10 BW125): 11
    #   DR1 (SF9 BW125): 53
    #   DR2 (SF8 BW125): 129
    #   DR3 (SF7 BW125): 242
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 1)

    #select the port number
    s.bind(3)
    # make the socket blocking
    # (waits for the data to be sent and for the 2 receive windows to expire)
    s.setblocking(True)

    payload = bytearray(16)
    # query sensors
    ph_sensor.write('R')
    time.sleep(1)
    data1 = ph_sensor.read()
    print(data1)
    do_sensor.write('R')
    time.sleep(1)
    data2 = do_sensor.read()
    print(data2)
    ec_sensor.write('R')
    time.sleep(1)
    data3 = ec_sensor.read()
    print(data3)
    #ph_sensor.write('Sleep')
    #Cayenne LPP
    payload[0] = 0x01 # channel 1
    payload[1] = 2 # Analog Input, .01 Signed
    ph = int(data1 * 100) #ph sensor
    payload[2] = ph >> 8
    payload[3] = ph
    payload[4] = 0x02 # channel 2
    payload[5] = 2 # Analog Input, .01 Signed
    do = int(data2 * 100) #dissolved oxygen sensor
    payload[6] = do >> 8
    payload[7] = do
    payload[8] = 0x03 # channel 3
    payload[9] = 2 # Analog Input, .01 Signed
    ec = int(data3 * 100) # conductivity sensor
    payload[10] = ec >> 8
    payload[11] = ec
    payload[12] = 0x04 # channel 4
    payload[13] = 2 # Analog Input, .01 Signed
    battery = int(batt.value() / 10) #battery voltage
    payload[14] = battery >> 8
    payload[15] = battery
    #print(payload)
    s.send(payload)
    # make the socket non-blocking
    # (because if there's no data received it will block forever...)
    #s.setblocking(False)
    pycom.rgbled(green)
    time.sleep(0.1)
    pycom.rgbled(off)
    print('Send data')
    time.sleep(2)
    lora.nvram_save() #Save the LoRaWAN state
    pycom.nvs_set('loraSaved', 1)
    ds.go_to_sleep(58)  # go to sleep for 60 seconds
else:
    # Initialize LoRa in LORAWAN mode.
    lora = LoRa(mode=LoRa.LORAWAN)

    lora.nvram_restore() # Restore the LoRaWAN state

    #Setup the single channel for connection to the gateway 
    for channel in range(0, 72): 
        lora.remove_channel(channel) 
    for chan in range(0, 8): 
        lora.add_channel(chan,  frequency=freq,  dr_min=0,  dr_max=3) 
        
    if(lora.has_joined()):
        print("Joined!")

    # create a LoRa socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

    # set the LoRaWAN data rate
    #   US Data Rates Max Payload (bytes)
    #   DR0 (SF10 BW125): 11
    #   DR1 (SF9 BW125): 53
    #   DR2 (SF8 BW125): 129
    #   DR3 (SF7 BW125): 242
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 1)

    #select the port number
    s.bind(3)
    # make the socket blocking
    # (waits for the data to be sent and for the 2 receive windows to expire)
    s.setblocking(True)

    payload = bytearray(16)
    # query sensors
    ph_sensor.write('R')
    time.sleep(1)
    data1 = ph_sensor.read()
    print(data1)
    do_sensor.write('R')
    time.sleep(1)
    data2 = do_sensor.read()
    print(data2)
    ec_sensor.write('R')
    time.sleep(1)
    data3 = ec_sensor.read()
    print(data3)
    #ph_sensor.write('Sleep')
    #Cayenne LPP
    payload[0] = 0x01 # channel 1
    payload[1] = 2 # Analog Input, .01 Signed
    ph = int(data1 * 100) #ph sensor
    payload[2] = ph >> 8
    payload[3] = ph
    payload[4] = 0x02 # channel 2
    payload[5] = 2 # Analog Input, .01 Signed
    do = int(data2 * 100) #dissolved oxygen sensor
    payload[6] = do >> 8
    payload[7] = do
    payload[8] = 0x03 # channel 3
    payload[9] = 2 # Analog Input, .01 Signed
    ec = int(data3 * 100) # conductivity sensor
    payload[10] = ec >> 8
    payload[11] = ec
    payload[12] = 0x04 # channel 4
    payload[13] = 2 # Analog Input, .01 Signed
    battery = int(batt.value() / 10) #battery voltage
    payload[14] = battery >> 8
    payload[15] = battery
    #print(payload)
    s.send(payload)
    # make the socket non-blocking
    # (because if there's no data received it will block forever...)
    #s.setblocking(False)
    pycom.rgbled(green)
    time.sleep(0.1)
    pycom.rgbled(off)
    print('Send data')
    time.sleep(2)
    lora.nvram_save() #Save the LoRaWAN state
    #pycom.nvs_set('loraSaved', 0)
    ds.go_to_sleep(58)  # go to sleep for 60 seconds