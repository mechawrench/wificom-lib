'''Tests for punchbag module.'''

import os
import unittest
from wificom import punchbag

data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "punchbag_data")

class TestValidData(unittest.TestCase):
	def setUp(self):
		self.data_file = open(os.path.join(data_dir, "valid.txt"), encoding="UTF-8")
		self.tree = punchbag.DigiROM_Tree(self.data_file)
	def tearDown(self):
		self.data_file.close()
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
	def test_dmog_you_win(self):
		self.pick("Classic Punchbags")
		self.assertEqual(self.digirom("DMOG you win"), "V1-FC03-FD02")

class TestInvalidData(unittest.TestCase):
	def test_error(self):
		for filename in os.listdir(data_dir):
			if filename.startswith("L"):
				with self.subTest(filename=filename):
					line_label_target = filename.split("_")[0] + ":*"
					with open(os.path.join(data_dir, filename), encoding="UTF-8") as data_file:
						tree = punchbag.DigiROM_Tree(data_file)
						self.assertRaisesRegex(ValueError, line_label_target, tree.children)
