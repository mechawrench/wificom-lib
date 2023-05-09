'''
realtime.py
Handles real-time battle logic.
'''

import time
import dmcomm.protocol
from dmcomm import CommandError

STATUS_IDLE = 0
STATUS_WAIT = 1
STATUS_PUSH = 2

_MESSAGE_EXPIRY_TIME = 30

class RealTime:
	#pylint: disable=too-many-instance-attributes
	'''
	Abstract base class for real-time battles.

	Subclasses must implement:
	* `def message(self)` - the message to send to the other player.
	* `def matched(self, rom_str)` - True if the incoming digirom string
		fits the expected pattern, False otherwise.
	'''
	def __init__(self, execute_callback, send_callback, receive_callback, status_callback):
		self._execute_callback = execute_callback
		self._send_callback = send_callback
		self._receive_callback = receive_callback
		self._status_callback = status_callback
		self.time_start = None
		self.result = None
		self.status = STATUS_IDLE
		self.received_message = None
		self.received_digirom = None
		self.comm_attempts = 0  # for host only
	def execute(self, digirom, do_led=False):
		'''
		Execute digirom using the execute callback, and store result.
		'''
		self._execute_callback(digirom, do_led)
		self.result = digirom.result
	def modify_received_digirom(self):
		'''
		Called on received digirom.
		Changes nothing by default. Can be overridden by subclasses as required.
		Returns True if OK, False if error (additional checks can be added here).
		'''
		return True
	def send_message(self):
		'''
		Send message to the other player, using the send callback,
		and `message` function as defined by subclass.
		'''
		self._send_callback(self.message())
	def receive_message(self):
		'''
		Receive and store message from the other player if there is one,
		using the receive callback.

		Expire previous stored message if needed, or overwrite if there is a new one.
		'''
		if self.received_message is not None:
			(timestamp, _) = self.received_message
			if time.monotonic() - timestamp > _MESSAGE_EXPIRY_TIME:
				self.received_message = None
		message = self._receive_callback()
		if message is not None:
			self.received_message = (time.monotonic(), message)
	def receive_digirom(self):
		'''
		Receive digirom from the other player if there is one, from the queued message.
		Validate with `matched` function as defined by subclass.
		Parse digirom, and modify if defined in subclass.
		`self.received_digirom` becomes the new digirom if there is one, None if there is not.
		Raises `CommandError` if `matched` is False, or for other errors.
		'''
		self.received_digirom = None
		if self.received_message is None:
			return
		(_, message) = self.received_message
		self.received_message = None
		if not self.matched(message):
			raise CommandError("Unexpected RTB message type: " + str(message))
		self.received_digirom = dmcomm.protocol.parse_command(message)
		if not self.modify_received_digirom():
			self.received_digirom = None
			raise CommandError("Unexpected RTB message contents: " + str(message))
	def update_status(self, status):
		'''
		Report current status to the status callback and save it here.
		'''
		self._status_callback(status, status != self.status)
		self.status = status

class RealTimeHost(RealTime):
	'''
	Abstract class for real-time host.

	Subclasses must implement:
	* property `scan_str` - the digirom string to use for scanning.
	* `def scan_successful(self)` - True if enough data was collected from the toy
		using the scan digirom, False otherwise.
	* property `wait_min` - the minimum time to wait in seconds before attempting
		to connect to the toy for the second time.
	* property `wait_max` - the maximum time to wait for a reply from the other player.
	* property `max_attempts` - the maximum number of attempts at the second
		round of communication.
	* property `retry_delay` - the wait time in seconds before retrying.
	* `def comm_successful(self)` - True if the second interaction with the toy
		was successful, False otherwise.

	(Items marked "property" here can also be class attributes.)
	'''
	def loop(self):
		'''
		Update state machine. Should be called repeatedly.
		'''
		self.receive_message()  #but not digirom right now
		if self.received_digirom is not None:
			if time.monotonic() - self.time_start >= self.retry_delay:
				self._attempt_second_comm()
		elif self.time_start is None:
			self.update_status(STATUS_PUSH)
			digirom = dmcomm.protocol.parse_command(self.scan_str)
			self.execute(digirom)
			if self.scan_successful():
				self.send_message()
				self.time_start = time.monotonic()
				self.update_status(STATUS_WAIT)
		elif time.monotonic() - self.time_start < self.wait_min:
			self.update_status(STATUS_WAIT)
		elif time.monotonic() - self.time_start > self.wait_max:
			self.time_start = None
		else:
			self.update_status(STATUS_WAIT)
			self.receive_digirom()
			if self.received_digirom is not None:
				self.comm_attempts = 0
				self._attempt_second_comm()
	def _attempt_second_comm(self):
		self.execute(self.received_digirom, True)
		if self.comm_successful():
			self.received_digirom = None
			self.time_start = None
		else:
			self.time_start = time.monotonic()
			self.comm_attempts += 1
			if self.comm_attempts >= self.max_attempts:
				self.received_digirom = None
				self.time_start = None

