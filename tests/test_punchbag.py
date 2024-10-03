'''Tests for punchbag module (valid file).'''

import os
import pytest
import target_paths
from wificom import punchbag

class tree_wrapper:
	def __init__(self, tree):
		self.tree = tree
	def child_by_text(self, text):
		for child in self.tree.children():
			if child.text == text:
				return child
		raise KeyError(text)
	def pick(self, text):
		child = self.child_by_text(text)
		self.tree.pick(child)
	def digirom(self, text):
		child = self.child_by_text(text)
		return self.tree.digirom(child)

@pytest.fixture
def data():
	data_file = open(os.path.join(target_paths.punchbag_data, "valid.txt"), encoding="UTF-8")
	tree = punchbag.DigiROM_Tree(data_file)
	wrapper = tree_wrapper(tree)
	yield wrapper
	data_file.close()

def test_dmog_you_win(data):
	data.pick("Classic Punchbags")
	assert data.digirom("DMOG you win") == "V1-FC03-FD02"
