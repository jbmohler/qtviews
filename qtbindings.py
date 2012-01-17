#!/usr/bin/env python
import os
import glob

files = """
setup.py
lib/*.py

scripts/pyhacc
"""

files = [f.strip() for f in files.split('\n') if f.strip() != ""]

import argparse
parser = argparse.ArgumentParser(description='Convert package to use PySide or PyQt4')
parser.add_argument('--platform', dest='platform', type=str, default='PyQt4', help='value must be PySide or PyQt4')
parser.add_argument('--sudo', dest='sudo', type=str, default='', help='sudo incarnation (if desired) for cleaning build folders')
args = parser.parse_args()

full_file_list = sum([glob.glob(f) for f in files], [])
print "Converting {0} files to use {1}.".format(len(full_file_list), args.platform)
dest = args.platform
assert dest in ["PyQt4", "PySide"]
src = "PySide" if dest == "PyQt4" else "PyQt4"

for f in full_file_list:
    s = None
    with open(f, "r") as fh:
        s = fh.read()
    s = s.replace("from {0}".format(src), "from {0}".format(dest))
    s = s.replace("qt_bindings = '{0}'".format(src), "qt_bindings = '{0}'".format(dest))
    s = s.replace("QtUiBuild(Command, {0}UiBuild)".format(src), "QtUiBuild(Command, {0}UiBuild)".format(dest))
    s = s.replace("\r\n", "\n")
    with open(f, "wb") as fh:
        fh.write(s)
