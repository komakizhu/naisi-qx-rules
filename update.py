#!/usr/bin/env python3
"""从奶思官方原版生成 QX 资源。Python 3.11+、Node、jq、系统 ICU。"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
import sys
import time

from naisi_qx.pipeline import ROOT, build_candidate, promote
from naisi_qx.reporting import dumps


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="复用官方快照和已检查依赖；不声称实时可访问")
    parser.add_argument("--bootstrap", action="store_true", help="首次/审阅新增隔离后，显式接受隔离基线；不绕过失败的依赖或测试")
    parser.add_argument("--candidate-dir", type=Path, help="只生成此候选目录，通过后也不替换当前产物")
    parser.add_argument("--promote", type=Path, help="只提升已经全部通过的候选；提升前核对完整摘要")
    args = parser.parse_args()
    logs = ROOT / "logs"
    logs.mkdir(exist_ok=True)
    log = logs / (time.strftime("update-%Y%m%d-%H%M%S", time.gmtime()) + f"-{time.time_ns()%1000000:06d}.log")
    logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s",
                        handlers=[logging.FileHandler(log, encoding="utf-8")])
    logging.Formatter.converter = time.gmtime
    # Lock belongs to the converter, not to any of the user's proxy software.
    import fcntl
    lock = (logs / ".update.lock").open("w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("已有更新正在运行；未替换当前文件。", file=sys.stderr)
        return 2
    try:
        if args.promote:
            changed = promote(args.promote.resolve())
            print(dumps({"promoted": True, "changed_files": len(changed), "log": str(log)}), end="")
            return 0
        candidate = (args.candidate_dir or ROOT / ".build/candidate").resolve()
        print("正在读取官方原版并校验依赖；完整日志：" + str(log), flush=True)
        result = build_candidate(candidate, offline=args.offline, bootstrap=args.bootstrap)
        if result["valid"] and not args.candidate_dir:
            result["changed_files"] = len(promote(candidate))
        result["log"] = str(log)
        print(dumps(result), end="")
        return 0 if result["valid"] else 1
    except Exception as exc:
        logging.exception("update failed; valid outputs preserved")
        print(f"更新失败，当前有效文件未替换：{exc}\n日志：{log}", file=sys.stderr)
        return 1
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()


if __name__ == "__main__":
    raise SystemExit(main())
