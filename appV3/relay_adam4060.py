'''
Script to control relay OSA electronic for Pi
S. Filhol, April 2023

Relay Documnetation:
- https://www.osaelectronics.com/product/rlb0665n/#tab-documentation
'''

from pymodbus.client import ModbusSerialClient
from pymodbus.transaction import ModbusRtuFramer
import time
import argparse, os

addr_channels = {'channel_0': 16, 'channel_1': 17, 'channel_2': 18, 'channel_3': 19}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--switch', '-s', help='switch relay ON/OFF', default='on')
    parser.add_argument('--relay_channel', '-rc', help='relay to activate', default='channel_3')
    parser.add_argument('--time_delay', '-t', help='time to wait after switching relay in seconds', default=20)
    args = parser.parse_args()

    # Create a Modbus RTU client
    client = ModbusSerialClient(method='rtu', port='/dev/ttyS0', baudrate=9600, stopbits=1, bytesize=8, parity='N',
                                framer=ModbusRtuFramer)

    # Connect to the Modbus RTU slave
    if client.connect():
        # Define the slave address (or device address)
        slave_address = 0x01
        channel = addr_channels.get(args.relay_channel)
        time.sleep(1)
        if args.switch == 'on':
            response = client.write_coil(channel, 1, slave_address)
            if not response.isError():
                print(f"Channel  {args.relay_channel} turned ON")
                print(f"---> Delay of {args.time_delay} s")
                time.sleep(float(args.time_delay))
            else:
                raise ValueError(f"Error writing to channel {args.relay_channel}", response)

        elif args.switch == 'off':
            response = client.write_coil(channel, 0, slave_address)
            if not response.isError():
                print(f"Channel {args.relay_channel} turned OFF")
                time.sleep(0.5)
            else:
                raise ValueError(f"Error writing to channel {args.relay_channel}", response)
        # Close the connection
        client.close()
    else:
        raise ValueError('No client to connect to')
