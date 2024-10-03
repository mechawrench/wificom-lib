'''
punchbag.py
Handles the DigiROM tree.
'''

NO_CONTENT = -1
LEADING_SPACE = -2

def count_tabs(line):
	'''
	Count leading tabs on line.
	NO_CONTENT for comment, blank line, or tabs only.
	LEADING_SPACE if a space was found before text begins.
	'''
	tabs = 0
	for character in line:
		if character == "\t":
			tabs += 1
		elif character in "#\r\n":
			return NO_CONTENT
		elif character == " ":
			return LEADING_SPACE
		else:
			return tabs
	return NO_CONTENT

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
		tabs = NO_CONTENT
		while True:
			if tabs != NO_CONTENT:
				prev_tabs = tabs
			pos = f.tell()
			line = f.readline()
			if line == "":
				# EOF
				if prev_tabs == 0:
					self._error("Layout error", pos)
				break
			tabs = count_tabs(line)
			if tabs == LEADING_SPACE:
				self._error("Tabs required", pos)
			if tabs == NO_CONTENT:
				continue
			if tabs <= start_tabs:
				break
			tab_step = tabs - prev_tabs
			if tab_step == 0 or tab_step > 1:
				self._error("Layout error", pos)
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
			self._error("No menu here", node.pos)
		self._menu_path.append(node.pos)
	def back(self):
		'''Step back one menu level. Ignored if at the root.'''
		if len(self._menu_path) > 0:
			self._menu_path.pop()
	def _error(self, message, pos):
		'''Raise ValueError with start-of-line seek position converted to line number.'''
		f = self._file_obj
		f.seek(0)
		line_number = 0
		while f.tell() <= pos and f.readline() != "":
			line_number += 1
		raise ValueError(f"L{line_number}: {message}")
