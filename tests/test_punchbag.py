'''Tests for punchbag module (valid file).'''

import os
import pytest
import target_paths
from wificom import punchbag

class TreeWrapper:
	'''Wrap digiroms tree with helper functions for testing.'''
	def __init__(self, tree):
		self.tree = tree
	def child_by_text(self, text):
		'''Get the child specified by `text`.'''
		for child in self.tree.children():
			if child.text == text:
				return child
		raise KeyError(text)
	def pick(self, text):
		'''Move to the child specified by `text`.'''
		child = self.child_by_text(text)
		self.tree.pick(child)
	def digirom(self, text):
		'''Get the digirom specified by `text` from the current node.'''
		child = self.child_by_text(text)
		return self.tree.digirom(child)

@pytest.fixture
def data():
	'''Set up data from "valid.txt".'''
	#pylint: disable=consider-using-with
	data_file = open(os.path.join(target_paths.punchbag_data, "valid.txt"), encoding="UTF-8")
	tree = punchbag.DigiROM_Tree(data_file)
	wrapper = TreeWrapper(tree)
	yield wrapper
	data_file.close()

#pylint: disable=redefined-outer-name,missing-function-docstring

def test_dmog_you_win(data):
	data.pick("Classic Punchbags")
	assert data.digirom("DMOG you win") == "V1-FC03-FD02"
