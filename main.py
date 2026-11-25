"""Entry program: copies the pre-rendered front page to /output/entry.png.

The image is produced at build time by build.py (from stories.json).
This program needs no network and no third-party packages, and it is
deterministic: the same bytes on every run.
"""
import hashlib
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
OUT = os.path.join(OUT_DIR, "entry.png")

os.makedirs(OUT_DIR, exist_ok=True)
shutil.copyfile(SRC, OUT)
os.chmod(OUT, 0o644)  # outputs must be readable by every user
src_sha = hashlib.sha256(open(SRC, "rb").read()).hexdigest()
out_sha = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
if src_sha != out_sha or os.path.getsize(SRC) != os.path.getsize(OUT):
    raise SystemExit("copy mismatch: output does not match entry.png")
print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes, sha256={out_sha})")
