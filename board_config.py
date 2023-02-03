'''
board_config.py
Handles differences between boards.

Arduino Nano RP2040 Connect, with BladeSabre's pin assignments.

Pi Pico + AirLift, with BladeSabre's pin assignments.
This was used for development but is no longer recommended.

Pi Pico W, with BladeSabre's pin assignments.
'''
import board
import dmcomm.hardware as hw

print("Board ID: ", board.board_id)

# pylint: disable=unused-import

if board.board_id == "arduino_nano_rp2040_connect":
	from wificom.hardware.nina_wifi import Wifi as WifiCls
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
	}
elif board.board_id == "raspberry_pi_pico":
	from wificom.hardware.nina_wifi import Wifi as WifiCls
	led_pin = board.LED
	controller_pins = [
		hw.ProngOutput(board.GP19, board.GP21),
		hw.ProngInput(board.GP26),
		hw.InfraredOutput(board.GP16),
		hw.InfraredInputModulated(board.GP17),
		hw.InfraredInputRaw(board.GP14),
		hw.TalisInputOutput(board.GP15),
	]
	extra_power_pins = [
		(board.GP11, True),
		(board.GP13, True),
		(board.GP18, True),
	]
	wifi_pins = {
		"esp32_sck": board.GP6,
		"esp32_mosi": board.GP7,
		"esp32_miso": board.GP4,
		"esp32_cs": board.GP5,
		"esp32_busy": board.GP8,
		"esp32_reset": board.GP9,
	}
	ui_pins = None
elif board.board_id == "raspberry_pi_pico_w":
	from wificom.hardware.picow_wifi import Wifi as WifiCls
	led_pin = board.GP10
	controller_pins = [
		hw.ProngOutput(board.GP19, board.GP21),
		hw.ProngInput(board.GP22),
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
	}
else:
	raise ValueError("Your board is not supported.")