class RealTimeGuest(RealTime):
	'''
	Abstract class for real-time guest.

	Subclasses must implement:

	* `def comm_successful(self)` - True if the interaction with the toy
		was successful, False otherwise.
	'''
	def loop(self):
		'''
		Update state machine. Should be called repeatedly.
		'''
		self.receive_message()
		self.receive_digirom()
		if self.received_digirom is not None:
			self.update_status(STATUS_PUSH)
			self.execute(self.received_digirom)
			self.update_status(STATUS_WAIT)
			if self.comm_successful():
				self.send_message()

class RealTimeGuestTalis(RealTimeHost):
	'''
	Real-time guest for Legendz battle.
	Based on host because this battle type is almost symmetrical.
	'''
	scan_str = "LT2"  #: RealTimeHost interface
	wait_min = 9      #: RealTimeHost interface
	wait_max = 25     #: RealTimeHost interface
	max_attempts = 4  #: RealTimeHost interface
	retry_delay = 5   #: RealTimeHost interface
	def scan_successful(self):
		'''RealTimeHost interface'''
		return len(self.result) == 1 and len(self.result[0].data) >= 20
	def message(self):
		'''RealTime interface'''
		return "LT1-" + str(self.result[0])[2:] + "-AA590003" * 3
	def matched(self, rom_str):
		'''RealTime interface'''
		return rom_str.startswith("LT1-")
	def comm_successful(self):
		'''RealTimeHost interface'''
		return len(self.result) >= 4

class RealTimeHostTalis(RealTimeGuestTalis):
	'''
	Real-time host for Legendz battle.
	Based on guest (which uses host interface) because this battle type is almost symmetrical.
	'''
	def modify_received_digirom(self):
		'''RealTime interface'''
		if len(self.received_digirom) == 0:
			return False
		sent_data = self.result[0].data  # we already know this is long enough
		rom_data = self.received_digirom[0].data
		if len(rom_data) < 20:
			return False
		rom_data[14] = sent_data[14] #random number that only Pod copies?
		rom_data[15] = sent_data[15] #session ID
		rom_data[17] = sent_data[17] #terrain
		rom_data[-1] = 0
		rom_data[-1] = sum(rom_data) % 256
		return True

class RealTimeHostPenXBattle(RealTimeHost):
	'''Real-time host for PenX battle.'''
	scan_str = "X2-0069-2169-8009"  #: RealTimeHost interface
	wait_min = 0      #: RealTimeHost interface
	wait_max = 7      #: RealTimeHost interface
	max_attempts = 3  #: RealTimeHost interface
	retry_delay = 3   #: RealTimeHost interface
	def scan_successful(self):
		'''RealTimeHost interface'''
		return len(self.result) == 7 and self.result[6].data is not None
	def message(self):
		'''RealTime interface'''
		# pylint: disable=consider-using-f-string
		return "X2-{0}-{1}-{2}-@4^3^F9".format(
			str(self.result[0])[2:],
			str(self.result[2])[2:],
			str(self.result[4])[2:],
		)
	def matched(self, rom_str):
		'''RealTime interface'''
		return rom_str.startswith("X1-")
	def comm_successful(self):
		'''RealTimeHost interface'''
		return len(self.result) == 8

class RealTimeGuestPenXBattle(RealTimeGuest):
	'''Real-time guest for PenX battle.'''
	def matched(self, rom_str):
		'''RealTime interface'''
		return rom_str.startswith("X2-")
	def comm_successful(self):
		'''RealTimeGuest interface'''
		return len(self.result) == 9
	def message(self):
		'''RealTime interface'''
		# pylint: disable=consider-using-f-string
		return "X1-{0}-{1}-{2}-{3}".format(
			str(self.result[0])[2:],
			str(self.result[2])[2:],
			str(self.result[4])[2:],
			str(self.result[6])[2:],
		)
