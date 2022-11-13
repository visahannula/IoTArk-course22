#!/usr/bin/env python3
# HAMK, IoT Ark Excercise MQTT Client with Python for 
# Node RED + Maps
# This is a simple MQTT client publishing some bogus values
# to simulate for the excercise.
# Uses Paho MQTT.
#
# Set environment var MQTT_BROKER as broker hostname or ip
#
# By: Visa Hannula

import sys
import os # for env
import json
from datetime import datetime, timezone, timedelta
from time import sleep
from math import cos, radians

import paho.mqtt.client as mqtt

MQTT_BROKER = os.environ.get('MQTT_BROKER')
MQTT_TOPIC = 'hamk/iot-python-client' # will be appended with sensor name

if not MQTT_BROKER:
    MQTT_BROKER='localhost'
    print(f'Broker hostname not defined, using {MQTT_BROKER}')


class Sensor:
    def __init__(self, name, speed_up=1, speed_left=1, icon=":star"):
        self.name = name
        self.last_time = None
        self.lat = None # latitude coordinate as degrees.decimals
        self.lon = None # longitude coordinate as degrees.decimals
        self.speed_up = speed_up # meters per second
        self.speed_left = speed_left
        self.icon = icon

    def start(self):
        self.last_time = datetime.now(tz=timezone.utc)
        print(f"Started sensor: {self.name}, {self.last_time}")

    def set_position(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def get_position(self):
        timedifference = datetime.now(tz=timezone.utc) - self.last_time
        timedifference_seconds = timedifference.total_seconds()

        print(f'Current timediff: {timedifference_seconds}')

        lat = self.lat + ((timedifference_seconds * self.speed_up)/111111)
        lon = self.lon + ((timedifference_seconds * self.speed_left)/(111111 * cos(radians(self.lat))))

        self.set_position(lat, lon)
        self.last_time = datetime.now(tz=timezone.utc)

        return {
            "lat": self.lat,
            "lon": self.lon
        }
        
    def get_dict(self):
        dict_obj = {
            "name": self.name,
            "running": True if not self.last_time == None else False,
            "icon": self.icon
        }
        dict_obj.update(self.get_position())
        
        return dict_obj


def pub_to_broker(mqttc, obj, flags, rc):
    print(f'Connection! {mqttc}, {obj}, {flags}, {rc}')


def on_publish(mqttc, obj, mid):
    print(f'Client with id \"{str(mqttc._client_id, "utf8")}\" published. mid: {str(mid)}')
    pass


def on_connect_fail():
    print("Connection failed!")
    sys.exit(1)

# payload always contains the current date
def create_payload(sensor_data):
    d = datetime.now(tz=timezone.utc).isoformat(timespec="seconds")

    payload = {
        "hamk": True,
        "course": "IoTArk",
        "timestamp": d
    }

    payload.update(sensor_data)

    print(f'Intermediate {payload}')

    return payload



def main(argv=[]):
    mqtt_client = mqtt.Client("Client_for_Study")
    mqtt_client.on_connect = pub_to_broker
    mqtt_client.on_publish = on_publish
    mqtt_client.on_connect_fail = on_connect_fail
    
    mqtt_client.connect(host=MQTT_BROKER)

    sensors = [
        {
            "name": "Santa Claus",
            "initial_lat": 66.54328556230257, # Santa village
            "initial_lon": 25.845727069829188,
            "speed_up": 1.2,
            "speed_left": 1.5,
            "icon": ":santa:",
            "obj": None
        },
        {
            "name": "Aeroplane 774",
            "initial_lat": 66.5547424073456, 
            "initial_lon": 25.81127964455749,
            "speed_up": 75,
            "speed_left": 57,
            "icon": ":airplane:",
            "obj": None
        },
        {
            "name": "Heli Aslak",
            "initial_lat": 66.54085588672697,
            "initial_lon": 25.866901092402323,
            "speed_up": 55,
            "speed_left": -57,
            "icon": "helicopter",
            "obj": None
        },
        {
            "name": "Reindeer 1.",
            "initial_lat": 66.54655132697363,
            "initial_lon": 25.84243694805249,
            "speed_up": 2,
            "speed_left": 4,
            "icon": ":deer:",
            "obj": None
        },
        {
            "name": "Reindeer 2.",
            "initial_lat": 66.54749582714075, 
            "initial_lon": 25.843993522504604,
            "speed_up": 2,
            "speed_left": -4,
            "icon": ":deer:",
            "obj": None
        }
    ]

    # initialize sensors
    for sensor in sensors:
        sensor["obj"] = Sensor(sensor["name"])
        sensor["obj"].set_position(sensor["initial_lat"], sensor["initial_lon"])
        sensor["obj"].speed_up = sensor["speed_up"]
        sensor["obj"].speed_left = sensor["speed_left"]
        sensor["obj"].icon = sensor["icon"]
        sensor["obj"].start()

    for reading in range(35):
        for sensor in sensors:
            sen_obj = sensor.get("obj")
            payload = json.dumps(create_payload(sen_obj.get_dict()))

            print(f'Publishing. Topic: "{MQTT_TOPIC}/{sen_obj.name.replace(" ", "_")}", Payload: "{payload}"')
            mqtt_client.publish(retain=False, topic=f'{MQTT_TOPIC}/{sen_obj.name.replace(" ", "_")}', payload=payload)
            sleep(0.5)

    if mqtt_client.is_connected():
        print(f'Disconnecting.')
        mqtt_client.disconnect()

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
