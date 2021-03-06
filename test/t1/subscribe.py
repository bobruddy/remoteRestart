#!python3

import paho.mqtt.client as mqtt
import time

#Client(client_id="", clean_session=True, userdata=None, protocol=MQTTv311, transport="tcp")

def on_message(client, userdata, message):
	print("message received ", str(message.payload.decode("utf-8")))
	print("message topic=", message.topic)
	print("message qos=", message.qos)
	print("message retain flag=", message.retain)
	print("")

host = "iot.eclipse.org"
client_name = "mysub"

client = mqtt.Client(client_name)

client.on_message = on_message

client.connect(host)


client.loop_start()
client.subscribe("myhouse/light")

time.sleep(300)

client.loop_stop()
