from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import logging
import os
from pathlib import Path
import re
import subprocess
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request


USER_AGENT = "Naisi-QX-Converter/1.0 (+https://github.com/fmz200/wool_scripts)"


class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        redirected = super().redirect_request(request, fp, code, message, headers, new_url)
        if redirected is not None and urllib.parse.urlsplit(new_url).hostname != "api.github.com":
            redirected.remove_header("Authorization")
        return redirected


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_url(url: str) -> str:
    """Only change GitHub's raw delivery endpoint; keep repo/ref/path/hash."""
    parsed = urllib.parse.urlsplit(url)
    if parsed.hostname in {"github.com", "www.github.com"}:
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 5 and parts[2] == "raw":
            return urllib.parse.urlunsplit(("https", "raw.githubusercontent.com",
                "/" + "/".join(parts[:2] + parts[3:]), parsed.query, parsed.fragment))
    return url


def get(url: str, *, timeout=25, limit=16_000_000, retries=2):
    url = urllib.parse.urldefrag(url)[0]
    last = None
    for attempt in range(retries + 1):
        try:
            request_headers = {"User-Agent": USER_AGENT}
            # Only send workflow authentication to GitHub's API, never to raw
            # dependencies or redirect destinations. Tokens are never logged.
            token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
            if urllib.parse.urlsplit(url).hostname == "api.github.com" and token:
                request_headers["Authorization"] = "Bearer " + token
            request = urllib.request.Request(url, headers=request_headers)
            with urllib.request.build_opener(PublicRedirect()).open(request, timeout=timeout) as response:
                data = response.read(limit + 1)
                if len(data) > limit:
                    raise ValueError(f"响应超过 {limit} bytes")
                return data, {"status": response.status, "final_url": response.url,
                    "content_type": response.headers.get("Content-Type", ""),
                    "etag": response.headers.get("ETag", "")}
        except (OSError, ValueError) as exc:
            last = exc
            if isinstance(exc, urllib.error.HTTPError) and exc.code < 500:
                break
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"{url}: {last}")


def resolve_commit(repo: str, branch: str) -> dict:
    try:
        data, _ = get(f"https://api.github.com/repos/{repo}/commits/{branch}", limit=2_000_000)
        info = json.loads(data)
    except RuntimeError as exc:
        logging.info("GitHub API unavailable (%s); trying read-only local GitHub/Git transport", exc)
        info = None
        if shutil.which("gh"):
            proc = subprocess.run(["gh", "api", f"repos/{repo}/commits/{branch}"],
                                  capture_output=True, text=True, timeout=45)
            if proc.returncode == 0:
                info = json.loads(proc.stdout)
        if info is None and shutil.which("git"):
            proc = subprocess.run(["git", "ls-remote", "https://github.com/" + repo + ".git", "refs/heads/" + branch],
                                  capture_output=True, text=True, timeout=45)
            if proc.returncode == 0 and proc.stdout.strip():
                info = {"sha": proc.stdout.split()[0], "commit": {"committer": {"date": "未从 Git 传输取得日期"}}}
        if info is None:
            raise RuntimeError(f"无法确定官方 {repo}/{branch} 的最新 commit；保留有效文件") from exc
    if not re.fullmatch(r"[0-9a-f]{40}", info.get("sha", "")):
        raise ValueError(f"无效的 GitHub commit: {repo}")
    return {"repo": repo, "branch": branch, "commit": info["sha"],
            "commit_date": info["commit"]["committer"]["date"]}


def download_source(repo: str, branch: str, path: str, target: Path):
    info = resolve_commit(repo, branch)
    url = f"https://raw.githubusercontent.com/{repo}/{info['commit']}/{path}"
    data, headers = get(url)
    if b"<html" in data[:1024].lower() or not data.strip():
        raise ValueError(f"规则来源不是有效文本: {url}")
    data.decode("utf-8-sig")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return {**info, "path": path, "url": url,
            "tracking_url": f"https://raw.githubusercontent.com/{repo}/{branch}/{path}",
            "sha256": digest(data), "bytes": len(data), **headers}


def audit_dependency(url: str, cache: Path, *, kind="script", timeout=25) -> dict:
    checked = utc_now()
    delivery = canonical_url(url)
    result = {"url": url, "delivery_url": delivery, "kind": kind, "checked_at": checked}
    try:
        data, headers = get(delivery, timeout=timeout, limit=8_000_000)
        result.update(headers)
        result.update(sha256=digest(data), bytes=len(data))
        content = data.decode("utf-8-sig")
        if not content.strip():
            raise ValueError("空响应")
        if "text/html" in headers["content_type"].lower() or re.search(
                r"^\s*(?:<!doctype\s+html|<html\b)", content, re.I):
            raise ValueError("返回 HTML，不能当作脚本/JSON 使用")
        suffix = ".js" if kind == "script" else ".json"
        path = cache / (digest(url.encode()) + suffix)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        result["cache_file"] = str(path.name)
        if kind == "script":
            check = subprocess.run(["node", str(Path(__file__).resolve().parents[1] /
                "tools/js-audit.cjs"), str(path)], capture_output=True, text=True, timeout=20)
            syntax = json.loads(check.stdout)
            result["syntax"] = syntax
            if not syntax["ok"]:
                raise ValueError(syntax["error"])
            result["qx_api_signals"] = sorted(set(re.findall(
                r"\$(?:task|prefs|done|request|response|httpClient|persistentStore|environment)\b", content)))
            result["dynamic_code"] = bool(re.search(r"\beval\s*\(|new\s+Function\s*\(", content))
            result["runtime_fetch"] = bool(re.search(r"\$task\.fetch|\$httpClient|\bfetch\s*\(", content))
        else:
            json.loads(content)
        result["ok"] = True
    except Exception as exc:
        result.update(ok=False, error=str(exc))
    logging.info("dependency %s %s", "OK" if result["ok"] else "FAIL", url)
    return result


def audit_dependencies(dependencies: dict[str, dict], cache: Path, *, workers=6):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda item: audit_dependency(item[0], cache,
            kind=item[1]["kind"]), sorted(dependencies.items())))
    return {item["url"]: {**item, "source_lines": dependencies[item["url"]]["source_lines"]}
            for item in results}
