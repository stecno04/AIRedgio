import usb.core
import usb
import array

# info = usb.core.show_devices()
# busses = usb.busses()
# for bus in busses:
#     devices = bus.devices
#     for dev in devices:
#         print(dev.idVendor, dev.idProduct)

def add(byte_array: array.array, position: int) -> array.array | None:
    if position >= len(byte_array):
        return None
    if (byte_array[position] == 255):
        byte_array[position] = 0
        return add(byte_array, position)
    return byte_array

dev: usb.core.Device = usb.core.find(idVendor=1155, idProduct=22352)
endpoint = dev[0][(0,0)][0]
endpoint2 = dev[0][(0,0)][1]
init = [0 for _ in range(64)]
init[0] = 179
payload = array.array('B', init)
c = 0
while True:
    c += 1
    payload = add(payload, 0)
    # print(payload)
    

    dev.write(endpoint2.bEndpointAddress, payload)
    data = dev.read(endpoint.bEndpointAddress,endpoint.wMaxPacketSize)
    
    numero_intero = (int.from_bytes(bytes(data[0:2]), byteorder='big'))/10  # Interpreta i byte come intero (big-endian)

    print(numero_intero)  # Output: 16909060
    # time.sleep(1)
    

    # print(payload[0], datetime.fromtimestamp(time.time()))
    