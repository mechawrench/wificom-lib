'''
This file is part of the DMComm project by BladeSabre. License: MIT.
WiFiCom on supported boards (see board_config.py).
'''
import time
import digitalio
import displayio
import pwmio
import usb_cdc

# Light LED dimly while starting up. Doing this here because the following imports are slow.
# pylint: disable=wrong-import-order,wrong-import-position
LED_DUTY_CYCLE_DIM=0x1000
import board_config
led = pwmio.PWMOut(board_config.led_pin,
	duty_cycle=LED_DUTY_CYCLE_DIM, frequency=1000, variable_frequency=True)
# pylint: enable=wrong-import-order,wrong-import-position

from dmcomm import CommandError, ReceiveError
import dmcomm.hardware as hw
import dmcomm.protocol
import dmcomm.protocol.realtime as rt
import wificom.hardware.ui
from wificom.hardware import nvm
from wificom.mqtt import platform_io
import digiroms

def serial_print(contents, end="\n"):
	'''
	Print output to the serial console
	'''
	serial.write((contents + end).encode("utf-8"))

def execute_digirom(rom):
	'''
	Execute the digirom and report results according to reporting settings.
	'''
	error = ""
	result_end = "\n"
	try:
		controller.execute(rom)
	except (CommandError, ReceiveError) as ex:
		error = repr(ex)
		result_end = " "
	if not platform_io.is_output_hidden:
		serial_print(str(rom.result), result_end)
	else:
		serial_print("Received output, check the App")
	if error != "":
		serial_print(error)

rtb_types = {
	("legendz", "host"): rt.RealTimeHostTalis,
	("legendz", "guest"): rt.RealTimeGuestTalis,
	("digimon-penx-battle", "host"): rt.RealTimeHostPenXBattle,
	("digimon-penx-battle", "guest"): rt.RealTimeGuestPenXBattle,
}
def rtb_send_callback(message):
	'''
	Called when a RTB object sends a message.
	'''
	platform_io.send_rtb_digirom_output(message)
	print("RTB sent message:", message)
def rtb_receive_callback():
	'''
	Called when a RTB object checks for messages received.
	'''
	if platform_io.rtb_digirom is not None:
		msg = platform_io.rtb_digirom
		platform_io.rtb_digirom = None
		return msg
	return None
def rtb_status_callback(status):
	'''
	Called when a RTB object updates the status display.
	'''
	if status == rt.STATUS_PUSH:
		led.duty_cycle = 0xFFFF
	else:
		led.duty_cycle = LED_DUTY_CYCLE_DIM

def run_wifi():
	'''
	Do the normal WiFiCom things.
	'''
	# pylint: disable=too-many-branches,too-many-statements
	digirom = None
	rtb_was_active = False
	rtb_type_id = None
	rtb_last_ping = 0

	# Connect to WiFi and MQTT
	led.frequency = 1
	led.duty_cycle = 0x8000
	wifi = board_config.WifiCls(**board_config.wifi_pins)
	out, mqtt_client = wifi.connect()
	platform_io.connect_to_mqtt(out, mqtt_client)
	led.frequency = 1000
	led.duty_cycle = LED_DUTY_CYCLE_DIM

	while True:
		time_start = time.monotonic()
		replacement_digirom = platform_io.get_subscribed_output()
		if replacement_digirom is not None:
			if not platform_io.is_output_hidden:
				print("New digirom:", replacement_digirom)
			else:
				serial_print("Received digirom input, check the App")

		if replacement_digirom is not None:
			digirom = dmcomm.protocol.parse_command(replacement_digirom)

		if platform_io.rtb_active:
			rtb_type_id_new = (platform_io.rtb_battle_type, platform_io.rtb_user_type)
			if not rtb_was_active or rtb_type_id_new != rtb_type_id:
				rtb_type_id = rtb_type_id_new
				if rtb_type_id in rtb_types:
					rtb = rtb_types[rtb_type_id](
						execute_digirom,
						rtb_send_callback,
						rtb_receive_callback,
						rtb_status_callback,
					)
				else:
					serial_print(platform_io.rtb_battle_type + " not implemented")
			rtb_was_active = True
			# Heartbeat approx every 10 seconds
			if time_start - rtb_last_ping > 10:
				platform_io.send_digirom_output("RTB")
				rtb_last_ping = time_start
			platform_io.loop()
			rtb.loop()
		else:
			if rtb_was_active:
				led.duty_cycle = LED_DUTY_CYCLE_DIM
			rtb_was_active = False
			last_output = None
			if digirom is not None:
				execute_digirom(digirom)
				if len(str(digirom.result)) >= 1:
					last_output = str(digirom.result)

			# Send to MQTT topic (acts as a ping also)
			platform_io.send_digirom_output(last_output)

			while True:
				platform_io.loop()
				if platform_io.get_subscribed_output(False) is not None:
					break
				if time.monotonic() - time_start >= 5:
					break
				time.sleep(0.1)

