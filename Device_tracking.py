import asyncio, json
from bleak import BleakScanner, BleakClient

HEART_RATE_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
HEART_RATE_MEASUREMENT_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

print_lock = asyncio.Lock()

DICTOWNERS = {
    "1": ["H1_31543", None],
    "2": ["H1_38200", None],
    "3": ["H1_39251", None],
    "4": ["H1_39415", None],
    "5": ["H1_40673", None],
    "6": ["H1_41002", None]
}

class DeviceBracelet:
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.heart_rate = 0
        self._client = None
        self.status = False
    
    def on_disconnect(self, client: BleakClient):
        self.status = False
        self.heart_rate = "N/D"
        print(f"Disconnected: {self.name}")
        try:
            if self._client:
                asyncio.create_task(self._client.unpair())
        except Exception as e:
            print(f"Error unpairing: {e}")

    async def connect(self):
        try:
            self._client = BleakClient(
                self.address,
                disconnected_callback=self.on_disconnect
            )
            
            await self._client.connect(timeout=20.0)
            self.status = True
            
            def heart_rate_callback(sender, data):
                flags = data[0]
                if flags & 0x01:  # 16-bit
                    self.heart_rate = int.from_bytes(data[1:3], 'little')
                else:  # 8-bit
                    self.heart_rate = int(data[1])
            
            await self._client.start_notify(
                HEART_RATE_MEASUREMENT_UUID,
                heart_rate_callback
            )
            
            for owner in DICTOWNERS:
                if DICTOWNERS[owner][0] == self.name:
                    DICTOWNERS[owner][1] = self
            
            return True
        
        except Exception as e:
            print(f"Connection error for {self.name}: {e}")
            self.status = False
            return False

async def scan_devices():
    async with print_lock:
        print("\nScanning for devices...")
    
    try:
        devices = await BleakScanner(scanning_mode="active").discover(timeout=10.0)
        
        for d in devices:
            if d.name and d.name.startswith("H1_"):
                device_exists = any(
                    DICTOWNERS[owner][1] and DICTOWNERS[owner][1].name == d.name 
                    for owner in DICTOWNERS
                )
                
                if not device_exists:
                    new_device = DeviceBracelet(str(d.name), str(d.address))
                    for owner in DICTOWNERS:
                        if DICTOWNERS[owner][0] == new_device.name:
                            DICTOWNERS[owner][1] = new_device
                            print(f"Found new device: {new_device.name}")
    
    except Exception as e:
        print(f"Scan error: {e}")

async def continuous_scan(interval=30):
    while True:
        await scan_devices()
        await asyncio.sleep(interval)

async def monitor_devices():
    while True:
        try:
            connect_tasks = []
            for owner in DICTOWNERS:
                device = DICTOWNERS[owner][1]
                if device and not device.status:
                    connect_tasks.append(device.connect())
            
            if connect_tasks:
                await asyncio.gather(*connect_tasks)
        
        except Exception as e:
            print(f"Monitoring error: {e}")
        
        await asyncio.sleep(5)

async def print_status(): 
    TRANSMIT_DATA = {
        "1": "N/D",
        "2": "N/D",
        "3": "N/D",
        "4": "N/D",
        "5": "N/D",
        "6": "N/D"
    }
    while True:
        for key in DICTOWNERS:
            device = DICTOWNERS[key][1]
            if device and device.status:
                TRANSMIT_DATA[key] = device.heart_rate
            else:
                TRANSMIT_DATA[key] = "N/D"
        
        with open("TRANSMIT.json", "w") as f:
            json.dump(TRANSMIT_DATA, f)
            
        await asyncio.sleep(1)


async def main():
    await scan_devices()

    await asyncio.gather(
        monitor_devices(),
        print_status(),
        asyncio.create_task(continuous_scan())
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nExiting...")