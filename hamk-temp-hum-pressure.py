#!/usr/bin/env python3
# HAMK, IoT Ark Excercise MQTT Client with python for 
# Node RED + Dashboard
# This is a simple MQTT client publishing some bogus values
# for temperature, humidity and atmospheric pressure. Uses Paho MQTT.
#
# Set environment var MQTT_BROKER as broker hostname or ip
#
# By: Visa Hannula

import sys
import os # for env
import json
from datetime import datetime, timezone
from time import sleep

import paho.mqtt.client as mqtt

MQTT_BROKER = os.environ.get('MQTT_BROKER')
MQTT_TOPIC = 'hamk/iot-python-client'

if not MQTT_BROKER:
    MQTT_BROKER='localhost'
    print(f'Broker hostname not defined, using {MQTT_BROKER}')


def pub_to_broker(mqttc, obj, flags, rc):
    print(f'Connection! {mqttc}, {obj}, {flags}, {rc}')


def on_publish(mqttc, obj, mid):
    print(f'Client with id \"{str(mqttc._client_id, "utf8")}\" published. mid: {str(mid)}')
    pass


def on_connect_fail():
    print("Connection failed!")
    sys.exit(1)

# payload always contains the current date
def create_payload(temperature, humidity, pressure):
    d = datetime.now(tz=timezone.utc).isoformat(timespec="seconds")

    return {
        "hamk": True,
        "course": "IoTArk",
        "assignment_num": 3,
        "temperature": f'{temperature:.1f}',
        "humidity": int(humidity),
        "pressure": int(pressure),
        "timestamp": d
    }


def sensor_values(limit):
    x = 0
    y = 1

    while x < limit:
        print(f'NOW RETURNING: {x+(y*x)}')
        yield x+(y*x) if x+(y*x) != 0 else 1
        x += 1
        y += 2


def main(argv=[]):
    mqtt_client = mqtt.Client("Client_for_Study")
    mqtt_client.on_connect = pub_to_broker
    mqtt_client.on_publish = on_publish
    mqtt_client.on_connect_fail = on_connect_fail
    
    mqtt_client.connect(host=MQTT_BROKER)

    for reading in sensor_values(10):
        payload = json.dumps(
            create_payload(
                temperature=15+(10/reading), humidity=55+(reading/20), pressure=1040-(0.3*reading)
            )
        )

        print(f'Publishing. Topic: "{MQTT_TOPIC}", Payload: "{payload}"')
        mqtt_client.publish(retain=False, topic=MQTT_TOPIC, payload=payload)
        sleep(2)


    if mqtt_client.is_connected():
        print(f'Disconnecting.')
        mqtt_client.disconnect()

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
