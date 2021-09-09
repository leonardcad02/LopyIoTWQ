import time
from machine import I2C
import atlasi2c

i2c = I2C(0, I2C.MASTER, baudrate=100000)
ph_sensor = atlasi2c.ATLASI2C(i2c, addr=99)
do_sensor = atlasi2c.ATLASI2C(i2c, addr=97)
ec_sensor = atlasi2c.ATLASI2C(i2c, addr=100)

while(True):
    ph_sensor.write('R')
    time.sleep(1)
    data = ph_sensor.read()
    print(data)
    do_sensor.write('R')
    time.sleep(1)
    data = do_sensor.read()
    print(data)
    ec_sensor.write('R')
    time.sleep(1)
    data = ec_sensor.read()
    print(data)
    #ph_sensor.write('Sleep')
    time.sleep(10)