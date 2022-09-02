import os
import json
import uuid
import time
import threading
from datetime import datetime
from collections import deque

import pytz
import psycopg2
from pgcopy import CopyManager
from paho.mqtt.client import Client


TABLE = "orm_singledatameasurement"
COLUMNS = ("time", "UUID", "recorded", "data", "measurement_location_id")

DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")

MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID")
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST")
MQTT_BROKER_PORT = os.getenv("MQTT_BROKER_PORT")


def utc_rfc3339_to_datetime(date: str) -> datetime:
    """Convert UTC RFC 3339 datetime string to Python datetime object"""

    return datetime.fromisoformat(date.replace("Z", "")).replace(tzinfo=pytz.UTC)


def on_connect(client, userdata, flags, rc):
    print("Connected to broker with result code " + str(rc))


def on_message(client, buffer, message):
    """Write incoming CCOM messages to database"""

    ccom_entities = json.loads(message.payload)["CCOMData"]["entities"]

    for entity in ccom_entities:
        try:
            # type = entity["@@type"]
            measurement_id = uuid.UUID(entity["UUID"])
            measurement_location_id = uuid.UUID(entity["measurementLocation"]["UUID"])
            timestamp = utc_rfc3339_to_datetime(entity["recorded"]["dateTime"])
            data = bytes(json.dumps(entity["data"]), "utf-8")

            buffer.append(
                (timestamp, measurement_id, timestamp, data, measurement_location_id)
            )

        except KeyError:
            continue


def logger(buffer, connection, manager):

    while True:
        while len(buffer) > 0:
            # Write data to database buffer and commit
            print(buffer[0])
            manager.copy(buffer.popleft())
            connection.commit()


def main():
    # Init a data buffer between the MQTT client and database client
    buffer = deque([tuple], maxlen=10000)

    # Connect to database and start logger thread
    connection = psycopg2.connect(
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        database=DATABASE_NAME,
    )
    manager = CopyManager(connection, TABLE, COLUMNS)
    threading.Thread(target=logger, args=(buffer, connection, manager))

    # Init and connect MQTT client
    mqtt = Client(client_id=MQTT_CLIENT_ID)
    mqtt.on_message = on_message
    mqtt.on_connect = on_connect
    mqtt.user_data_set(buffer)
    mqtt.connect(MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)
    mqtt.subscribe("#", qos=2)

    try:
        mqtt.loop_forever()
    except KeyboardInterrupt:
        print("User interrupt")
    finally:
        print("Disconnecting from MQTT broker")
        mqtt.disconnect()

        print("Emptying buffer to database...")
        while len(buffer) > 0:
            time.sleep(0.1)

        print("Closing database connection")
        connection.close()


if __name__ == "__main__":
    main()
