'''Tests for punchbag module (error cases).

Scans files with names starting with "L" in punchbag_data directory,
and expects ValueError with message starting with "filename up to first underscore".
'''

import os
import pytest
import target_paths
from wificom import punchbag

def pytest_generate_tests(metafunc):
	'''Collect filenames starting with "L" in punchbag_data.'''
	names = [name for name in os.listdir(target_paths.punchbag_data) if name.startswith("L")]
	metafunc.parametrize("filename", names)

def test_error(filename):
	'''Test that the specified file causes ValueError mentioning the expected line.'''
	line_label_target = filename.split("_")[0] + ":*"
	with open(os.path.join(target_paths.punchbag_data, filename), encoding="UTF-8") as data_file:
		tree = punchbag.DigiROM_Tree(data_file)
		with pytest.raises(ValueError, match=line_label_target):
			tree.children()
