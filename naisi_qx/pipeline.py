from __future__ import annotations

from dataclasses import asdict
import json
import logging
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from .converter import Conversion, ConversionError, cats_compare, validate_outputs
from .network import audit_dependencies, digest, download_source, get, utc_now
from .reporting import coverage_report, cats_report, dumps, validation_report


ROOT = Path(__file__).resolve().parents[1]
QX_COMMIT = "af6fb594233ec4a3ec6d4ccb3601e9c36b75ea2d"
QX_FILES = {"sample.conf": "qx-sample.conf", "rewrite.md": "qx-rewrite.md",
            "resource-parser.js": "qx-resource-parser.js", "sample-import-rewrite.snippet": "qx-import-rewrite.snippet",
            "sample-echo-response.js": "qx-sample-echo-response.js"}


def write(path: Path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8") if isinstance(content, str) else content)


def fetch_sources(destination: Path):
    destination.mkdir(parents=True, exist_ok=True)
    metadata = {
        "naisi": download_source("fmz200/wool_scripts", "main", "QuantumultX/rewrite/rewrite.snippet",
                                 destination / "naisi-original.snippet"),
        "cats": download_source("Cats-Team/AdRules", "main", "qx.conf", destination / "cats-qx.conf"),
        "qx": {"repo": "crossutility/Quantumult-X", "commit": QX_COMMIT,
               "note": "固定为本转换器实际调研过的官方文档版本；新语法需人工更新转换器后测试"}}
    license_url = f"https://raw.githubusercontent.com/fmz200/wool_scripts/{metadata['naisi']['commit']}/LICENSE"
    data, _ = get(license_url)
    write(destination / "naisi-LICENSE", data)
    for source, target in QX_FILES.items():
        url = f"https://raw.githubusercontent.com/crossutility/Quantumult-X/{QX_COMMIT}/{source}"
        data, _ = get(url)
        write(destination / target, data)
    metadata["files"] = {p.name: digest(p.read_bytes()) for p in sorted(destination.iterdir()) if p.is_file()}
    write(destination / "sources.json", dumps(metadata))
    return metadata


def offline_sources(source: Path, target: Path):
    info = json.loads((source / "sources.json").read_text())
    if info["naisi"]["repo"] != "fmz200/wool_scripts" or info["naisi"]["path"] != "QuantumultX/rewrite/rewrite.snippet":
        raise ConversionError("离线来源不是指定的官方原版路径")
    if digest((source / "naisi-original.snippet").read_bytes()) != info["naisi"]["sha256"]:
        raise ConversionError("官方原版快照摘要与来源清单不一致")
    for name, expected in info["files"].items():
        if digest((source / name).read_bytes()) != expected:
            raise ConversionError(f"上游快照被改动：{name}")
        write(target / name, (source / name).read_bytes())
    write(target / "sources.json", dumps(info))
    return info


def stable_audits(fresh, previous):
    """Identical inputs keep artifacts byte-for-byte identical; logs record every new check."""
    for key, value in fresh.items():
        old = previous.get(key)
        if old and {k:v for k,v in old.items() if k != "checked_at"} == {k:v for k,v in value.items() if k != "checked_at"}:
            value["checked_at"] = old["checked_at"]
    return fresh


def build_candidate(candidate: Path, *, offline=False, bootstrap=False, run_tests=True):
    if (ROOT / ".build").resolve() not in candidate.resolve().parents:
        raise ConversionError("候选目录必须位于本项目 .build/ 内，避免覆盖其他目录")
    # Fresh temporary candidate, then rename. Never reuse a half-built previous candidate.
    candidate.parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="naisi-build-", dir=candidate.parent))
    try:
        sources = offline_sources(ROOT / "upstream", work / "upstream") if offline else fetch_sources(work / "upstream")
        text = (work / "upstream/naisi-original.snippet").read_text(encoding="utf-8-sig")
        inventory = Conversion(text)
        required = inventory.dependency_urls()
        old_file = ROOT / "dependency-audit.json"
        previous = json.loads(old_file.read_text()) if old_file.exists() else {}
        cache = ROOT / ".cache/dependencies"
        if offline:
            dependencies = previous
            for url in required:
                item = dependencies.get(url)
                if not item or not item.get("ok"):
                    raise ConversionError(f"离线依赖缺失/失败：{url}；先在线运行更新")
                path = cache / item["cache_file"]
                if not path.exists() or digest(path.read_bytes()) != item.get("sha256"):
                    raise ConversionError(f"离线缓存缺失或被改动：{url}；先在线运行更新")
            logging.info("offline: reusing previous HTTP evidence, no claim of live reachability")
        else:
            fresh = audit_dependencies(required, cache)
            logging.info("live HTTP evidence: %s", dumps(fresh).strip())
            dependencies = stable_audits(fresh, previous)
        conversion = Conversion(text, dependencies=dependencies, data_cache=cache)
        rewrite, filters = conversion.render("rewrite"), conversion.render("filter")
        errors = validate_outputs(conversion, rewrite, filters) + conversion.gate_errors
        comparison = cats_compare(conversion.kept("filter"), (work / "upstream/cats-qx.conf").read_text())
        if comparison["cats_parse_errors"]:
            errors.append("Cats 出现无法解析的新规则，差集结论不完整")
        baseline_file = ROOT / "rule-inventory.json"
        baseline = json.loads(baseline_file.read_text()) if baseline_file.exists() else []
        baseline_quarantine = {x["raw"].strip() for x in baseline if x["status"] == "quarantined"}
        for rule in conversion.rules:
            if rule.status == "quarantined" and rule.raw.strip() not in baseline_quarantine and not bootstrap:
                errors.append(f"新增隔离 L{rule.line}，需先审阅候选报告；保留当前有效版本")
        if not baseline and not bootstrap:
            errors.append("首次生成须显式使用 --bootstrap 接受已审阅隔离；后续更新无需此参数")
        outputs = {
            "Naisi-QX-Rewrite.conf": rewrite,
            "Naisi-QX-Filter.list": filters,
            "Naisi-QX-Filter-Delta.list": "# 奶思未被 Cats 完整覆盖的候选；策略 reject；见 cats-comparison.md\n" +
                "\n".join(x["rule"] for x in comparison["rules"] if x["status"] == "residual") + "\n",
            "source-ledger.json": dumps(conversion.ledger),
            "rule-inventory.json": dumps([asdict(r) for r in conversion.rules]),
            "hostname-audit.json": dumps({"hostnames": conversion.hostname_audit, "rules": conversion.mitm_rule_audit}),
            "coverage.json": dumps(conversion.coverage()), "coverage.md": coverage_report(conversion.coverage()),
            "cats-comparison.json": dumps(comparison), "cats-comparison.md": cats_report(comparison, sources["cats"]),
            "dependency-audit.json": dumps(dependencies),
            **conversion.assets,
        }
        for name, content in outputs.items():
            write(work / name, content)
        results = {"status": "not-run", "tests_run": 0}
        write(work / "validation-report.md", validation_report(conversion, sources, dependencies, errors))
        write(work / "validation.json", dumps({"errors": errors, "stats": conversion.stats(), "tests": results}))
        if run_tests:
            env = dict(os.environ, NAISI_CANDIDATE=str(work))
            proc = subprocess.run(["python3", "-m", "unittest", "discover", "-s", "tests", "-v"],
                                  cwd=ROOT, env=env, capture_output=True, text=True, timeout=240)
            output = proc.stdout + proc.stderr
            import re
            match = re.search(r"Ran (\d+) tests?", output)
            results = {"status": "passed" if proc.returncode == 0 else "failed", "tests_run": int(match[1]) if match else 0,
                       "command": "python3 -m unittest discover -s tests -v", "returncode": proc.returncode}
            logging.info("tests: %s", output.strip())
            if proc.returncode:
                errors.append("自动化测试失败，详见 logs 中的完整输出")
        if not run_tests:
            errors.append("未运行测试，候选不可发布")
        write(work / "test-results.json", dumps(results))
        write(work / "validation-report.md", validation_report(conversion, sources, dependencies, errors, results))
        write(work / "validation.json", dumps({"errors": errors, "stats": conversion.stats(), "tests": results}))
        paths = sorted(str(p.relative_to(work)) for p in work.rglob("*") if p.is_file())
        manifest = {"format_version": 1, "valid": not errors, "stats": conversion.stats(),
                    "files": {name: digest((work / name).read_bytes()) for name in paths}}
        write(work / "manifest.json", dumps(manifest))
        if candidate.exists():
            shutil.rmtree(candidate)
        work.rename(candidate)
        logging.info("candidate %s valid=%s stats=%s", candidate, not errors, conversion.stats())
        return {"valid": not errors, "errors": errors, "stats": conversion.stats(), "path": str(candidate)}
    finally:
        if work.exists():
            shutil.rmtree(work)


