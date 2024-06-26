import asyncio
from bleak import BleakClient, BleakGATTCharacteristic
import struct

MAC_ADDR = 'A8:10:87:22:40:40'
CHARACTERISTIC = '70bc767e-7a1a-4304-81ed-14b9af54f7bd'


async def main():
    client = BleakClient(MAC_ADDR, timeout=60.0, disconnected_callback=disconnect_callback)
    try:
        await client.connect()
        await client.start_notify(CHARACTERISTIC, callback)
        while True:
            await asyncio.sleep(2)
    except Exception as e:
        print(f"Error while working with device {MAC_ADDR}. {e}")
    finally:
        await client.stop_notify(CHARACTERISTIC)
        await client.disconnect()


def callback(sender: BleakGATTCharacteristic, data: bytearray):
    print(f"{sender} {data}")
    intensity = struct.unpack('<f', data[5:9])[0]
    print(f"Current intensity: {intensity} \u03BCSv/h")
    dose = struct.unpack('<f', data[1:5])[0]
    print(f"Dose: {dose} mSv")
    temp = data[12]
    print(f"Temperature: {temp}\u2103")
    bat = data[11]
    print(f"Battery: {bat}%")
    print("---")


def disconnect_callback(client: BleakClient):
    print(f"{client.address} disconnect event recieved (no device nearby).")
    for task in asyncio.Task.all_tasks():
        task.cancel()


asyncio.run(main())
