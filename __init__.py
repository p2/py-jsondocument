import sys
import os.path
abspath = os.path.realpath(os.path.dirname(__file__))
if abspath not in sys.path:
	sys.path.insert(0, abspath)
