'''
code.py
WiFiCom on supported boards (see board_config.py).
'''

import neopixel
import pwmio
import board_config

# Light LED dimly here so it comes on as soon as possible.
led_pwm = pwmio.PWMOut(board_config.led_pin,
	duty_cycle=0x1000, frequency=1000, variable_frequency=True)

try:
	led_neo = neopixel.NeoPixel(**board_config.neopixel, auto_write=False)
	led_neo.brightness = 0.1
	led_neo.fill(0xFFFFFF)
	led_neo.show()
except AttributeError:
	led_neo = None

from wificom import main  # pylint: disable=wrong-import-order,wrong-import-position

main.main(led_pwm, led_neo)
