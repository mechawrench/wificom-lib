'''
sound.py
Handles the PIO sound output.
'''

import array
import rp2pio

_PIO_FREQ = 1_000_000
_SILENT_DIV = 32

_PROGRAM = array.array("H",
	[32928, 24660, 40999, 44, 57345, 40999, 70, 57344, 40999, 73, 132, 0, 8076])
'''
start:
	pull
	out y 20   ; low 20 bits: duration in cycles
	mov x osr  ; high 12 bits: half-period in ticks (if 0, silent with period=32)
	jmp !x delay
high:
	set pins 1
	mov x osr
highloop:
	jmp x-- highloop
low:
	set pins 0
	mov x osr
lowloop:
	jmp x-- lowloop
	jmp y-- high
	jmp start
delay:
	jmp y-- delay [31]
'''

def _make_sound(note):
	(frequency, duration) = note
	if frequency == 0:
		half_period = 0
		duration_out = int(duration * _PIO_FREQ / _SILENT_DIV)
	else:
		half_period = int(_PIO_FREQ / frequency / 2)
		duration_out = int(duration * frequency)
	if half_period > 0xFFF:
		raise ValueError(f"Frequency {frequency} too small")
	if duration_out > 0xFFFFF:
		raise ValueError(f"Duration {duration} too large")
	return (half_period << 20) | duration_out

class PIOSound:
	'''
	Handles sound output via RP2040 PIO.
	'''
	def __init__(self, pin):
		self._state_machine = rp2pio.StateMachine(
			_PROGRAM,
			frequency=_PIO_FREQ,
			first_set_pin=pin,
			set_pin_count=1,
		)
		self.sound_on = True
	def deinit(self):
		'''
		Deinitialises the PIOSound and releases any hardware resources for reuse.
		'''
		self._state_machine.deinit()
	def play(self, notes):
		'''
		Play notes of [(frequency, duration)] in the background. frequency=0 for silence.
		'''
		if not self.sound_on:
			return
		to_send = [_make_sound(note) for note in notes]
		self._state_machine.background_write(array.array("L", to_send))
	def play_one(self, frequency, duration):
		'''
		Play one note in the background. frequency=0 for silence.
		'''
		self.play([(frequency, duration)])
