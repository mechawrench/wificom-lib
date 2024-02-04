'''
main.py
Handles WiFiCom main program logic.
'''

import time
import errno
import gc
import os
import random
import traceback

import board
import digitalio
import displayio
import microcontroller
import supervisor
import usb_cdc

from adafruit_minimqtt.adafruit_minimqtt import MMQTTException
from dmcomm import CommandError, ReceiveError
import dmcomm.hardware as hw
import dmcomm.protocol
import wificom.realtime as rt
import wificom.ui
from wificom import modes
from wificom import mqtt
from wificom import settings
from wificom.import_secrets import secrets_imported, secrets_error, secrets_error_display
from config import config
import board_config
import version_info

LOG_FILENAME = "wificom_log.txt"
LOG_FILENAME_OLD = "wificom_log_old.txt"
LOG_MAX_SIZE = 2000
startup_mode = None
controller = None
ui = None  #pylint: disable=invalid-name
done_wifi_before = False
serial = usb_cdc.console

COMMAND_DIGIROM = 0
COMMAND_ERROR = 1
COMMAND_P = 2
COMMAND_I = 3

def serial_readline():
	'''
	Custom version of serial.readline() which accepts CR as well as LF.
	Also converts to string and strips result. Prints errors.
	Returns None on error or if stripped result is empty.
	'''
	if serial.in_waiting == 0:
		return None
	data_received = bytearray()
	while True:
		item = serial.read(1)
		if len(item) == 0:
			print(f"too slow: {bytes(data_received)}")
			return None
		if item in (b"\r", b"\n"):
			break
		data_received.append(item[0])
	try:
		serial_str = data_received.decode("utf-8")
	except UnicodeError:
		print(f"UnicodeError: {bytes(data_received)}")
		return None
	serial_str = serial_str.strip().strip("\0")
	if serial_str == "":
		return None
	return serial_str

def get_version_info():
	'''
	Convert version info to a TOML string.
	'''
	return f'''name = "{version_info.name}"\r
version = "{version_info.version}"\r
variant = "{version_info.variant}"\r
circuitpython_version = "{os.uname().version}"\r
circuitpython_board_id = "{board.board_id}"'''

def execute_digirom(rom, do_led=True):
	'''
	Execute the digirom and report results.
	'''
	try:
		controller.execute(rom)
		result = str(rom.result)
	except (CommandError, ReceiveError) as e:
		result = str(rom.result)
		if len(result) > 0:
			result += " "
		result += repr(e)
	if do_led:
		ui.led_bright()
	if serial == usb_cdc.data:
		print(result)
	else:
		mqtt.handle_result(result)
	if do_led:
		if "r:" in result or "Error" in result:
			time.sleep(0.2)
		else:
			time.sleep(0.05)
		ui.led_dim()
	return result

def process_new_digirom(command):
	'''
	Parse the command and show success/failure.

	Returns (command_type, output) where:
	command_type=    output=
	COMMAND_DIGIROM  DigiROM object
	COMMAND_ERROR    error string
	COMMAND_P        "[pause]"
	COMMAND_I        version info string
	'''
	try:
		digirom = dmcomm.protocol.parse_command(command)
	except CommandError as e:
		ui.beep_error()
		return (COMMAND_ERROR, repr(e))
	if digirom.signal_type is None:
		# It's an OtherCommand
		if digirom.op == "P":
			# silent
			return (COMMAND_P, "[pause]")
		elif digirom.op == "I":
			new_digirom_alert()
			return (COMMAND_I, get_version_info())
		else:
			ui.beep_error()
			return (COMMAND_ERROR, "NotImplementedError:op=" + digirom.op)
	# It's a DigiROM
	new_digirom_alert()
	return (COMMAND_DIGIROM, digirom)

def new_digirom_alert():
	'''
	Beep once and blink LED 3 times for new DigiROM.
	'''
	ui.beep_activate()
	for _ in range(3):
		ui.led_bright()
		time.sleep(0.05)
		ui.led_dim()
		time.sleep(0.05)

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
		ui.led_bright()
		if changed:
			ui.beep_activate()
	if status in (rt.STATUS_IDLE, rt.STATUS_WAIT):
		ui.led_dim()

