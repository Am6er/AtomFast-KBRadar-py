import asyncio
from bleak import BleakScanner


async def main():
    devices = await BleakScanner.discover(timeout=60.0)
    for d in devices:
        print(f"Found device MAC {d.address}, Name {d.name}")

asyncio.run(main())
