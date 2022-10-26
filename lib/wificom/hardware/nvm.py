'''
nvm.py
Handles the non-volatile storage.
'''

import microcontroller

MAGIC = "wificom02"
LENGTH = len(MAGIC) + 1

MODE_MENU = "m"
MODE_WIFI = "w"
MODE_SERIAL = "s"
MODE_PUNCHBAG = "p"
MODE_DRIVE = "d"
MODE_DEV = "*"

_MODES = "mwspd*"

def _nvm_str():
	the_bytes = microcontroller.nvm[0:LENGTH]
	try:
		return the_bytes.decode("ascii")
	except UnicodeError:
		return "?"

def get_mode():
	'''
	Return the currently-set mode, defaulting to MODE_MENU.
	'''
	nvm_str = _nvm_str()
	mode = nvm_str[-1]
	if nvm_str.startswith(MAGIC) and mode in _MODES:
		return mode
	return MODE_MENU

def set_mode(mode):
	'''
	Set a new mode. Return True if NVM was changed, False otherwise.
	'''
	if mode not in _MODES:
		raise ValueError(str(mode) + " not a mode")
	new_nvm_str = MAGIC + mode
	if new_nvm_str == _nvm_str():
		return False
	microcontroller.nvm[0:LENGTH] = bytes(new_nvm_str, "ascii")
	return True
