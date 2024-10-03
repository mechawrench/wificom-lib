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

#pylint: disable=redefined-outer-name

def test_dmog_you_win(data):
	'''First digirom (has trailing whitespace)'''
	data.pick("Classic Punchbags")
	assert data.digirom("DMOG you win") == "V1-FC03-FD02"

def test_dmog_you_lose(data):
	'''Fourth digirom'''
	data.pick("Classic Punchbags")
	assert data.digirom("PenOG you lose") == "V1-211F-000F-09FF-EABF"

def test_make_it_longer(data):
	'''Deeper in the tree'''
	data.pick("Classic Punchbags")
	data.pick("Make")
	data.pick("It")
	data.pick("Longer")
	assert data.digirom("PenX you win") == "X1-0159-4379-2E49-@4009"

def test_dscan_curebox(data):
	'''Second section'''
	data.pick("Infrared")
	data.pick("D-Scanner")
	assert data.digirom("Cure Box barcode") == "BC1-0200000002711"

def test_dscan_supercharge(data):
	'''Blank lines'''
	data.pick("Infrared")
	data.pick("D-Scanner")
	assert data.digirom("SuperCharge barcode") == "BC1-0200000002511"

def test_ic(data):
	'''Stepping out; weirdly indented comment'''
	data.pick("Infrared")
	assert data.digirom("iC you win") == "IC1-C067-4257-0197-0007-@F007"

def test_dl(data):
	'''Top-level digirom at end'''
	assert data.digirom("Data Link 2000pt") == "DL2-1301002000AA>>+?-1301002000AA>>+?"
