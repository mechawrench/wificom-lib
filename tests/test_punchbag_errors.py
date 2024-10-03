'''Tests for punchbag module (error cases).'''

import os
import pytest
import target_paths
from wificom import punchbag

def pytest_generate_tests(metafunc):
	filenames = [filename for filename in os.listdir(target_paths.punchbag_data) if filename.startswith("L")]
	metafunc.parametrize("filename", filenames)

def test_error(filename):
	line_label_target = filename.split("_")[0] + ":*"
	with open(os.path.join(target_paths.punchbag_data, filename), encoding="UTF-8") as data_file:
		tree = punchbag.DigiROM_Tree(data_file)
		with pytest.raises(ValueError, match=line_label_target):
			tree.children()
