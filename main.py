import os
import json
import uuid
import signal
import threading
from datetime import datetime
from collections import deque

import pytz
import psycopg2
from pgcopy import CopyManager
from paho.mqtt.client import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TABLE = "orm_singledatameasurement"
COLUMNS = ("time", "UUID", "recorded", "data", "measurement_location_id")

DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = int(os.getenv("DATABASE_PORT", 5600))
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")

MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID")
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))

BUFFER_MAX_SIZE = int(os.getenv("BUFFER_MAX_SIZE", 10000))
# Init a data buffer between the MQTT client and database client
buffer: deque = deque([], maxlen=BUFFER_MAX_SIZE)


def utc_rfc3339_to_datetime(date: str) -> datetime:
    """Convert UTC RFC 3339 datetime string to Python datetime object"""

    return datetime.fromisoformat(date.replace("Z", "")).replace(tzinfo=pytz.UTC)


def on_connect(client, userdata, flags, rc):
    print("Connected to broker with result code " + str(rc))


def on_message(client, userdata, message):
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


def logger(connection, manager, terminate):
    """Write data from buffer to database until terminated with terminate flag"""

    while not terminate.is_set():
        while len(buffer) > 0:
            # Write data to database buffer and commit
            manager.copy([buffer.popleft()])
            connection.commit()


def main():
    def stop_service(signum, frame):
        """Stop connections gracefully"""

        print("Received signal:", signum)

        print("Disconnecting from MQTT broker")
        mqtt.disconnect()

        print("Emptying buffer to database...")
        terminate.set()
        logger_thread.join()

        print("Closing database connection")
        connection.close()

        exit()

    # Connect to database and start logger thread
    connection = psycopg2.connect(
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        database=DATABASE_NAME,
    )
    manager = CopyManager(connection, TABLE, COLUMNS)
    terminate = threading.Event()
    logger_thread = threading.Thread(
        target=logger, args=(connection, manager, terminate)
    )
    logger_thread.start()

    # Init and connect MQTT client
    mqtt = Client(client_id=MQTT_CLIENT_ID)
    mqtt.on_message = on_message
    mqtt.on_connect = on_connect
    mqtt.user_data_set(buffer)
    mqtt.connect(MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)
    mqtt.subscribe("#", qos=2)

    # Set signal callback for stopping service gracefully
    signal.signal(signal.SIGINT, stop_service)
    signal.signal(signal.SIGTERM, stop_service)

    mqtt.loop_forever()


if __name__ == "__main__":
    main()
