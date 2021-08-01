from mqtt import MQTTClient


def sub_cb(topic, msg): 
   print(msg)

# connect MQTT broker  
def mqtt_connect():
   client = MQTTClient("core-mosquitto", "192.168.0.142", user="lopy4", password="lopy1234", port=1883)
   client.set_callback(sub_cb) 
   client.connect()

   return client

# publish message
def mqtt_publish(client, topic, message):
   client.subscribe(topic=topic)
   client.publish(topic=topic, msg=(str(message)))