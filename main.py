import config
import machine
from machine import Pin, SoftI2C
import network
import os
import ssd1306
import time

wlan = network.WLAN(network.STA_IF) # create station interface
if wlan.isconnected() != True:
    wlan.active(False)
    wlan.active(True)       # activate the interface
    wlan.config(txpower=8.5)  #set to 8.5dBm
    wlan.isconnected()      # check if the station is connected to an AP
    time.sleep_ms(500)
    if not wlan.isconnected():
      print('connecting to network...')
      wlan.connect(config.WIFI_SSID, config.WIFI_PASSWD) # connect to an AP
      time.sleep_ms(500)
      while not wlan.isconnected():
        pass
print('network config:', wlan.ifconfig())

oled_width = 128
oled_height = 64
# OLED reset pin
i2c_rst = Pin(16, Pin.OUT)
# Initialize the OLED display
i2c_rst.value(0)
time.sleep_ms(5)
i2c_rst.value(1) # must be held high after initialization
# Setup the I2C lines
i2c_scl = Pin(15, Pin.OUT, Pin.PULL_UP)
i2c_sda = Pin(4, Pin.OUT, Pin.PULL_UP)
# Create the bus object
i2c = SoftI2C(scl=i2c_scl, sda=i2c_sda)
# Create the display object
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
oled.fill(0)
oled.text(wlan.ifconfig()[0], 0, 0)
oled.text('HELLO WiFi ESP32', 0, 25)
oled.text('Version 1.0.0', 0, 55)
  
#oled.line(0, 0, 50, 25, 1)
oled.show()
