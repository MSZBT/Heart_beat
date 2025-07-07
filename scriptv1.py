import asyncio
from bleak import BleakScanner, BleakClient

HEART_RATE_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
HEART_RATE_MEASUREMENT_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

print_lock = asyncio.Lock()

#DICTOWNERS = {
#    "OWNER_1": [
#        "NAME_DEVICE",
#        #//OBJECT OF DEVICE//#
#    ]
#}

DICTOWNERS = {
    "1": [
        "H1_38200",
        None
    ],

    "2": [
        "H1_39251",
        None
    ],

    "3": [
        "H1_39415",
        None
    ],
    "4": [
        "H1_41002",
        None
    ]
}

TRACKING_DEVICES = set()
UNTRACKING_DEVICES = set()
#будет содержать ("H1_39415",None)
#содержат адреса устройств

class Device_bracelet:
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.heartRate = 0
        self._client = None
        self.status = False
    
    def on_disconnect(self, client: BleakClient):
            self.status = False
            print(f"Disconnected: {self.name}")
            TRACKING_DEVICES.discard((self.name, self))
            UNTRACKING_DEVICES.add((self.name, self))
            #получаем данные что устрйство отключено

    async def connect(self):
        self._client = BleakClient(self.address, disconnected_callback=self.on_disconnect)
        await self._client.connect()

        def callback(sender, data):
            self._update_heart_rate(data)
            '''if not (self.name, self) in TRACKING_DEVICES:
                TRACKING_DEVICES.add((self.name, self))'''
            if not any(d_name == self.name for d_name, _ in TRACKING_DEVICES):
                TRACKING_DEVICES.add((self.name, self))
                UNTRACKING_DEVICES.discard((self.name, self))

        
        await self._client.start_notify(
            HEART_RATE_MEASUREMENT_UUID,
            callback
        )
        return True
    
    def _update_heart_rate(self, data):
        self.status = self._client.is_connected
        flags = data[0]
        if flags & 0x01:  # 16-bit
            self.heartRate = int.from_bytes(data[1:3], 'little')
        else:  # 8-bit
            self.heartRate = int(data[1])


stub = Device_bracelet("Undefind", "Not find")
for key in DICTOWNERS:
    DICTOWNERS[key][1] = stub

    
async def scan_devices():
    async with print_lock:
        print("\nScanning for devices...", end="\r")
    devices = await BleakScanner.discover()    
    PREFIX = "H1_"
    for d in devices:
        if d.name and str(d.name).startswith(PREFIX):
            new_device = Device_bracelet(str(d.name), str(d.address))
            for key in DICTOWNERS:
                if DICTOWNERS[key][0] == new_device.name:
                    DICTOWNERS[key][1] = new_device

async def continuous_scan(interval=5):
    while True:
        try:
            found_devices = await BleakScanner.discover()
            current_device_names = {d.name for d in found_devices if d.name and d.name.startswith("H1_")}
            for name in current_device_names:
                if not any(d_name == name for d_name, _ in TRACKING_DEVICES) and \
                   not any(d_name == name for d_name, _ in UNTRACKING_DEVICES):
                    address = next(d.address for d in found_devices if d.name == name)
                    new_device = Device_bracelet(name, address)
                    UNTRACKING_DEVICES.add((new_device.name, new_device))
            
        except Exception as e:
            async with print_lock:
                print(f"Scanning error: {str(e)}")
        
        await asyncio.sleep(interval)


async def monitor_devices():
    while True:
        tasks = []
        for key in DICTOWNERS:
            device = DICTOWNERS[key][1]
            if device and not device.status:  
                tasks.append(device.connect()) 
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True) 
        
        await asyncio.sleep(1)


async def print_heart_rates():    
    while True:
        async with print_lock:
            output = []
            output.append("\nHeart Rate Monitor:")
            output.append('%-5s | %-10s | %-20s | %-10s | %-10s' % ('Owner', 'Name', "Address", "BPM", "Status"))
            output.append("-"*69)
            for key in DICTOWNERS:
                if DICTOWNERS[key][1]:
                    output.append('%-5s | %-10s | %-20s | %-10s | %-10s' % 
                           (key, DICTOWNERS[key][1].name, DICTOWNERS[key][1].address, DICTOWNERS[key][1].heartRate, "Connected" if DICTOWNERS[key][1].status else "Disconnected"))
            print("\n".join(output))

            print(f"{'=' * 69}")
            print("TRACKING DEVICES:")
            print(f"{'-' * 69}\n")
            for d in TRACKING_DEVICES:
                print(d)
            
            print(f"{'=' * 69}\n")
            print("UNTRACKING DEVICES:")
            print(f"{'-' * 69}\n")
            for d in UNTRACKING_DEVICES:
                print(d)
            print(f"{'=' * 69}\n") 
        await asyncio.sleep(1)

async def main():
    await scan_devices()
    
    await asyncio.gather(
        monitor_devices(),
        print_heart_rates(),
        continuous_scan()
    )

if __name__ == "__main__":
    asyncio.run(main())