def main_menu(play_startup_sound=True):
	'''
	Show the main menu.
	'''
	print("Main menu")
	if play_startup_sound:
		ui.beep_ready()
	options = []
	results = []
	if startup_mode == modes.MODE_DEV:
		options.append("* Dev Mode *")
		results.append(None)
	if board_config.WifiCls is not None:
		options.append("WiFi")
		results.append(run_wifi)
	options.extend(["Serial", "Punchbag", "Settings"])
	results.extend([run_serial, run_punchbag, run_settings])
	while True:
		menu_result = ui.menu(options, results, None)
		menu_result()

def menu_drive():
	'''
	Chosen Drive option from the menu.
	'''
	mode_change_reboot(modes.MODE_DRIVE)

def mode_change_reboot(mode):
	'''
	Reset with new mode.
	'''
	modes.set_mode(mode)
	ui.display_text("Rebooting...")
	time.sleep(0.5)
	microcontroller.reset()

def run_wifi():
	'''
	Do the normal WiFiCom things.
	'''
	# pylint: disable=too-many-branches,too-many-statements,too-many-locals

	if board_config.WifiCls is None:
		print("No WiFi specified in board_config; running serial")
		run_serial()
		return

	print("Running WiFi")
	gc.collect()
	print("Free memory before WiFi:", gc.mem_free())

	digirom = None
	rtb_was_active = False
	rtb_type_id = None
	rtb_last_ping = 0

	if not secrets_imported:
		if ui.has_display:
			print(secrets_error)
			failure_alert(secrets_error_display)
		else:
			raise ValueError(secrets_error)

	global done_wifi_before  # pylint: disable=global-statement
	if done_wifi_before:
		if startup_mode != modes.MODE_DEV:
			# Reconnect after reboot for wifi mode but not dev mode
			modes.set_mode(modes.MODE_WIFI)
		print("*** Soft reboot to reinitialize WiFi ***")
		ui.display_text("Soft reboot...")
		time.sleep(0.8)
		supervisor.reload()
	done_wifi_before = True

	# Connect to WiFi and MQTT
	ui.led_fast_blink()
	ui.display_text("Connecting to WiFi")
	def fail(message):
		if ui.has_display:
			failure_alert(message, reconnect=True)
		else:
			raise ConnectionError(message)
	wifi = board_config.WifiCls(**board_config.wifi_pins)
	mqtt_client = wifi.connect()
	if mqtt_client is None:
		fail("WiFi failed")
	ui.display_text("Connecting to MQTT")
	mqtt_connect = mqtt.connect_to_mqtt(mqtt_client)
	if mqtt_connect is False:
		fail("MQTT failed")
	ui.led_dim()
	ui.beep_ready()
	ui.display_text("WiFi\nHold C to exit")
	while not ui.is_c_pressed():
		time_start = time.monotonic()
		new_command = mqtt.get_subscribed_output()
		if new_command is not None:
			digirom = None
			(command_type, output) = process_new_digirom(new_command)
			if command_type == COMMAND_DIGIROM:
				digirom = output
			elif command_type in [COMMAND_ERROR, COMMAND_P, COMMAND_I]:
				print(output)
				mqtt.send_digirom_output(output)
		if mqtt.rtb_active:
			rtb_type_id_new = (mqtt.rtb_battle_type, mqtt.rtb_user_type)
			if not rtb_was_active or rtb_type_id_new != rtb_type_id:
				new_digirom_alert()
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
					print(mqtt.rtb_battle_type + " not implemented")
			rtb_was_active = True
			# Heartbeat approx every 10 seconds
			if time_start - rtb_last_ping > 10:
				mqtt.send_digirom_output("RTB")
				rtb_last_ping = time_start
			mqtt.loop()
			try:
				rtb.loop()
			except CommandError as e:
				print(repr(e))
		else:
			if rtb_was_active:
				ui.led_dim()
			rtb_was_active = False
			last_output = None
			if digirom is not None:
				result = execute_digirom(digirom)
				if len(result) >= 1:
					last_output = result

			# Send to MQTT topic (acts as a ping also)
			mqtt.send_digirom_output(last_output)

			while True:
				mqtt.loop()
				if mqtt.get_subscribed_output(False) is not None:
					break
				if time.monotonic() - time_start >= 5:
					break
				time.sleep(0.1)
	mqtt.quit_rtb()

