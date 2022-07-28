# This file is part of the DMComm project by BladeSabre. License: MIT.
# WiFiCom on Arduino Nano RP2040 Connect, with BladeSabre's pin assignments.

import board
import busio
import digitalio
import time
import usb_cdc

from dmcomm import CommandError, ReceiveError
import dmcomm.hardware as hw
import dmcomm.protocol
import dmcomm.protocol.auto
from wificom.hardware.RP2040ArduinoNanoConnect import RP2040ArduinoNanoConnect, esp
from wificom.mqtt.platformio import PlatformIO

pins_extra_power = [
	(board.D6, False), (board.D7, True),
	(board.D8, False),
	(board.D11, False), (board.D12, True),
]
outputs_extra_power = []
for (pin, value) in pins_extra_power:
	output = digitalio.DigitalInOut(pin)
	output.direction = digitalio.Direction.OUTPUT
	output.value = value
	outputs_extra_power.append(output)

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

controller = hw.Controller()
controller.register(hw.ProngOutput(board.A0, board.A2))
controller.register(hw.ProngInput(board.A3))
controller.register(hw.InfraredOutput(board.D9))
controller.register(hw.InfraredInputModulated(board.D10))
controller.register(hw.InfraredInputRaw(board.D5))
controller.register(hw.TalisInputOutput(board.D4))

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

last_output = None

serial.timeout = 1
def serial_print(s):
	serial.write(s.encode("utf-8"))
serial_print("dmcomm-python starting\n")

# Connect to WiFi
RP2040ArduinoNanoConnect.connectToSsid()

# Connect to MQTT
PlatformIO.connect_to_mqtt(esp) 

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
	replacementDigirom = PlatformIO.getSubscribedOutput()
	if(replacementDigirom is not None):
		print("New digirom:", replacementDigirom)
	last_output = None
	if replacementDigirom is not None:
		digirom = dmcomm.protocol.parse_command(replacementDigirom)
	if digirom is not None:
		error = ""
		result_end = "\n"
		try:
			controller.execute(digirom)
		except (CommandError, ReceiveError) as e:
			error = repr(e)
			result_end = " "
		led.value = True
		serial_print(str(digirom.result) + result_end)
		if error != "":
			serial_print(error + "\n")
		if len(str(digirom.result)) >= 1:
			last_output = str(digirom.result)
		led.value = False

	# Send to MQTT topic (acts as a ping also)
	PlatformIO.on_digirom_output(last_output)

	# seconds_passed = t
	while (time.monotonic() - time_start) < 5:
		PlatformIO.loop()
		if (PlatformIO.getSubscribedOutput(False) != None):
			break
		time.sleep(0.1)
