'''
This file is part of the DMComm project by BladeSabre. License: MIT.
WiFiCom on supported boards (see board_config.py).
'''
import time
import board
# import busio
import digitalio
import usb_cdc

from dmcomm import CommandError, ReceiveError
import dmcomm.hardware as hw
import dmcomm.protocol
import dmcomm.protocol.auto
import dmcomm.protocol.realtime as rt
from wificom.hardware.wifi import Wifi
from wificom.mqtt import platform_io
import board_config

outputs_extra_power = []
for (pin, value) in board_config.extra_power_pins:
	output = digitalio.DigitalInOut(pin)
	output.direction = digitalio.Direction.OUTPUT
	output.value = value
	outputs_extra_power.append(output)

controller = hw.Controller()
for pin_description in board_config.controller_pins:
	controller.register(pin_description)

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

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
	platform_io_obj.on_rtb_digirom_output(message)
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
	led.value = status == rt.STATUS_PUSH
rtb_was_active = False

# Serial port selection
if usb_cdc.data is not None:
	serial = usb_cdc.data
else:
	serial = usb_cdc.console
#serial = usb_cdc.console  # same as REPL
#serial = usb_cdc.data  # alternate USB serial
#serial = busio.UART(board.TX, board.RX)  # for external UART

# Choose an initial digirom / auto-responder here:
digirom = None  # disable
#digirom = dmcomm.protocol.auto.AutoResponderVX("V")  # 2-prong auto-responder
#digirom = dmcomm.protocol.auto.AutoResponderVX("X")  # 3-prong auto-responder
#digirom = dmcomm.protocol.parse_command("IC2-0007-^0^207-0007-@400F" + "-0000" * 16)  # Twin any
# ...or use your own digirom, as for the Twin above.

serial.timeout = 1

def serial_print(contents):
	'''
	Print output to the serial console
	'''
	serial.write(contents.encode("utf-8"))

serial_print("dmcomm-python starting\n")

# Connect to WiFi
wifi = Wifi(**board_config.wifi_pins)
esp = wifi.connect()

# Connect to MQTT
platform_io_obj = platform_io.PlatformIO()
platform_io_obj.connect_to_mqtt(esp)

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
	if not platform_io_obj.get_is_output_hidden():
		serial_print(str(rom.result) + result_end)
	else:
		serial_print("Received output, check the App\n")
	if error != "":
		serial_print(error + "\n")

while True:
	time_start = time.monotonic()
	if serial.in_waiting != 0:
		digirom = None
		serial_bytes = serial.readline()
		serial_str = serial_bytes.decode("ascii", "ignore")
		# readline only accepts "\n" but we can receive "\r" after timeout
		if serial_str[-1] not in ["\r", "\n"]:
			serial_print("too slow\n")
			continue
		serial_str = serial_str.strip()
		serial_str = serial_str.strip("\0")
		serial_print(f"got {len(serial_str)} bytes: {serial_str} -> ")
		try:
			command = dmcomm.protocol.parse_command(serial_str)
			if hasattr(command, "op"):
				# It's an OtherCommand
				raise NotImplementedError("op=" + command.op)
			digirom = command
			serial_print(f"{digirom.physical}{digirom.turn}-[{len(digirom)} packets]\n")
		except (CommandError, NotImplementedError) as e:
			serial_print(repr(e) + "\n")
		time.sleep(1)
	replacementDigirom = platform_io_obj.get_subscribed_output()
	if replacementDigirom is not None:
		if not platform_io_obj.get_is_output_hidden():
			print("New digirom:", replacementDigirom)
		else:
			serial_print("Received digirom input, check the App\n")

	if replacementDigirom is not None:
		digirom = dmcomm.protocol.parse_command(replacementDigirom)

	if platform_io_obj.get_is_rtb_active():
		if not rtb_was_active:
			rtb_type_id = (platform_io.rtb_battle_type, platform_io.rtb_user_type)
			if rtb_type_id in rtb_types:
				rtb = rtb_types[rtb_type_id](
					execute_digirom,
					rtb_send_callback,
					rtb_receive_callback,
					rtb_status_callback,
				)
			else:
				serial_print(platform_io.rtb_battle_type + " not implemented\n")
		rtb_was_active = True
		platform_io_obj.loop()
		rtb.loop()
	else:
		if rtb_was_active:
			led.value = False
		rtb_was_active = False
		last_output = None
		if digirom is not None:
			execute_digirom(digirom)
			if len(str(digirom.result)) >= 1:
				last_output = str(digirom.result)

		# Send to MQTT topic (acts as a ping also)
		platform_io_obj.on_digirom_output(last_output)

		while (time.monotonic() - time_start) < 5:
			platform_io_obj.loop()
			if platform_io_obj.get_subscribed_output(False) is not None:
				break
			time.sleep(0.1)