def run_serial():
	'''
	Run in serial mode.
	'''
	digirom = None
	while True:
		time_start = time.monotonic()
		if serial.in_waiting != 0:
			digirom = None
			serial_bytes = serial.readline()
			serial_str = serial_bytes.decode("ascii", "ignore")
			# readline only accepts "\n" but we can receive "\r" after timeout
			if serial_str[-1] not in ["\r", "\n"]:
				serial_print("too slow")
				continue
			serial_str = serial_str.strip()
			serial_str = serial_str.strip("\0")
			serial_print(f"got {len(serial_str)} bytes: {serial_str} -> ", end="")
			try:
				command = dmcomm.protocol.parse_command(serial_str)
				if hasattr(command, "op"):
					# It's an OtherCommand
					raise NotImplementedError("op=" + command.op)
				digirom = command
				serial_print(f"{digirom.physical}{digirom.turn}-[{len(digirom)} packets]")
			except (CommandError, NotImplementedError) as ex:
				serial_print(repr(ex))
			time.sleep(1)
		if digirom is not None:
			execute_digirom(digirom)
		seconds_passed = time.monotonic() - time_start
		if seconds_passed < 5:
			time.sleep(5 - seconds_passed)

def run_punchbag():
	'''
	Run in punchbag mode.
	'''
	names = [name for (name, rom) in digiroms.items]
	roms = [dmcomm.protocol.parse_command(rom) for (name, rom) in digiroms.items]
	while True:
		rom = ui.menu(names, roms, "")
		if rom == "":
			return
		ui.display_text(["Punchbag", "Hold C to return"])
		while not ui.is_c_pressed():
			time_start = time.monotonic()
			execute_digirom(rom)
			seconds_passed = time.monotonic() - time_start
			if seconds_passed < 5:
				time.sleep(5 - seconds_passed)

def run_drive():
	'''
	Go into drive mode.
	'''
	while True:
		pass

# Serial port selection
if usb_cdc.data is not None:
	serial = usb_cdc.data
	#do_wifi = False
else:
	serial = usb_cdc.console
	#do_wifi = True
serial.timeout = 1
serial_print("WiFiCom starting")

outputs_extra_power = []
for (pin, value) in board_config.extra_power_pins:
	output = digitalio.DigitalInOut(pin)
	output.direction = digitalio.Direction.OUTPUT
	output.value = value
	outputs_extra_power.append(output)

controller = hw.Controller()
for pin_description in board_config.controller_pins:
	controller.register(pin_description)

displayio.release_displays()
ui = wificom.hardware.ui.UserInterface(**board_config.ui_pins)
while True:
	menu_result = ui.menu(
		["WiFi", "Serial", "Punchbag", "Drive"],
		[run_wifi, run_serial, run_punchbag, run_drive],
		None,
	)
	menu_result()
