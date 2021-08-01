from machine import ADC
from machine import Pin
from project import mqtt_connect, mqtt_publish
import time
import pycom

# create an analog pin for Photoresistor Module (photoresistance + 10 kohm resistor)
LightSensorPin = 'P16'     # sensor signal connected to P16
lightPin = Pin(LightSensorPin, mode=Pin.IN)     # set up pin mode to input
adc = ADC(bits=10)      # create an ADC object bits=10 means range 0-1024 the lower value the less light detected
apin = adc.channel(attn=ADC.ATTN_11DB, pin=LightSensorPin)     # create an analog pin on P16;  attn=ADC.ATTN_11DB measures voltage from 0.1 to 3.3v

# Create the binary input pin for Line Follow Sensor Module
line_follow_input = Pin('P14', mode=Pin.IN)     # set up pin mode to input

# creat the MQTT client 
client = mqtt_connect()

# initialize the door open state as "False", closed.
door_open = False

# an unstopping loop
while True:

   # get light sensor values and publish through MQTT
   light_val = apin()
   mqtt_publish(client, "home-assistant/Light", light_val)

   # get line follow sensor value (0: closed, 1: open) and publish through MQTT
   line_follow_value = line_follow_input.value()
   if str(line_follow_value) == '1':
      mqtt_publish(client, "home-assistant/Door", "Open")
   else:
      mqtt_publish(client, "home-assistant/Door", "Closed")

   if str(line_follow_value) == '1' and int(light_val) > 800:
      # if the door is opened in a very low light situation (int(light_val) > 800, hard to see anything in the room) 
      door_open = True     # change the door state to open, which only happen in the low light situation
      pycom.heartbeat(False)     # stop heartbeat signal of LED
      pycom.rgbled(int('0xffffff'))    # light on the LED with white light

   elif door_open == True and int(light_val) > 700:
      # if detect the door is closed in the low light situation
      if str(line_follow_value) == '0':
         door_open = False    # change the door state to closed
         time.sleep(10)    # keep the light for another 10 seconds
         pycom.heartbeat(True)      # return heartbeat signal of LED

   elif door_open == True and int(light_val) < 700:
      # other cases, like forget to close the door in the night, but it's going to be brighter
      door_open = False
      pycom.heartbeat(True)

   time.sleep(1)     # check every one second