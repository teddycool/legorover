__author__ = 'psk'
#http://blog.bitify.co.uk/2013/11/connecting-and-calibrating-hmc5883l.html
#!/usr/bin/python
import math
import time

import smbus

bus = smbus.SMBus(1)
address = 0x1e


def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def write_byte(adr, value):
    bus.write_byte_data(address, adr, value)

write_byte(0, 0b01110000) # Set to 8 samples @ 15Hz
write_byte(1, 0b00100000) # 1.3 gain LSb / Gauss 1090 (default)
write_byte(2, 0b00000000) # Continuous sampling

scale = 0.92

x_out = read_word_2c(3) * scale
y_out = read_word_2c(7) * scale
z_out = read_word_2c(5) * scale

bearing  = math.atan2(y_out, x_out)
if (bearing < 0):
    bearing += 2 * math.pi

print "Bearing: ", math.degrees(bearing)
print "x, y, z -out", x_out, y_out, z_out

print "Start to rtate the compass horizontally"

time.sleep(2)

print "Starts measuring..."
minx = 0
maxx = 0
miny = 0
maxy = 0
#Drive in a circle and read the compass
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
from MotorControl import MotorControlL298

mc = MotorControlL298.MotorControlL298(GPIO)
mc.rightTurn()
mc.update()

for i in range(0,100):
    x_out = read_word_2c(3)
    y_out = read_word_2c(7)
    z_out = read_word_2c(5)


    if x_out < minx:
        minx=x_out

    if y_out < miny:
        miny=y_out

    if x_out > maxx:
        maxx=x_out

    if y_out > maxy:
        maxy=y_out

    print x_out, y_out, (x_out * scale), (y_out * scale)
    time.sleep(0.1)

print "Done..."
print "minx: ", minx
print "miny: ", miny
print "maxx: ", maxx
print "maxy: ", maxy
print "x offset: ", (maxx + minx) / 2
print "y offset: ", (maxy + miny) / 2
mc.stop()
mc.update()
