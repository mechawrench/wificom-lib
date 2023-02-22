'''
This file is part of the DMComm project by BladeSabre. License: MIT.
WiFiCom on supported boards (see board_config.py).
'''
import time
import gc
import digitalio
import displayio
import microcontroller
import pwmio
import supervisor
import usb_cdc

# Light LED dimly while starting up. Doing this here because the following imports are slow.
# pylint: disable=wrong-import-order,wrong-import-position
gc.collect()
print("Free memory at start:", gc.mem_free())
LED_DUTY_CYCLE_DIM=0x1000
import board_config
led = pwmio.PWMOut(board_config.led_pin,
	duty_cycle=LED_DUTY_CYCLE_DIM, frequency=1000, variable_frequency=True)
# pylint: enable=wrong-import-order,wrong-import-position

from dmcomm import CommandError, ReceiveError
import dmcomm.hardware as hw
import dmcomm.protocol
import wificom.realtime as rt
import wificom.ui
from wificom import nvm
from wificom import mqtt
from wificom.import_secrets import secrets_imported, secrets_error_display
from config import config

gc.collect()
print("Free memory after imports:", gc.mem_free())

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
	if not mqtt.is_output_hidden:
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
	mqtt.send_rtb_digirom_output(message)
	print("RTB sent message:", message)
def rtb_receive_callback():
	'''
	Called when a RTB object checks for messages received.
	'''
	if mqtt.rtb_digirom is not None:
		msg = mqtt.rtb_digirom
		mqtt.rtb_digirom = None
		return msg
	return None
def rtb_status_callback(status, changed):
	'''
	Called when a RTB object updates the status display.
	'''
	if status == rt.STATUS_PUSH:
		led.duty_cycle = 0xFFFF
		if changed:
			ui.beep_activate()
	if status == rt.STATUS_PUSH_SYNC:
		led.duty_cycle = 0xFFFF
	if status in (rt.STATUS_IDLE, rt.STATUS_WAIT):
		led.duty_cycle = LED_DUTY_CYCLE_DIM

def main_menu():
	'''
	Show the main menu.
	'''
	serial_print("Main menu")
	if startup_mode == nvm.MODE_DEV:
		options_prefix = ["*Dev mode*"]
		results_prefix = [None]
	else:
		options_prefix = []
		results_prefix = []
	while True:
		menu_result = ui.menu(
			options_prefix + ["WiFi", "Serial", "Punchbag", "Drive"],
			results_prefix + [menu_wifi, menu_serial, menu_punchbag, menu_drive],
			None,
		)
		menu_result()

def menu_wifi():
	'''
	Chosen WiFi option from the menu.
	'''
	if serial == usb_cdc.console and startup_mode != nvm.MODE_DRIVE:
		run_wifi()
	else:
		menu_reboot(nvm.MODE_WIFI)

def menu_serial():
	'''
	Chosen Serial option from the menu.
	'''
	if serial == usb_cdc.data or startup_mode == nvm.MODE_DEV:
		run_serial()
	else:
		menu_reboot(nvm.MODE_SERIAL)

def menu_punchbag():
	'''
	Chosen Punchbag option from the menu.
	'''
	if serial == usb_cdc.console and startup_mode != nvm.MODE_DRIVE:
		run_punchbag()
	else:
		menu_reboot(nvm.MODE_PUNCHBAG)

def menu_drive():
	'''
	Chosen Drive option from the menu.
	'''
	if startup_mode in [nvm.MODE_DRIVE, nvm.MODE_DEV]:
		run_drive()
	else:
		menu_reboot(nvm.MODE_DRIVE)

def menu_reboot(mode):
	'''
	Reset, confirming USB drive ejection if necessary.
	'''
	if startup_mode in [nvm.MODE_DRIVE, nvm.MODE_DEV]:
		ui.display_text("Eject + press A")
		while not ui.is_a_pressed():
			pass
	nvm.set_mode(mode)
	ui.display_text("Rebooting...")
	time.sleep(0.5)
	ui.clear()
	microcontroller.reset()

