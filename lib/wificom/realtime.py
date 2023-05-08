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
STATUS_PUSH_SYNC = 3

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
		self.received_message = None  # for host only
		self.comm_attempts = 0  # for host only
	def execute(self, rom_str):
		'''
		Parse rom_str, modify if defined in subclass,
		execute digirom using the execute callback, and store result.
		'''
		digirom = dmcomm.protocol.parse_command(rom_str)
		self.modify(digirom)
		self._execute_callback(digirom, False)
		self.result = digirom.result
	def modify(self, digirom):
		'''
		Called before executing digirom.
		Does nothing by default. Can be overridden by subclasses as required.
		'''
	def send_message(self):
		'''
		Send message to the other player, using the send callback,
		and `message` function as defined by subclass.
		'''
		self._send_callback(self.message())
	def receive_message(self):
		'''
		Receive message from the other player if there is one, using the receive callback.
		Validate with `matched` function as defined by subclass.
		Returns message if there is one, None if there is not.
		Raises `CommandError` if `matched` is False.
		'''
		message = self._receive_callback()
		if message is None:
			return None
		if not self.matched(message):
			raise CommandError("Unexpected message type: " + str(message))
		return message
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
	* property `scan_status` - the status value to report when starting to scan.
	* property `scan_str` - the digirom string to use for scanning.
	* `def scan_successful(self)` - True if enough data was collected from the toy
		using the scan digirom, False otherwise.
	* property `wait_min` - the minimum time to wait in seconds before attempting
		to connect to the toy for the second time.
	* property `wait_max` - the maximum time to wait for a reply from the other player.
	'''
	@property
	def max_attempts(self):
		'''The maximum number of attempts at the second round of communication.'''
		return 1
	@property
	def retry_delay(self):
		'''The wait time in seconds before retrying.'''
		return 1
	def comm_successful(self):
		'''
		True if the second interaction with the toy was successful
		or we are not doing retries; False otherwise.
		'''
		return True
	def loop(self):
		'''
		Update state machine. Should be called repeatedly.
		'''
		if self.received_message is not None:
			if time.monotonic() - self.time_start >= self.retry_delay:
				self._attempt_second_comm()
		elif self.time_start is None:
			self.update_status(self.scan_status)
			self.execute(self.scan_str)
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
			self.received_message = self.receive_message()
			if self.received_message is not None:
				self.comm_attempts = 0
				self._attempt_second_comm()
	def _attempt_second_comm(self):
		self.execute(self.received_message)
		if self.comm_successful():
			self.received_message = None
			self.time_start = None
		else:
			self.time_start = time.monotonic()
			self.comm_attempts += 1
			if self.comm_attempts >= self.max_attempts:
				self.received_message = None
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
		message = self.receive_message()
		if message is not None:
			self.update_status(STATUS_PUSH)
			self.execute(message)
			self.update_status(STATUS_WAIT)
			if self.comm_successful():
				self.send_message()

class RealTimeGuestTalis(RealTimeHost):
	'''
	Real-time guest for Legendz battle.
	Based on host because this battle type is almost symmetrical.
	'''
	@property
	def scan_status(self):
		'''RealTimeHost interface'''
		return STATUS_PUSH_SYNC
	@property
	def scan_str(self):
		'''RealTimeHost interface'''
		return "LT2"
	def scan_successful(self):
		'''RealTimeHost interface'''
		return len(self.result) == 1 and len(self.result[0].data) >= 20
	def message(self):
		'''RealTime interface'''
		return "LT1-" + str(self.result[0])[2:] + "-AA590003" * 3
	@property
	def wait_min(self):
		'''RealTimeHost interface'''
		return 9
	@property
	def wait_max(self):
		'''RealTimeHost interface'''
		return 15
	def matched(self, rom_str):
		'''RealTime interface'''
		return rom_str.startswith("LT1-")
	@property
	def max_attempts(self):
		'''RealTimeHost interface'''
		return 4
	@property
	def retry_delay(self):
		'''RealTimeHost interface'''
		return 5
	def comm_successful(self):
		'''RealTimeHost interface'''
		return len(self.result) >= 6

class RealTimeHostTalis(RealTimeGuestTalis):
	'''
	Real-time host for Legendz battle.
	Based on guest (which uses host interface) because this battle type is almost symmetrical.
	'''
	def modify(self, digirom):
		'''RealTime interface'''
		if len(digirom) == 0:
			return
		sent_data = self.result[0].data
		rom_data = digirom[0].data
		rom_data[14] = sent_data[14] #random number that only Pod copies?
		rom_data[15] = sent_data[15] #session ID
		rom_data[17] = sent_data[17] #terrain
		rom_data[-1] = 0
		rom_data[-1] = sum(rom_data) % 256

class RealTimeHostPenXBattle(RealTimeHost):
	'''Real-time host for PenX battle.'''
	@property
	def scan_status(self):
		'''RealTimeHost interface'''
		return STATUS_PUSH
	@property
	def scan_str(self):
		'''RealTimeHost interface'''
		return "X2-0069-2169-8009"
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
	@property
	def wait_min(self):
		'''RealTimeHost interface'''
		return 0
	@property
	def wait_max(self):
		'''RealTimeHost interface'''
		return 7
	def matched(self, rom_str):
		'''RealTime interface'''
		return rom_str.startswith("X1-")

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
