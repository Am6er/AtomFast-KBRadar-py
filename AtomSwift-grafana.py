import asyncio
import datetime
import requests
from bleak import BleakClient, BleakGATTCharacteristic
import struct
import time

MAC_ADDR = 'F8:30:02:30:C2:2F'
CHARACTERISTIC = '70bc767e-7a1a-4304-81ed-14b9af54f7bd'

class Data:
    intensity = None
    dose = None
    temp = None
    bat = None
    intensity_list = []
    temp_list = []
    RECONNECT_FLAG = False

    def add_metrics(self, intens: float, temp: float):
        self.intensity_list.append(intens)
        self.temp_list.append(temp)

    def get_avg_intensity(self) -> float:
        avg_intens = sum(self.intensity_list) / len(self.intensity_list)
        self.intensity_list.clear()
        return avg_intens

    def get_avg_temp(self) -> float:
        avg_temp = sum(self.temp_list) / len(self.temp_list)
        self.temp_list.clear()
        return avg_temp


DATA = Data()


async def main():
    print(f"{datetime.datetime.now()} Service started, now try to connect to {MAC_ADDR}")
    while True:
        client = BleakClient(MAC_ADDR, timeout=60.0, disconnected_callback=disconnect_callback)
        try:
            await client.connect()
            await client.start_notify(CHARACTERISTIC, callback)
            print(f"{datetime.datetime.now()} Connect to device with MAC {MAC_ADDR}")
            while True:
                seconds = 60
                for _ in range(0, seconds):
                    await asyncio.sleep(5)
                    if DATA.RECONNECT_FLAG:
                        print(f"{datetime.datetime.now()} Stop flag recieved, reconnecting")
                        break
                if DATA.RECONNECT_FLAG:
                    DATA.RECONNECT_FLAG = False
                    break
                # once per 5 minutes
                if len(DATA.intensity_list) == 0 or len(DATA.temp_list) == 0:
                    print(f"{datetime.datetime.now()} Empty list of measurements, reconnecting")
                    break
                if DATA.intensity is not None:
                    avg_intens = DATA.get_avg_intensity()
                    avg_temp = DATA.get_avg_temp()
                    post_data = {
                        'ID': MAC_ADDR,
                        'NAME': 'AtomFast',
                        'R_DoseRate': avg_intens,
                        'TEMP_Detector': avg_temp,
                    }

                    post_headers = {
                        'Content-Length': str(len(post_data)),
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Host': 'narodmon.ru'
                    }
                    try:
                        response = requests.post(url='https://narodmon.ru/post.php', data=post_data, headers=post_headers)
                        print(f"{datetime.datetime.now()} Post data to narodmon AVG Intesity: {avg_intens} \u03BCR/h, AVG Temp: {avg_temp} \u2103  Result: {response}")
                    except Exception as e:
                        print(f"{datetime.datetime.now()} Error while sending data to narodmon. {e.__str__()}")

                    post_data = f'DOSERATE,MODEL="AtomSwift" value={avg_intens}'

                    post_headers = {
                        'Content-Length': str(len(post_data)),
                        'Content-Type': 'text/plain; charset=utf-8',
                        'Host': '192.168.1.2'
                    }
                    try:
                        response = requests.post(url='http://192.168.1.2:8086/write?db=mon', data=post_data, headers=post_headers)
                        print(f"{datetime.datetime.now()} Post data to InfluxDB AVG Intesity: {avg_intens} \u03BCR/h, Result: {response}")
                    except Exception as e:
                        print(f"{datetime.datetime.now()} Error while sending data to InfluxDB. {e.__str__()}")

                    post_data = f'TEMPERATURE,MODEL="AtomSwift" value={avg_temp}'

                    post_headers = {
                         'Content-Length': str(len(post_data)),
                         'Content-Type': 'text/plain; charset=utf-8',
                         'Host': '192.168.1.2'
                    }

                    try:
                        response = requests.post(url='http://192.168.1.2:8086/write?db=mon', data=post_data, headers=post_headers)
                        print(f"{datetime.datetime.now()} Post data to InfluxDB AVG Temp: {avg_temp} \u2103, Result: {response}")
                    except Exception as e:
                        print(f"{datetime.datetime.now()} Error while sending data to InfluxDB. {e.__str__()}")


        except Exception as e:
            print(f"{datetime.datetime.now()} Error while working with device {MAC_ADDR}. {e.__str__()}")


def callback(sender: BleakGATTCharacteristic, data: bytearray):
    DATA.dose = 100 * struct.unpack('<f', data[1:5])[0]
    DATA.intensity = 100 * struct.unpack('<f', data[5:9])[0]
    DATA.bat = data[11]
    DATA.temp = data[12]
    DATA.add_metrics(DATA.intensity, DATA.temp)
    # printresult(DATA)


def printresult(data: Data):
    if data.intensity is None:
        return
    print(f"{datetime.datetime.now()};Intensity (\u03BCR/h);{data.intensity};Dose (mR);{data.dose};Temp (\u2103);{data.temp};Bat (%);{data.bat}")


def disconnect_callback(client: BleakClient):
    print(f"{datetime.datetime.now()} {client.address} disconnect event recieved (no device nearby).")
    DATA.intensity_list.clear()
    DATA.temp_list.clear()
    DATA.RECONNECT_FLAG = True


asyncio.run(main())