done_wifi_before = False
def run_wifi():
	'''
	Do the normal WiFiCom things.
	'''
	# pylint: disable=too-many-branches,too-many-statements
	serial_print("Running WiFi")
	gc.collect()
	print("Free memory before WiFi:", gc.mem_free())

	digirom = None
	rtb_was_active = False
	rtb_type_id = None
	rtb_last_ping = 0

	if not secrets_imported:
		print("Error with secrets.py (see above)")
		ui.display_text(secrets_error_display)
		while not ui.is_c_pressed():
			pass
		return

	global done_wifi_before  # pylint: disable=global-statement
	if done_wifi_before:
		if startup_mode == nvm.MODE_DEV:
			ui.display_text("Soft reboot...")
			time.sleep(0.5)
			ui.clear()
			supervisor.reload()
		else:
			menu_reboot(nvm.MODE_WIFI)
	done_wifi_before = True

	# Connect to WiFi and MQTT
	led.frequency = 1
	led.duty_cycle = 0x8000
	ui.display_text("Connecting to WiFi")
	wifi = board_config.WifiCls(**board_config.wifi_pins)
	mqtt_client = wifi.connect()
	if mqtt_client is None:
		connection_failure_alert('WiFi')
	ui.display_text("Connecting to MQTT")
	mqtt.connect_to_mqtt(mqtt_client)
	led.frequency = 1000
	led.duty_cycle = LED_DUTY_CYCLE_DIM
	ui.display_text("WiFi\nHold C to change")
	while not ui.is_c_pressed():
		time_start = time.monotonic()
		replacement_digirom = mqtt.get_subscribed_output()
		if replacement_digirom is not None:
			if not mqtt.is_output_hidden:
				print("New digirom:", replacement_digirom)
			else:
				serial_print("Received digirom input, check the App")

		if replacement_digirom is not None:
			digirom = dmcomm.protocol.parse_command(replacement_digirom)

		if mqtt.rtb_active:
			rtb_type_id_new = (mqtt.rtb_battle_type, mqtt.rtb_user_type)
			if not rtb_was_active or rtb_type_id_new != rtb_type_id:
				rtb_type_id = rtb_type_id_new
				if rtb_type_id in rtb_types:
					rtb = rtb_types[rtb_type_id](
						execute_digirom,
						rtb_send_callback,
						rtb_receive_callback,
						rtb_status_callback,
					)
					rtb_status_callback(rtb.status, True)
				else:
					serial_print(mqtt.rtb_battle_type + " not implemented")
			rtb_was_active = True
			# Heartbeat approx every 10 seconds
			if time_start - rtb_last_ping > 10:
				mqtt.send_digirom_output("RTB")
				rtb_last_ping = time_start
			mqtt.loop()
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
			mqtt.send_digirom_output(last_output)

			while True:
				mqtt.loop()
				if mqtt.get_subscribed_output(False) is not None:
					break
				if time.monotonic() - time_start >= 5:
					break
				time.sleep(0.1)
def connection_failure_alert(failure_type):
	'''
	Alert on connection failure.
	'''
	led.duty_cycle = 0
	# pylint: disable=consider-using-f-string
	ui.display_text("{} Failed\nHold C to reboot".format(failure_type))
	ui.beep_wifi_failure()
	while True:
		time.sleep(0.5)
		if ui.is_c_pressed():
			time.sleep(2)
			supervisor.reload()
def run_serial():
	'''
	Run in serial mode.
	'''
	serial_print("Running serial")
	digirom = None
	ui.display_text("Serial\nHold C to change")
	while not ui.is_c_pressed():
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
				serial_print(f"{digirom.signal_type}{digirom.turn}-[{len(digirom)} packets]")
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
	serial_print("Running punchbag")
	digiroms = config["digiroms"]
	names = [name for (name, rom) in digiroms]
	roms = [dmcomm.protocol.parse_command(rom) for (name, rom) in digiroms]
	while True:
		rom = ui.menu(names, roms, "")
		if rom == "":
			return
		ui.display_text("Punchbag\nHold C to change")
		while not ui.is_c_pressed():
			time_start = time.monotonic()
			execute_digirom(rom)
			seconds_passed = time.monotonic() - time_start
			if seconds_passed < 5:
				time.sleep(5 - seconds_passed)
		time.sleep(1)

def run_drive():
	'''
	Run in drive mode.
	'''
	serial_print("Running drive")
	if not ui.has_display:
		while True:
			pass
	result = ui.menu(
		["*Drive enabled*", "WiFi", "Serial", "Punchbag"],
		[None, menu_wifi, menu_serial, menu_punchbag],
		None,
	)
	result()

# Serial port selection
if usb_cdc.data is not None:
	serial = usb_cdc.data
else:
	serial = usb_cdc.console
serial.timeout = 1
serial_print("WiFiCom starting")

outputs_extra_power = []
for (pin, value) in board_config.extra_power_pins:
	output = digitalio.DigitalInOut(pin)
	output.direction = digitalio.Direction.OUTPUT
	output.value = value
	outputs_extra_power.append(output)

gc.collect()
print("Free memory before dmcomm registrations:", gc.mem_free())
controller = hw.Controller()
for pin_description in board_config.controller_pins:
	controller.register(pin_description)
gc.collect()
print("Free memory after dmcomm registrations:", gc.mem_free())

startup_mode = nvm.get_mode()
mode_was_requested = nvm.was_requested()
serial_print("Mode: " + nvm.get_mode_str(), end="; ")
if nvm.clear_request():
	serial_print("request cleared")
else:
	serial_print("not requested")

displayio.release_displays()
ui = wificom.ui.UserInterface(**board_config.ui_pins)  #pylint: disable=invalid-name
ui.sound_on = config["sound_on"]

run_column = 0
if not ui.has_display:
	run_column += 2
	serial_print("Display not found: " + str(ui.display_error))
if not mode_was_requested:
	run_column += 1
serial_print("Run column: " + str(run_column))
branches = {
	# mode:            (ui requested, ui not req, no ui req,  no ui not req)
	nvm.MODE_MENU:     (main_menu,    main_menu,  run_wifi,   run_wifi),
	nvm.MODE_WIFI:     (run_wifi,     main_menu,  run_wifi,   run_wifi),
	nvm.MODE_SERIAL:   (run_serial,   main_menu,  run_serial, run_serial),
	nvm.MODE_PUNCHBAG: (run_punchbag, main_menu,  run_wifi,   run_wifi),  # last 2 unexpected
	nvm.MODE_DRIVE:    (run_drive,    run_drive,  run_drive,  run_drive), # last 2 unexpected
	nvm.MODE_DEV:      (main_menu,    main_menu,  run_wifi,   run_wifi),
}
branches[startup_mode][run_column]()
main_menu()
