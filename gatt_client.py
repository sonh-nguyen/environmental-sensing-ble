import asyncio
from bleak import BleakClient
from firebase import firebase
import time
import logging

ROOT_NODE = '/NUCLEO-F411RE'
TEMP = '/temp'
HUM = '/hum'
PRES = '/pres'

logger = logging.getLogger('GATT CLIENT')
logger.setLevel(logging.DEBUG)
syslog_handler = logging.FileHandler('/tmp/gattclient.log')
syslog_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
syslog_handler.setFormatter(formatter)
logger.addHandler(syslog_handler)

firebase_app = firebase.FirebaseApplication('https://environmental-sensing-5fd53-default-rtdb.asia-southeast1.firebasedatabase.app/', None)

async def run(address, loop):
    while True:
        try:
            async with BleakClient(address, loop=loop) as client:
                # Define the UUIDs for the Environment Service
                temperature_uuid = "00002a6e-0000-1000-8000-00805f9b34fb"
                humidity_uuid = "00002a6f-0000-1000-8000-00805f9b34fb"
                pressure_uuid = "00002a6d-0000-1000-8000-00805f9b34fb"

                # Read temperature data
                temperature_data = await client.read_gatt_char(temperature_uuid)
                temperature_value = int.from_bytes(temperature_data, byteorder='little') / 100.0

                # Read humidity data
                humidity_data = await client.read_gatt_char(humidity_uuid)
                humidity_value = int.from_bytes(humidity_data, byteorder='little') / 100.0

                # Read pressure data
                pressure_data = await client.read_gatt_char(pressure_uuid)
                pressure_value = int.from_bytes(pressure_data, byteorder='little') / 100.0

                # print(f"Temperature: {temperature_value} °C")
                # print(f"Humidity: {humidity_value} %")
                # print(f"Pressure: {pressure_value} hPa")

                logger.info(f"Temperature: {temperature_value} °C - Humidity: {humidity_value} % - Pressure: {pressure_value} hPa")

                firebase_app.put(ROOT_NODE, TEMP, temperature_value)
                firebase_app.put(ROOT_NODE, HUM, humidity_value)
                firebase_app.put(ROOT_NODE, PRES, pressure_value)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            # Handle the specific exception as needed (e.g., logging, notifying the user)

        # Add a delay before attempting to connect again
        time.sleep(3)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    device_mac_address = "D0:69:63:9A:89:A1"
    logger.info("Start GATT Client, wait 30s for Bluetooh service")
    time.sleep(30)
    loop.run_until_complete(run(device_mac_address, loop))
