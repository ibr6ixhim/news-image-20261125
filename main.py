"""Entry program: copies the pre-rendered front page to /output/entry.png.

The image is produced at build time by build.py (from stories.json). This program needs
no network and no third-party packages, and it is deterministic (same bytes on every run).
"""
import os
import shutil

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "entry.png")
OUT_DIR = "/output"
OUT = os.path.join(OUT_DIR, "entry.png")

os.makedirs(OUT_DIR, exist_ok=True)
shutil.copyfile(SRC, OUT)
os.chmod(OUT, 0o644)  # outputs must be readable by every user
