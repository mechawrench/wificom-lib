
import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.realpath("__file__")))
lib_dir = os.path.join(root_dir, "lib")
sys.path.append(lib_dir)

punchbag_data = os.path.join(root_dir, "tests/punchbag_data")
