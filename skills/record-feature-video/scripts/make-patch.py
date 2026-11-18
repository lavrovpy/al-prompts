"""Write the name-patch init script for agent-browser from a name map.

Usage: python3 make-patch.py <names.json> <out.js>
The same names.json gives ocr-check.sh its patterns (the "ocr" list).
"""

import json
import sys
from pathlib import Path

names = json.loads(Path(sys.argv[1]).read_text())
for key in ("hosts", "replace"):
    if key not in names:
        sys.exit(f"{sys.argv[1]} has no {key!r}")
template = (Path(__file__).parent / "patch.template.js").read_text()
Path(sys.argv[2]).write_text(template.replace("__CONFIG__", json.dumps(names, indent=2)))
print(sys.argv[2])
