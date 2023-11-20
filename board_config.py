'''
board_config.py
Handles differences between boards.

WiFiCom:
Recommended pins are assigned here for:
- Raspberry Pi Pico W
- Arduino Nano RP2040 Connect
If you are using another RP2040 board with an AirLift module,
you will need to edit this file.

Non-WiFi:
Recommended pins are assigned here for:
- Raspberry Pi Pico
- Seeeduino Xiao RP2040

Note `wifi_type` is not present in older board_config.
'''

import board
import dmcomm.hardware as hw

if board.board_id in ["raspberry_pi_pico", "raspberry_pi_pico_w"]:
	if board.board_id == "raspberry_pi_pico_w":
		wifi_type = "picow"
		led_pin = board.GP10
	else:
		wifi_type = None
		led_pin = board.LED
	controller_pins = [
		hw.ProngOutput(board.GP19, board.GP21),
		hw.ProngInput(board.GP22),  # note this may need changed to GP26 on older builds
		hw.InfraredOutput(board.GP16),
		hw.InfraredInputModulated(board.GP17),
		hw.InfraredInputRaw(board.GP14),
		hw.TalisInputOutput(board.GP15),
	]
	extra_power_pins = [
		(board.GP13, True),
		(board.GP18, True),
	]
	wifi_pins = {}
	ui_pins = {
		"display_scl": board.GP5,
		"display_sda": board.GP4,
		"button_a": board.GP9,
		"button_b": board.GP8,
		"button_c": board.GP3,
		"speaker": board.GP2,
	}
elif board.board_id == "arduino_nano_rp2040_connect":
	wifi_type = "nina"
	led_pin = board.LED
	controller_pins = [
		hw.ProngOutput(board.A0, board.A2),
		hw.ProngInput(board.A3),
		hw.InfraredOutput(board.D9),
		hw.InfraredInputModulated(board.D10),
		hw.InfraredInputRaw(board.D5),
		hw.TalisInputOutput(board.D4),
	]
	extra_power_pins = [
		(board.D6, False),
		(board.D7, True),
		(board.D8, False),
		(board.D11, False),
		(board.D12, True),
	]
	wifi_pins = {
		"esp32_sck": board.SCK1,
		"esp32_mosi": board.MOSI1,
		"esp32_miso": board.MISO1,
		"esp32_cs": board.CS1,
		"esp32_busy": board.ESP_BUSY,
		"esp32_reset": board.ESP_RESET,
	}
	ui_pins = {
		"display_scl": board.A5,
		"display_sda": board.A4,
		"button_a": board.D1,
		"button_b": board.D2,
		"button_c": board.D3,
		"speaker": board.D0,
	}
elif board.board_id == "seeeduino_xiao_rp2040":
	wifi_type = None
	# The on-board LED is inverted, so pretty useless. And want external for cased units.
	led_pin = board.A3
	controller_pins = [
		hw.ProngOutput(board.D10, board.D7),  # D10 is GP3, D9 is GP4
		hw.ProngInput(board.D8),
		hw.InfraredOutput(board.A1),
		hw.InfraredInputModulated(board.A2),
		hw.InfraredInputRaw(board.A0),
	]
	extra_power_pins = []
	wifi_pins = {}
	ui_pins = {
		"display_scl": None,
		"display_sda": None,
		"button_a": None,
		"button_b": None,
		"button_c": board.D6,
		# Speaker is not currently optional. Avoid wasting a pin we might need in future.
		"speaker": board.LED_RED,
	}
else:
	raise ValueError("Please configure pins in board_config.py")

# pylint: disable=unused-import
try:
	import wificom
except ImportError:
	wifi_type = None  # support dmcomm-python by itself
if wifi_type == "picow":
	from wificom.wifi_picow import Wifi as WifiCls
elif wifi_type == "nina":
	from wificom.wifi_nina import Wifi as WifiCls
else:
	WifiCls = None  # pylint: disable=invalid-name
