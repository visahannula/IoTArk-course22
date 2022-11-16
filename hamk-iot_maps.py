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

import json
import os  # for env
import sys
from datetime import datetime, timezone
from math import cos, radians
from time import sleep

import paho.mqtt.client as mqtt

MQTT_BROKER = os.environ.get('MQTT_BROKER')
MQTT_TOPIC = 'hamk/iot-python-client' # will be appended with sensor name

if not MQTT_BROKER:
    MQTT_BROKER='localhost' # fallback to localhost
    print(f'Broker hostname not defined, using {MQTT_BROKER}')

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


# Model a sensor (naive)
# returns position as a value based on "speed" and time spent
class Sensor:
    def __init__(self, name: str, speed_lat=1, speed_lon=1, icon=":star:"):
        self.name = name
        self.last_update_time = None
        self.lat = None # latitude coordinate as degrees.decimals
        self.lon = None # longitude coordinate as degrees.decimals
        self.speed_lat = speed_lat # meters per second
        self.speed_lon = speed_lon
        self.icon = icon

    def start(self):
        self.last_update_time = datetime.now(tz=timezone.utc)
        print(f"Started sensor: {self.name}, {self.last_update_time}")

    def get_name(self, short=False):
        return self.name if not short else self.name.replace(" ", "_")

    def set_position(self, lat: float, lon: float):
        if lat > 90: # Edge of the world!
            lat = 90
        elif lat < -90:
            lat = -90

        if lon > 180:
            lon = -180
        elif lon < -180:
            lon = 180
        
        self.lat = lat
        self.lon = lon

    def get_position(self):
        timedifference = datetime.now(tz=timezone.utc) - self.last_update_time
        timedifference_seconds = timedifference.total_seconds()

        #print(f'Current timediff: {timedifference_seconds}')

        lat = self.lat + ((timedifference_seconds * self.speed_lat)/111111)
        lon = self.lon + ((timedifference_seconds * self.speed_lon)/(111111 * cos(radians(self.lat))))

        self.set_position(lat, lon)
        self.last_update_time = datetime.now(tz=timezone.utc)

        return {
            "lat": self.lat,
            "lon": self.lon
        }
    
    # return dict representation of obj
    def get_dict(self):
        dict_obj = {
            "name": self.name,
            "running": True if not self.last_update_time == None else False,
            "icon": self.icon
        }
        dict_obj.update(self.get_position())
        
        return dict_obj


# Class to hold the sensors and mqtt clients
class SensorMQTTClient:
    def __init__(self, sensor: Sensor, mqtt_client: mqtt.Client):
        self.sensor = sensor
        self.mqtt_client = mqtt_client


# MQTT callbacks
def pub_to_broker(mqttc, obj, flags, reasonCode):
    print(f'Connection! {mqttc}, {obj}, {flags}, {rc}')


def on_publish(mqttc, obj, mid):
    print(f'Client with id \"{str(mqttc._client_id, "utf8")}\" published. message id: {str(mid)}')
    pass

def on_connect_fail():
    print("Connection failed!")
    raise
    
def on_disconnect(client, userdata, reasonCode):
    print(f'Client {client.client_id} Disconnected')

# payload always contains the current date
def create_payload(sensor_data: dict):
    d = datetime.now(tz=timezone.utc).isoformat(timespec="seconds")

    payload = {
        "hamk": True,
        "course": "IoTArk",
        "timestamp": d
    }

    payload.update(sensor_data)

    return payload


def main(argv=[]):
    sensor_clients = []

    # initialize sensor clients and connect (could use some threading here?)
    for sensor in sensors:
        s = Sensor(sensor["name"])
        s.set_position(sensor["initial_lat"], sensor["initial_lon"])
        s.speed_lat = sensor["speed_up"]
        s.speed_lon = sensor["speed_left"]
        s.icon = sensor["icon"]
    
        mqtt_c = mqtt.Client(f"Client_Study_{s.name}") # name for mqtt
        mqtt_c.on_connect = pub_to_broker
        mqtt_c.on_publish = on_publish
        mqtt_c.on_connect_fail = on_connect_fail
        mqtt_c.on_disconnect = on_disconnect
    
        sensor_clients.append(SensorMQTTClient(s, mqtt_c))

        s.start()
        mqtt_c.connect(host=MQTT_BROKER)

    # publish sensor values to mqtt
    try:
        for reading in range(35):
            for client in sensor_clients:
                payload = json.dumps(create_payload(client.sensor.get_dict()))

                print(f'Publishing. Topic: "{MQTT_TOPIC}/{client.sensor.get_name(short=True)}", Payload: "{payload}"')
                client.mqtt_client.publish(retain=False, topic=f'{MQTT_TOPIC}/{client.sensor.get_name(short=True)}', payload=payload)
                sleep(0.5)
    except KeyboardInterrupt:
        print("OK. Shutting down.")

    for client in sensor_clients:
        if client.mqtt_client.is_connected():
            print(f'Disconnecting.')
            client.mqtt_client.disconnect()

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
