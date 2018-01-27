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


def on_message(unused_client, unused_userdata, message):
    """Callback when the device receives a message on a subscription."""
    payload = str(message.payload)
    print('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
            payload, message.topic, str(message.qos)))

def on_subscribe(unused_client, unused_userdata, unused_mid, granted_qos):
    print('Subscribed: ', granted_qos)
    if granted_qos == 128:
        print('Subscription failed')


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
    client.on_subscribe = on_subscribe

    # Connect to the Google MQTT bridge.
    client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

    return client
# [END iot_mqtt_config]


# [START iot_mqtt_run]
def main():

    mqtt_bridge_port = 8883
    project_id = 'remote-reset'
    mqtt_bridge_hostname = 'mqtt.googleapis.com'
    registry_id = 'remote-reset'
    device_id = 'd123456789'
    private_key_file = 'resources/rsa_private.pem'
    jwt_expires_minutes = 20
    message_type = 'event'
    num_messages = 100
    ca_certs = 'roots.pem'
    cloud_region = 'us-central1'
    algorithm = 'RS256'

    mqtt_topic = '/devices/d123456789/events'
    #mqtt_topic = '/projects/remote-reset/topics/powerStatus'

    client = get_client(
        project_id, cloud_region, registry_id, device_id,
        private_key_file, algorithm, ca_certs,
        mqtt_bridge_hostname, mqtt_bridge_port)

    #mqtt_config_topic = 'devices/d123456789/events'
    mqtt_config_topic = mqtt_topic
    #mqtt_config_topic = 'projects/remote-reset/topics/powerStatus'
    print('loop_start')
    client.loop_start()
    time.sleep(1)

    print('subscribe')
    client.subscribe(mqtt_config_topic, qos=1)
    time.sleep(20)

    print('publish')
    client.publish(mqtt_config_topic, "blah")
    time.sleep(4)

    print('disconnect')
    client.disconnect()
    time.sleep(1)

    print('loop_stop')
    client.loop_stop()
    time.sleep(1)

# [END iot_mqtt_run]


if __name__ == '__main__':
    main()
