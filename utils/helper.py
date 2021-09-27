"""
This module will contain helping functions.
"""

import contextlib
import sys

class DummyFile(object):
    def write(self, x): pass

    def flush(self, x): pass

@contextlib.contextmanager
def silent_std_out():
    save_stdout = sys.stdout
    sys.stdout = DummyFile()
    yield
    sys.stdout = save_stdout
