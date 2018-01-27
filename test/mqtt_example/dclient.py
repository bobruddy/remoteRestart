#!/usr/bin/env python

import argparse
import datetime
import os
import time

import jwt
import paho.mqtt.client as mqtt


# [START iot_mqtt_jwt]
def create_jwt(project_id, private_key_file, algorithm):
    token = {
            # The time that the token was issued at
            'iat': datetime.datetime.utcnow(),
            # The time the token expires.
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            # The audience field should always be set to the GCP project id.
            'aud': project_id
    }

    # Read the private key file.
    with open(private_key_file, 'r') as f:
        private_key = f.read()

    return jwt.encode(token, private_key, algorithm=algorithm)
# [END iot_mqtt_jwt]


# [START iot_mqtt_config]
def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))


def on_connect(unused_client, unused_userdata, unused_flags, rc):
    """Callback for when a device connects."""
    print('on_connect', mqtt.connack_string(rc))


def on_disconnect(unused_client, unused_userdata, rc):
    """Paho callback for when a device disconnects."""
    print('on_disconnect', error_str(rc))


def on_publish(unused_client, unused_userdata, unused_mid):
    """Paho callback when a message is sent to the broker."""
    print('on_publish')


#def on_message(unused_client, unused_userdata, message):
#    """Callback when the device receives a message on a subscription."""
#    payload = str(message.payload)
#    print('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
#            payload, message.topic, str(message.qos)))
def on_message(client, userdata, message):
	print("message received ", str(message.payload.decode("utf-8")))
	print("message topic=", message.topic)
	print("message qos=", message.qos)
	print("message retain flag=", message.retain)
	print("")
    


def get_client(
        project_id, cloud_region, registry_id, device_id, private_key_file,
        algorithm, ca_certs, mqtt_bridge_hostname, mqtt_bridge_port):
    """Create our MQTT client. The client_id is a unique string that identifies
    this device. For Google Cloud IoT Core, it must be in the format below."""
    client = mqtt.Client(
            client_id=('projects/{}/locations/{}/registries/{}/devices/{}'
                       .format(
                               project_id,
                               cloud_region,
                               registry_id,
                               device_id)))

    # With Google Cloud IoT Core, the username field is ignored, and the
    # password field is used to transmit a JWT to authorize the device.
    client.username_pw_set(
            username='unused',
            password=create_jwt(
                    project_id, private_key_file, algorithm))

    # Enable SSL/TLS support.
    client.tls_set(ca_certs=ca_certs)

    # Register message callbacks. https://eclipse.org/paho/clients/python/docs/
    # describes additional callbacks that Paho supports. In this example, the
    # callbacks just print to standard out.
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    # Connect to the Google MQTT bridge.
    client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

    return client


def main():

    mqtt_bridge_port = 8883
    project_id = 'remote-reset'
    mqtt_bridge_hostname = 'mqtt.googleapis.com'
    registry_id = 'remote-reset'
    device_id = 'c123456789'
    private_key_file = 'resources/rsa_private.pem'
    num_messages = 100
    ca_certs = 'roots.pem'
    cloud_region = 'us-central1'
    algorithm = 'RS256'

    #mqtt_topic = 'projects/remote-reset/topics/powerStatus/mytopic'
    mqtt_topic = 'projects/remote-reset/subscriptions/cmytopic'
    #mqtt_topic = '/devices/a123456789/events/mytopic'
    #mqtt_topic = '/devices/c123456789/state'

    client = get_client(
        project_id, cloud_region, registry_id, device_id,
        private_key_file, algorithm, ca_certs,
        mqtt_bridge_hostname, mqtt_bridge_port)

    client.loop_start()

    time.sleep(5)
    client.subscribe(mqtt_topic, qos=1)

    # Publish num_messages mesages to the MQTT bridge once per second.
    for i in range(1, num_messages + 1):

        # Send events every second. State should not be updated as often
        print("Waiting")
        time.sleep(2)

    # End the network loop and finish.
    client.loop_stop()
    print('Finished.')
# [END iot_mqtt_run]


if __name__ == '__main__':
    main()
