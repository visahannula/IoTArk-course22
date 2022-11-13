#!/usr/bin/env python3
# HAMK, IoT Ark Excercise MQTT Client with python for 
# Node RED + Dashboard
# This is a simple MQTT client publishing some bogus values
# for temperature, humidity and atmospheric pressure.
# Uses Paho MQTT.
#
# Set environment var MQTT_BROKER as broker hostname or ip
#
# By: Visa Hannula

import sys
import os # for env
import json
from datetime import datetime as dt

import paho.mqtt.client as mqtt

MQTT_BROKER = os.environ.get('MQTT_BROKER')
MQTT_TOPIC = 'hamk'

if not MQTT_BROKER:
    MQTT_BROKER='localhost'
    print(f'Broker hostname not defined, using {MQTT_BROKER}')


def pub_to_broker(mqttc, obj, flags, rc):
    print(f'Connection! {mqttc}, {obj}, {flags}, {rc}')


def on_publish(mqttc, obj, mid):
    print(f'Client with id \"{str(mqttc._client_id, "utf8")}\" published. mid: {str(mid)}')
    pass

def create_payload():
    d = dt.today().strftime("%d.%m.%Y")

    return {
        "hamk": True,
        "course": "IoTArk",
        "assignment_num": 3,
        "current_date": d
    }

def main(argv=[]):
    print(f'Test {argv[1] if len(argv) > 1 else "no arguments"}')

    mqtt_client = mqtt.Client("Client_for_Study")
    mqtt_client.on_connect = pub_to_broker
    mqtt_client.on_publish = on_publish
    
    mqtt_client.connect(host=MQTT_BROKER, )
    
    payload = json.dumps(create_payload())
    print(f'Publishing. Topic: "{MQTT_TOPIC}", Payload: "{payload}"')
    
    mqtt_client.publish(retain=False, topic=MQTT_TOPIC, payload=payload)

    if mqtt_client.is_connected():
        print(f'Disconnecting.')
        mqtt_client.disconnect()

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