def run_serial():
	'''
	Run in serial mode.
	'''
	print("Running serial")
	digirom = None
	ui.display_text("Serial\nHold C to exit")
	while not ui.is_c_pressed():
		time_start = time.monotonic()
		serial_str = serial_readline()
		if serial_str is not None:
			digirom = None
			(command_type, output) = process_new_digirom(serial_str)
			if command_type != COMMAND_I:
				print(f"got {len(serial_str)} bytes: {serial_str} -> ", end="")
			if command_type == COMMAND_DIGIROM:
				digirom = output
				print(f"{digirom.signal_type}{digirom.turn}-[{len(digirom)} packets]")
				time.sleep(1)
			elif command_type in [COMMAND_ERROR, COMMAND_P, COMMAND_I]:
				print(output)
		if digirom is not None:
			execute_digirom(digirom)
			seconds_passed = time.monotonic() - time_start
			if seconds_passed < 5:
				time.sleep(5 - seconds_passed)
		else:
			time.sleep(0.1)  # Just waiting for serial

def run_punchbag():
	'''
	Run in punchbag mode.
	'''
	print("Running punchbag")
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
		ui.beep_cancel()
		ui.display_text("Exiting\n(Release button)")
		while ui.is_c_pressed():
			pass

def run_settings():
	'''
	Run in settings mode.
	'''
	print("Running settings")
	settings_menu_configs = [
		("Version Info", display_info),
		("TOGGLE_SOUND", toggle_sound),
	]
	if startup_mode == modes.MODE_DEV:
		settings_menu_configs.append(("(Dev Mode no drive)", None))
		settings_menu_configs.append(("(Dev Mode no UF2)", None))
	else:
		settings_menu_configs.append(("Drive", menu_drive))
		settings_menu_configs.append(("UF2 Bootloader", reboot_uf2))
	names = [name for (name, value) in settings_menu_configs]
	values = [value for (name, value) in settings_menu_configs]
	toggle_sound_index = names.index("TOGGLE_SOUND")
	while True:
		names[toggle_sound_index] = "Sound: ON" if settings.is_sound_on() else "Sound: OFF"
		setting_value = ui.menu(names, values, "")
		if setting_value == "":
			return
		setting_value()

def display_info():
	'''
	Display settings info.
	'''
	print("Running display_info")
	version = version_info.version
	if len(version) <= 12:
		version = "WiFiCom: " + version
	info_text =  f"{version}\nCP: {os.uname().version.split()[0]}\n{board.board_id}"
	ui.display_text(info_text)
	while not ui.is_c_pressed():
		pass
	ui.beep_cancel()

def toggle_sound():
	'''
	Toggle sound on/off from the menu.
	'''
	if settings.is_sound_on():
		settings.set_sound_on(False)
		ui.sound_on = False
	else:
		settings.set_sound_on(True)
		ui.sound_on = True
		ui.beep_ready()

def reboot_uf2():
	'''
	Reboot into UF2 mode.
	'''
	ui.display_text("* UF2 Mode *\nCopy UF2 to RPI-RP2\nEject+reset to cancel")
	time.sleep(0.3)
	microcontroller.on_next_reset(microcontroller.RunMode.UF2)
	microcontroller.reset()

def run_drive():
	'''
	Run in drive mode.
	'''
	ui.display_text("* Drive Mode *\nEject when done\nThen hold C to exit")
	hold_c_to_reboot()

def run_unknown():
	'''
	Mode is unknown.
	'''
	ui.display_text("* First run? *\nEject when done\nThen hold C to reboot")
	hold_c_to_reboot()

def hold_c_to_reboot():
	'''
	Hold C to reboot.
	'''
	while True:
		while not ui.is_c_pressed():
			pass
		time_start = time.monotonic()
		while ui.is_c_pressed():
			if time.monotonic() - time_start > 3:
				mode_change_reboot(modes.MODE_MENU)

