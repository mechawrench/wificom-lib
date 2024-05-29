'''
punchbag.py
Handles the DigiROM tree.
'''

def count_tabs(line):
	'''
	Count leading tabs on line. None for comment or no content.
	'''
	tabs = 0
	for character in line:
		if character == "\t":
			tabs += 1
		elif character in "#\r\n":
			return None
		elif character == " ":
			raise ValueError("Tabs are required")
		else:
			return tabs
	return None

class DigiROM_Node:  #pylint:disable=invalid-name
	'''
	Node for the DigiROM tree.
	'''
	def __init__(self, text, pos):
		self.text = text
		self.pos = pos
		self.leaf_pos = []  # List for internal use, becomes int or None before handing back

class DigiROM_Tree:  #pylint:disable=invalid-name
	'''
	Parser for the DigiROM tree.
	'''
	def __init__(self, file_obj):
		self._file_obj = file_obj
		self._menu_path = []
	def depth(self):
		'''How many steps into the menu.'''
		return len(self._menu_path)
	def children(self):
		'''Options at current point, as [DigiROM_Node].'''
		# pylint: disable=too-many-branches
		result = []
		f = self._file_obj
		start_tabs = len(self._menu_path) - 1
		if start_tabs == -1:
			pos = 0
			f.seek(pos)
		else:
			pos = self._menu_path[-1]
			f.seek(pos)
			f.readline()
		prev_tabs = start_tabs
		tabs = None
		while True:
			if tabs is not None:
				prev_tabs = tabs
			pos = f.tell()
			line = f.readline()
			if line == "":
				# EOF
				break
			tabs = count_tabs(line)
			if tabs is None:
				continue
			if tabs <= start_tabs:
				break
			tab_step = tabs - prev_tabs
			if tab_step == 0 or tab_step > 1:
				raise ValueError("Layout error")
			if tabs == start_tabs + 1:
				result.append(DigiROM_Node(line.strip(), pos))
			elif tab_step == 1:
				if result[-1].leaf_pos is not None:
					result[-1].leaf_pos.append(pos)
			else:
				# tab_step < 0 and tabs > start_tabs + 1
				result[-1].leaf_pos = None
		for item in result:
			if item.leaf_pos is not None and len(item.leaf_pos) == 1:
				item.leaf_pos = item.leaf_pos[0]
			else:
				item.leaf_pos = None
		return result
	def digirom(self, node):
		'''Get the digirom at the chosen node, or None if not existing.'''
		if node.leaf_pos is None:
			return None
		f = self._file_obj
		f.seek(node.leaf_pos)
		return f.readline().strip()
	def pick(self, node):
		'''Move to the menu option at the chosen node.'''
		if node.leaf_pos is not None:
			raise ValueError("No menu here")
		self._menu_path.append(node.pos)
	def back(self):
		'''Step back one menu level. Ignored if at the root.'''
		if len(self._menu_path) > 0:
			self._menu_path.pop()
