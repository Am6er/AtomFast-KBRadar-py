import asyncio
import requests

from bleak import BleakClient, BleakGATTCharacteristic
import struct

MAC_ADDR = 'A8:10:87:22:40:40'
CHARACTERISTIC = '70bc767e-7a1a-4304-81ed-14b9af54f7bd'


class Data:
    intensity = None
    dose = None
    temp = None
    bat = None


DATA = Data()


async def main():
    while True:
        client = BleakClient(MAC_ADDR, timeout=60.0, disconnected_callback=disconnect_callback)
        try:
            await client.connect()
            await client.start_notify(CHARACTERISTIC, callback)
            while True:
                await asyncio.sleep(60*5)
                # once per 5 minutes
                if DATA.intensity is not None:
                    post_data = {
                        'ID': MAC_ADDR,
                        'NAME': 'AtomFast',
                        'R_DoseRate': DATA.intensity,
                    }

                    post_headers = {
                        'Content-Length': str(len(post_data)),
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Host': 'narodmon.ru'
                    }

                    response = requests.post(url='https://narodmon.ru/post.php', data=post_data, headers=post_headers)
                    print(response)
                    return
        except Exception as e:
            print(f"Error while working with device {MAC_ADDR}. {e}")
        finally:
            if client is not None and client.is_connected:
                await client.stop_notify(CHARACTERISTIC)
                await client.disconnect()


def callback(sender: BleakGATTCharacteristic, data: bytearray):
    # print(f"{sender} {data}")
    DATA.intensity = struct.unpack('<f', data[5:9])[0]
    # print(f"Current intensity: {DATA.intensity} \u03BCSv/h")
    DATA.dose = struct.unpack('<f', data[1:5])[0]
    # print(f"Dose: {DATA.dose} mSv")
    DATA.temp = data[12]
    # print(f"Temperature: {DATA.temp}\u2103")
    DATA.bat = data[11]
    # print(f"Battery: {DATA.bat}%")
    # print("---")


def disconnect_callback(client: BleakClient):
    print(f"{client.address} disconnect event recieved (no device nearby).")


asyncio.run(main())
