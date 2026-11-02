#!/usr/bin/env python3
"""Create a reviewable local delivery ZIP; never upload or modify Git state."""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from naisi_qx.network import digest
from naisi_qx.pipeline import verify_candidate


def main():
    manifest = verify_candidate(ROOT)
    excluded = {".git", ".cache", ".build", "dist", "__pycache__", "logs"}
    files = [p for p in ROOT.rglob("*") if p.is_file() and not any(x in excluded for x in p.relative_to(ROOT).parts)
             and p.name != ".DS_Store" and p.suffix not in {".pyc", ".pyo"}]
    # Include the most recent completed validation log, not external credentials
    # or all local runtime directories. Logs contain only this converter's evidence.
    latest_logs = sorted((ROOT / "logs").glob("update-*.log"))
    if latest_logs:
        files.append(latest_logs[-1])
    proof = ROOT / "logs/reproducibility-check.json"
    if proof.exists():
        files.append(proof)
    sources = json.loads((ROOT / "upstream/sources.json").read_text())
    stamp = sources['naisi']['commit_date']
    try:
        date = datetime.fromisoformat(stamp.replace('Z','+00:00'))
        zip_date = (date.year, date.month, date.day, date.hour, date.minute, date.second)
    except ValueError:
        zip_date = (2026,1,1,0,0,0)
    destination = ROOT / "dist/Naisi-QX-Complete.zip"
    destination.parent.mkdir(exist_ok=True)
    checksums = {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in sorted(set(files))}
    with zipfile.ZipFile(destination,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in sorted(set(files)):
            info = zipfile.ZipInfo("Naisi-QX/" + str(path.relative_to(ROOT)), date_time=zip_date)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info,path.read_bytes())
        info = zipfile.ZipInfo("Naisi-QX/package-checksums.json", date_time=zip_date)
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info,json.dumps(checksums,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("ZIP integrity check failed")
        for name, expected in checksums.items():
            if digest(archive.read("Naisi-QX/" + name)) != expected:
                raise RuntimeError("ZIP content mismatch: " + name)
    print(json.dumps({"path":str(destination),"bytes":destination.stat().st_size,"files":len(files),
                      "sha256":digest(destination.read_bytes()),"stats":manifest['stats'],
                      "tests":json.loads((ROOT/'test-results.json').read_text())},ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
