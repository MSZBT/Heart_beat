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
    ]
}

class Device_bracelet:
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.heartRate = 0
        self._client = None
        self.status = False
        
    async def connect(self):
        self._client = BleakClient(self.address)
        await self._client.connect()

        def callback(sender, data):
            self._update_heart_rate(data)
        
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
    #print(DICTOWNERS["1"])
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
            new_devices = []
            
            for device in found_devices:
                if device.name and device.name.startswith("H1_"):
                    exists = any(
                        DICTOWNERS[key][1] and 
                        DICTOWNERS[key][1].name == device.name 
                        for key in DICTOWNERS
                    )
                    if not exists:
                        new_devices.append(device)

            async with print_lock:
                if new_devices:
                    print("\n" + "="*50)
                    print("Found NEW devices not in DICTOWNERS:")
                    for device in new_devices:
                        print(f"- {device.name} ({device.address})")
                    print("="*50)
                else:
                    print("\nNo new compatible devices found")
            
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
            output.append("-"*60)
            for key in DICTOWNERS:
                if DICTOWNERS[key][1]:
                    output.append('%-5s | %-10s | %-20s | %-10s | %-10s' % 
                           (key, DICTOWNERS[key][1].name, DICTOWNERS[key][1].address, DICTOWNERS[key][1].heartRate, "Connected" if DICTOWNERS[key][1].status else "Disconnected"))
            print("\n".join(output))
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

