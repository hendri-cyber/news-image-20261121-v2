#!/usr/bin/env python3
"""Entry point: place the pre-rendered front page at the output path.

The image is rendered by draw.py in this repo (run it first to rebuild
entry.png). This program only copies the file, so repeated runs write
identical bytes and need no third-party packages.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
DST_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

if not os.path.exists(SRC):
    sys.exit("entry.png missing: run draw.py first")

os.makedirs(DST_DIR, exist_ok=True)
shutil.copyfile(SRC, os.path.join(DST_DIR, "entry.png"))
print("entry.png ->", DST_DIR)