def failure_alert(message, hard_reset=False, reconnect=False):
	'''
	Alert on failure and allow restart.
	'''
	if startup_mode == modes.MODE_DEV:
		reconnect = False
	instructions = "A:Menu  B:Reconnect" if reconnect else "Press A to reboot"
	ui.led_off()
	ui.display_text(f"{message}\n{instructions}")
	ui.beep_failure()
	while True:
		if ui.is_a_pressed(True):
			# A for screen, C for screenless
			break
		if ui.is_b_pressed() and reconnect:
			modes.set_mode(modes.MODE_WIFI)
			break
		# Short blink every 2s
		if int(time.monotonic() * 10) % 20 == 0:
			ui.led_bright()
		else:
			ui.led_off()
	ui.led_off()
	ui.beep_activate()
	if hard_reset:
		ui.display_text("Rebooting...")
		time.sleep(0.5)
		microcontroller.reset()
	else:
		ui.display_text("Soft reboot...")
		time.sleep(0.8)
		supervisor.reload()

def rotate_log():
	'''
	Rotate log file if over LOG_MAX_SIZE.
	'''
	try:
		log_size = os.stat(LOG_FILENAME)[6]
	except OSError:
		print("No log file yet")
		return
	if log_size > LOG_MAX_SIZE:
		try:
			os.rename(LOG_FILENAME, LOG_FILENAME_OLD)
			print("Rotated log file")
		except OSError as e:
			print("Cannot rotate log file: " + repr(e))
	else:
		print("Log file is present")

def report_crash(crash_exception, connection_lost=False):
	'''
	Report crash which resulted in crash_exception.
	'''
	trace = "".join(traceback.format_exception(crash_exception))
	print(trace)
	message = "Connection lost" if connection_lost else "Crashed"
	rotate_log()
	random_number = random.randint(100, 999)
	try:
		with open(LOG_FILENAME, "a", encoding="utf-8") as f:
			f.write(f"Crash ID {random_number}:\r\n{trace}\r\n")
		print("Wrote log")
		message += f" #{random_number}"
		hard_reset = True
	except OSError as e:
		print("Cannot write log: " + repr(e))
		message += ",nolog"
		hard_reset = False
	failure_alert(message, hard_reset, connection_lost)

def main(led_pwm):
	'''
	WiFiCom main program.
	'''
	# pylint: disable=too-many-statements
	global startup_mode, controller, ui  # pylint: disable=global-statement

	serial.timeout = 1
	print("WiFiCom starting")

	gc.collect()
	print("Free memory at start:", gc.mem_free())

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

	startup_mode = modes.get_mode()
	mode_was_requested = modes.was_requested()
	print("Mode: " + modes.get_mode_str())
	modes.clear_request()
	if startup_mode != modes.MODE_DEV:
		supervisor.runtime.autoreload = False

	displayio.release_displays()
	ui = wificom.ui.UserInterface(**board_config.ui_pins, led_pwm=led_pwm)
	if ui.has_display:
		ui.sound_on = settings.is_sound_on(default=config["sound_on"])
	else:
		ui.sound_on = config["sound_on"]

	run_column = 0
	if not ui.has_display:
		run_column += 2
		print("Display not found: " + str(ui.display_error))
	if not mode_was_requested:
		run_column += 1
	print("Run column: " + str(run_column))
	branches = {
		# mode:              (ui requested, ui not req, no ui req,  no ui not req)
		modes.MODE_MENU:     (main_menu,    main_menu,  run_wifi,   run_wifi),
		modes.MODE_WIFI:     (run_wifi,     main_menu,  run_wifi,   run_wifi),
		modes.MODE_SERIAL:   (run_serial,   main_menu,  run_serial, run_serial),
		modes.MODE_PUNCHBAG: (run_punchbag, main_menu,  run_wifi,   run_wifi),  # last 2 unexpected
		modes.MODE_SETTINGS: (run_settings, main_menu,  run_wifi,   run_wifi),  # last 2 unexpected
		modes.MODE_DRIVE:    (run_drive,    run_drive,  run_wifi,   run_wifi),  # last 2 unexpected
		modes.MODE_DEV:      (main_menu,    main_menu,  run_wifi,   run_wifi),
		modes.MODE_UNKNOWN:  (run_unknown,  run_unknown,run_wifi,   run_wifi),
	}
	try:
		branches[startup_mode][run_column]()
		main_menu(False)
	except (ConnectionError, MMQTTException) as e:
		report_crash(e, True)
	except OSError as e:
		if e.errno == errno.EHOSTUNREACH:
			report_crash(e, True)
		else:
			report_crash(e)
	except Exception as e:  #pylint: disable=broad-except
		report_crash(e)
