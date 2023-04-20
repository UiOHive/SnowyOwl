'''
Script to control relay OSA electronic for Pi
S. Filhol, April 2023

Relay Documnetation:
- https://www.osaelectronics.com/product/rlb0665n/#tab-documentation
'''

# Imports Section
import smbus
import time
import argparse, os

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--switch', '-s', help='switch relay ON/OFF', default='on')
    parser.add_argument('--relay_id', '-ri', help='relay to activate', default=1)
    parser.add_argument('--initial_all_off', '-off', help='turn initially all relay off', default=True)
    parser.add_argument('--time_delay', '-t', help='time to wait after switching relay in seconds', default=20)
    args = parser.parse_args()

    # Initial Setup
    relays = {
        '1': 0xFE,
        '2': 0xFD,
        '3': 0xFB,
        '4': 0xF7,
        '5': 0xEF,
        '6': 0xDF
    }

    bus = smbus.SMBus(1)

    # Set the I2C address
    PCF8574_addr = 0x20

    if args.initial_all_off:
        print(f'Turning all relay OFF')
        bus.write_byte(PCF8574_addr, 0xFF) # Turn all relays OFF

    # in prep. of switch relay individually
    state = bus.read_byte(PCF8574_addr)

    if args.switch.lower() == 'on':
        print(f'Turning relay {args.relay_id} ON')
        bus.write_byte(PCF8574_addr, relays.get(str(args.relay_id)))
        time.sleep(args.time_delay)

    if args.switch.lower() == 'off':
        print(f'Turning all relay OFF')
        #bus.write_byte(PCF8574_addr, relays.get(str(args.relay_id))) # Turn ON Relay 1
        bus.write_byte(PCF8574_addr, 0xFF)
        time.sleep(0.5)


