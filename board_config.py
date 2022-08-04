'''
board_config.py
Handles differences between boards.

Arduino Nano RP2040 Connect, with BladeSabre's pin assignments.

Pi Pico + AirLift with initial pin assignments.
Currently prongs and modulated IR only, to make room for temporary AirLift positioning.
'''
import board
import dmcomm.hardware as hw

board_id = board.board_id
print("Board ID: ", board_id)

if board_id == "arduino_nano_rp2040_connect":
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
elif board_id == "raspberry_pi_pico":
	controller_pins = [
		hw.ProngOutput(board.GP19, board.GP21),
		hw.ProngInput(board.GP26),
		hw.InfraredOutput(board.GP16),
		hw.InfraredInputModulated(board.GP17),
	]
	extra_power_pins = [(board.GP18, True)]
	wifi_pins = {
		"esp32_sck": board.GP10,
		"esp32_mosi": board.GP11,
		"esp32_miso": board.GP12,
		"esp32_cs": board.GP13,
		"esp32_busy": board.GP14,
		"esp32_reset": board.GP15,
	}
else:
	raise ValueError("Your board is not supported.")
