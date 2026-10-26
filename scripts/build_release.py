#!/usr/bin/env python3
import hashlib
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
version = re.search(r"^CXI_VERSION=(\S+)", (root/"cxi-core.sh").read_text()).group(1)
if len(sys.argv) > 1 and sys.argv[1] != "v"+version:
    raise SystemExit("Tag does not match CXI_VERSION")
target = root/"dist"
target.mkdir(exist_ok=True)
manifest = ""
for name in ("cxi-core.sh", "cxi.bash", "cxi.zsh", "README.md"):
    data = (root/name).read_bytes()
    (target/name).write_bytes(data)
    manifest += hashlib.sha256(data).hexdigest()+"  "+name+"\n"
(target/"SHA256SUMS").write_text(manifest)
template = (root/"install.sh.in").read_text()
(target/"install.sh").write_text(template.replace("@MANIFEST_SHA256@", hashlib.sha256(manifest.encode()).hexdigest()))
print("Built cxi "+version)
