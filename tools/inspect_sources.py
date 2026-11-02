"""Read-only source inventory used during the initial investigation."""
from pathlib import Path
import collections
import re

text = Path("upstream/naisi-original.snippet").read_text()
counts = collections.Counter()
for no, raw in enumerate(text.splitlines(), 1):
    line = raw.strip()
    if not line:
        counts["blank"] += 1
    elif line.startswith(("#", ";", "//")):
        counts["comment"] += 1
    elif line.startswith("hostname"):
        counts["mitm"] += 1
    elif re.search(r"\surl(?:-and-header)?\s", line):
        counts["rewrite"] += 1
    elif "," in line:
        counts["filter_or_foreign"] += 1
    else:
        print(no, line)
        counts["unknown"] += 1
print(dict(counts))
