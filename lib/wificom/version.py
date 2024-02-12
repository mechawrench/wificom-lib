'''
version.py
Handles the version info (from version_info.py and system)
'''

import collections
import os
import board
import version_info

def dictionary():
	'''
	Convert version info to an OrderedDict.
	'''
	result = collections.OrderedDict()
	result["name"] = version_info.name
	result["version"] = version_info.version
	result["circuitpython_version"] = os.uname().version
	result["circuitpython_board_id"] = board.board_id
	return result

def toml():
	'''
	Convert version info to a TOML string.
	'''
	dic = dictionary()
	items = [f'{key} = "{dic[key]}"' for key in dic]
	return "\r\n".join(items)

def onscreen():
	'''
	Create version info for display on the screen.
	'''
	version = version_info.version
	if len(version) <= 12:
		version = "WiFiCom: " + version
	return f"{version}\nCP: {os.uname().version.split()[0]}\n{board.board_id}"
