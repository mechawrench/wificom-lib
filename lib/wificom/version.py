'''
version.py
Handles the version info (from version_info.py and system)
'''

import collections
import os
import board
import version_info

_has_display = None
def set_display(value):
	'''
	Set whether we have a display.
	'''
	global _has_display  #pylint:disable=global-statement
	_has_display = value

def dictionary():
	'''
	Convert version info to an OrderedDict.
	'''
	result = collections.OrderedDict()
	result["name"] = version_info.name
	result["version"] = version_info.version
	result["circuitpython_version"] = os.uname().version
	result["circuitpython_board_id"] = board.board_id
	result["has_display"] = _has_display
	return result

def _toml_value(value):
	if value is True:
		return 'true'
	elif value is False:
		return 'false'
	else:
		return f'"{value}"'

def toml():
	'''
	Convert version info to a TOML string.
	'''
	dic = dictionary()
	items = [f'{key} = {_toml_value(dic[key])}' for key in dic]
	return "\r\n".join(items)

def onscreen():
	'''
	Create version info for display on the screen.
	'''
	version = version_info.version
	if len(version) <= 12:
		version = "WiFiCom: " + version
	return f"{version}\nCP: {os.uname().version.split()[0]}\n{board.board_id}"