def verify_candidate(candidate: Path):
    manifest = json.loads((candidate / "manifest.json").read_text())
    if not manifest.get("valid"):
        raise ConversionError("候选检查未通过，拒绝替换有效文件")
    for name, expected in manifest["files"].items():
        path = Path(name)
        allowed = {"Naisi-QX-Rewrite.conf", "Naisi-QX-Filter.list", "Naisi-QX-Filter-Delta.list",
            "source-ledger.json", "rule-inventory.json", "hostname-audit.json", "coverage.json", "coverage.md",
            "cats-comparison.json", "cats-comparison.md", "dependency-audit.json", "validation-report.md",
            "validation.json", "test-results.json"}
        upstream_names = {"naisi-original.snippet", "cats-qx.conf", "naisi-LICENSE", "sources.json", *QX_FILES.values()}
        safe = name in allowed or (len(path.parts) == 2 and path.parts[0] == "upstream" and path.name in upstream_names)
        import re
        safe = safe or bool(re.fullmatch(r"Data/Naisi-[0-9a-f]{12}\.json", name))
        if path.is_absolute() or ".." in path.parts or not safe:
            raise ConversionError("候选清单包含越界路径")
        if digest((candidate / name).read_bytes()) != expected:
            raise ConversionError("候选文件在校验后被改动：" + name)
    return manifest


def promote(candidate: Path, destination=ROOT):
    manifest = verify_candidate(candidate)
    changed = []
    backups = {}
    files = list(manifest["files"]) + ["manifest.json"]
    try:
        for name in files:
            path = destination / name
            data = (candidate / name).read_bytes()
            if path.exists() and path.read_bytes() == data:
                continue
            backups[name] = path.read_bytes() if path.exists() else None
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
                handle.write(data)
                temporary = handle.name
            os.replace(temporary, path)
            changed.append(name)
    except Exception:
        for name in reversed(changed):
            if backups[name] is None:
                (destination / name).unlink(missing_ok=True)
            else:
                write(destination / name, backups[name])
        raise
    logging.info("promoted %s changed files", len(changed))
    return changed
