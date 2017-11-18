from network import LoRa
import socket
import time
import binascii
import pycom

# stop LED heartbeat
pycom.heartbeat(False)
pycom.rgbled(0x000000)           # turn off LEDs

# Initialize LoRa in LORAWAN mode.
lora = LoRa(mode=LoRa.LORAWAN)

# create an OTAA authentication parameters
app_eui = binascii.unhexlify('0000000000000001'.replace(' ',''))
app_key = binascii.unhexlify('11B0282A189B75B0B4D2D8C7FA38548E'.replace(' ',''))

# Get the DevEUI from the node
print('DevEUI ', binascii.hexlify(lora.mac()))

# Quick Join in the US
for i in range(8, 72):
    print("Remove channel from search: ", i)
    lora.remove_channel(i)


# join a network using OTAA (Over the Air Activation)
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(1.0)
    pycom.rgbled(0x7f0000)           # blink RED led during join
    print('Not yet joined...')
    time.sleep(0.25)
    pycom.rgbled(0x000000)           # turn LED off


# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# selecting confirmed type of messages
s.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, True)

# set the LoRaWAN data rate
#s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)




cnt = 0
pycom.rgbled(0x000000)           # turn off

while True:
    # make the socket blocking
    # (waits for the data to be sent and for the 2 receive windows to expire)


    pycom.rgbled(0x007f00)           # turn on the green LED

    try:
        s.setblocking(True)
        # send some data
        s.send(bytes([cnt, 0x02, 0x03]))
        print( cnt, ' Sending...' )

    except Exception as e:
        if e.args[0] == 11:
            print('cannot send just yet, waiting...')
            time.sleep(2.0)
        else:
            raise    # raise the exception again

    pycom.rgbled(0x000000)           # turn on the RED LED

    # make the socket non-blocking
    # (because if there's no data received it will block forever...)
    s.setblocking(False)
    # get any data received (if any...)
    data = s.recv(64)
    if data:
        pycom.rgbled(0x00007f)           # turn on the RED LED
        print( 'Got:')
        print(data)
        time.sleep(0.25)
    else:
        print( 'No Data Received' )
    # saturating add so that count matches uint8 value in payload
    cnt+=1%255
    pycom.rgbled(0x000000)           # turn off LED
    time.sleep(5.0)
