'''
settings.py
Handles the stored settings.
'''

import microcontroller

INDEX_SOUND_ON_OFF = 0
VALUE_SOUND_OFF = 0
VALUE_SOUND_ON = 1

def is_sound_on(default=True):
	'''
	Return True if sound is on, False otherwise.
	Set to default if not recognised.
	'''
	value = microcontroller.nvm[INDEX_SOUND_ON_OFF]
	if value == VALUE_SOUND_OFF:
		return False
	if value == VALUE_SOUND_ON:
		return True
	set_sound_on(default)
	return default

def set_sound_on(is_on):
	'''
	Turn sound on if True, off otherwise.
	'''
	value = VALUE_SOUND_ON if is_on else VALUE_SOUND_OFF
	microcontroller.nvm[INDEX_SOUND_ON_OFF] = value
	print("Wrote NVM sound_on =", is_on)
