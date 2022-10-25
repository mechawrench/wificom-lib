'''
nvm.py
Handles the non-volatile storage.
'''

import microcontroller

MAGIC = "wificom1"
LENGTH = len(magic) + 1

MODE_WIFI = "w"
MODE_SERIAL = "s"
MODE_PUNCHBAG = "p"
MODE_DRIVE = "d"

_MODES = "wspd"

def _nvm_str():
	return str(microcontroller.nvm[0:LENGTH])

def get_mode():
	nvm_str = _nvm_str()
	mode = nvm_str[-1]
	if nvm_str.startswith(MAGIC) and mode in _MODES:
		return mode
	else:
		return MODE_WIFI

def set_mode(mode):
	if mode not in _MODES:
		raise ValueError(str(mode) + " not a mode")
	new_nvm_str = MAGIC + mode
	if new_nvm_str == _nvm_str():
		return False
	else:
		microcontroller.nvm[0:LENGTH] = bytes(new_nvm_str)
		return True
