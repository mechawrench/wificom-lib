'''
code.py
WiFiCom on supported boards (see board_config.py).
'''
# pylint: disable=wrong-import-order,wrong-import-position

from wificom import led_hardware
import board_config

# Light LEDs dimly here so they come on as soon as possible.
leds = led_hardware.LedHardware(board_config)
leds.dim(0xFFFFFF)

from wificom import main  #pylint:disable=ungrouped-imports

main.main(leds)
