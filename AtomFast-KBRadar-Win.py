import asyncio
import datetime
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
    intensity_list = []

    def add_intensity(self, intens: float):
        self.intensity_list.append(intens)

    def get_avg_intensity(self) -> float:
        avg_intens = sum(self.intensity_list) / len(self.intensity_list)
        self.intensity_list.clear()
        return avg_intens


DATA = Data()


async def main():
    while True:
        client = BleakClient(MAC_ADDR, timeout=60.0, disconnected_callback=disconnect_callback)
        try:
            print(f"{datetime.datetime.now()} Connect to device with MAC {MAC_ADDR}")
            await client.connect()
            await client.start_notify(CHARACTERISTIC, callback)
            while True:
                await asyncio.sleep(60 * 5)
                # once per 5 minutes
                if DATA.intensity is not None:
                    avg_intens = DATA.get_avg_intensity()
                    post_data = {
                        'ID': MAC_ADDR,
                        'NAME': 'AtomFast',
                        'R_DoseRate': avg_intens,
                    }

                    post_headers = {
                        'Content-Length': str(len(post_data)),
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Host': 'narodmon.ru'
                    }

                    response = requests.post(url='https://narodmon.ru/post.php', data=post_data, headers=post_headers)
                    print(f"{datetime.datetime.now()} Post data to narodmon AVG Intesity: {avg_intens} \u03BCR/h. Result: {response}")
        except Exception as e:
            print(f"Error while working with device {MAC_ADDR}. {e}")
        finally:
            if client is not None and client.is_connected:
                await client.stop_notify(CHARACTERISTIC)
                await client.disconnect()


def callback(sender: BleakGATTCharacteristic, data: bytearray):
    # print(f"{sender} {data}")
    DATA.intensity = 100 * struct.unpack('<f', data[5:9])[0]
    DATA.add_intensity(DATA.intensity)
    DATA.dose = 100 * struct.unpack('<f', data[1:5])[0]
    DATA.temp = data[12]
    DATA.bat = data[11]
    # printresult(DATA)


def printresult(data: Data):
    if data.intensity is None:
        return
    print(f"{datetime.datetime.now()}")
    print(f"Current intensity: {data.intensity} \u03BCR/h")
    print(f"Dose: {data.dose} mR")
    print(f"Temperature: {data.temp}\u2103")
    print(f"Battery: {data.bat}%")


def disconnect_callback(client: BleakClient):
    print(f"{client.address} disconnect event recieved (no device nearby).")


asyncio.run(main())
