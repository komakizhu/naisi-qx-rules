from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
import fnmatch
import ipaddress
import itertools
import json
from pathlib import Path
import re
import subprocess

from tools.icu_regex import ICURegex
from .network import canonical_url, digest


COMMENTS = ("#", ";", "//")
FILTER_TYPES = {"host", "host-suffix", "host-keyword", "host-wildcard", "ip-cidr", "ip6-cidr"}
ALIASES = {"domain": "host", "domain-suffix": "host-suffix", "domain-keyword": "host-keyword",
           "ip-cidr6": "ip6-cidr"}
REJECTS = {"reject", "reject-200", "reject-img", "reject-dict", "reject-array"}
SCRIPTS = {"script-request-header", "script-request-body", "script-response-header",
           "script-response-body", "script-echo-response", "script-analyze-echo-response"}
REPLACEMENTS = {"request-header", "response-header", "request-body", "response-body"}
# response-header is not shown in the pinned official sample: fail closed below.
SUPPORTED_REPLACEMENTS = REPLACEMENTS - {"response-header"}
JQ_ACTIONS = {"jsonjq-request-body", "jsonjq-response-body"}
REDIRECTS = {"302", "307"}
REWRITE_RE = re.compile(r"^(\S+)\s+(?:(.*?)\s+)?(url(?:-and-header)?)\s+(\S+)(?:\s+(.*))?$", re.I)


class ConversionError(ValueError):
    pass


@dataclass
class Rule:
    line: int
    raw: str
    app: str
    kind: str
    pattern: str = ""
    header: str = ""
    operator: str = "url"
    action: str = ""
    argument: str = ""
    filter_type: str = ""
    value: str = ""
    status: str = "kept"
    output: str = ""
    fixes: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    references: list[int] = field(default_factory=list)
    hints: list[str] = field(default_factory=list)
    optional: bool = False
    context: list[str] = field(default_factory=list)
    evidence: str = ""
    alternative: str = ""
    hostname_refs: list[str] = field(default_factory=list)
    features: list[str] = field(default_factory=list)

    def render(self):
        if self.kind == "filter":
            return f"{self.filter_type}, {self.value}, reject"
        matcher = self.pattern + (" " + self.header if self.header else "")
        return f"{matcher} {self.operator} {self.action}" + (" " + self.argument if self.argument else "")

    def match_key(self):
        # Escaped / and : are literals in both ICU and QX-style regexes.
        norm = lambda x: x.replace(r"\/", "/").replace(r"\:", ":")
        return (norm(self.pattern), self.header, self.operator)

    def duplicate_key(self):
        if self.kind == "filter":
            return (self.kind, self.filter_type, self.value, self.action)
        return (self.kind, *self.match_key(), self.action, self.argument)


def is_comment(line):
    return line.lstrip().startswith(COMMENTS)


def domain_valid(value: str, *, wildcards=False):
    if not value or len(value) > 253 or value.startswith("-"):
        return False
    allowed = r"[a-z0-9_?*.-]+" if wildcards else r"[a-z0-9_.-]+"
    return bool(re.fullmatch(allowed, value)) and all(value.split("."))


def jq_expression(argument: str):
    text = argument.strip()
    if text.startswith("'"):
        if not text.endswith("'") or len(text) < 2:
            raise ConversionError("JSONJQ 单引号未闭合")
        return text[1:-1]
    if "'" in text:
        raise ConversionError("JSONJQ 引号格式无法确认")
    return text


def jq_error(argument: str):
    expr = jq_expression(argument)
    if not expr.strip():
        return "JSONJQ 表达式为空"
    # Compile unreachable branch, do not run a filter against invented API data.
    check = subprocess.run(["jq", "-n", f"if false then ({expr}) else null end"],
                           capture_output=True, text=True, timeout=10)
    return check.stderr.strip() if check.returncode else None


def parse_filter(text: str, no=0, app="", *, normalize=True) -> Rule:
    parts = [x.strip() for x in text.split(",")]
    if len(parts) != 3 or parts[2].lower() != "reject":
        raise ConversionError("分流必须是类型、目标、reject 三段；不擅自改变其他策略")
    raw_type = parts[0]
    kind = ALIASES.get(raw_type.lower(), raw_type.lower())
    if kind not in FILTER_TYPES:
        raise ConversionError(f"不是本交付范围的域名/IP 分流类型：{raw_type}")
    rule = Rule(no, text, app, "filter", filter_type=kind, value=parts[1].lower(), action="reject")
    if raw_type != kind or parts[2] != "reject":
        rule.fixes.append(f"规则类型/动作标准化：{raw_type} → {kind}，策略 reject")
    if kind in {"ip-cidr", "ip6-cidr"}:
        try:
            network = ipaddress.ip_network(rule.value, strict=False)
        except ValueError as exc:
            raise ConversionError(f"无效 CIDR：{exc}") from exc
        if (network.version == 6) != (kind == "ip6-cidr"):
            raise ConversionError("IP 地址族与规则类型不一致")
        if str(network) != rule.value:
            rule.fixes.append(f"CIDR 网络地址标准化：{rule.value} → {network}（同一子网）")
        rule.value = str(network)
    elif kind in {"host", "host-suffix", "host-wildcard"}:
        if not domain_valid(rule.value, wildcards=kind == "host-wildcard"):
            raise ConversionError(f"目标不符合本工具的标准主机名/通配符检查：{rule.value}；不据此断言所有 QX 版本都会拒绝")
    elif not rule.value or re.search(r"[\s,/=:]", rule.value):
        raise ConversionError("host-keyword 包含空格、URL 或非法分隔符")
    rule.output = rule.render()
    return rule


def parse_rewrite(text: str, no=0, app="", *, repairs=True) -> Rule:
    fixes = []
    if repairs and re.match(r"^\S+\s+-\s+reject(?:-\w+)?$", text, re.I):
        text = re.sub(r"\s+-\s+", " url ", text, count=1)
        fixes.append("将其他软件的 ‘- reject-*’ 写法转换为 QX ‘url reject-*’")
    match = REWRITE_RE.fullmatch(text)
    if not match:
        raise ConversionError("无法按 URL [header] url/url-and-header action [argument] 解析")
    pattern, header, operator, action, argument = match.groups()
    rule = Rule(no, text, app, "rewrite", pattern=pattern, header=header or "",
                operator=operator.lower(), action=action.lower(), argument=argument or "", fixes=fixes)
    if operator != rule.operator or action != rule.action:
        rule.fixes.append("重写操作符/动作改为官方示例的小写")
    if bool(header) != (rule.operator == "url-and-header"):
        raise ConversionError("url-and-header 必须同时有 URL 与头部匹配式；url 不能多一个匹配式")
    if repairs and "http?:" in rule.pattern:
        rule.pattern = rule.pattern.replace("http?:", "https?:")
        rule.fixes.append("将 http?: 修成 https?:；原式只匹配 htt/http，遗漏 HTTPS")
    if repairs and r"res\.kfc\.com.\cn" in rule.pattern:
        rule.pattern = rule.pattern.replace(r"res\.kfc\.com.\cn", r"res\.kfc\.com\.cn")
        rule.fixes.append("肯德基域名误写的 \\c 控制字符改为字面域名点，与源注释 res.kfc.com.cn 一致")
    if repairs and r"(114\.115\.217\.129)|(home\.umetrip\.com)" in rule.pattern:
        rule.pattern = rule.pattern.replace(r"(114\.115\.217\.129)|(home\.umetrip\.com)", r"(114\.115\.217\.129|home\.umetrip\.com)")
        rule.fixes.append("航旅纵横主机二选一补成同一组，使协议、路径和结尾同时约束两个分支，避免 IP 分支匹配全部路径")
    if repairs and "getStartSend?client_sys=ios" in rule.pattern:
        rule.pattern = rule.pattern.replace("getStartSend?client_sys=ios", r"getStartSend\?client_sys=ios")
        rule.fixes.append("斗鱼 getStartSend 后的查询问号转义为字面字符；原式把前一个字母设为可选")
    if rule.action in REJECTS:
        if rule.argument:
            raise ConversionError("reject 动作不应带额外参数")
    elif rule.action in SCRIPTS:
        if not re.fullmatch(r"https?://\S+", rule.argument):
            raise ConversionError("上游脚本不是单一 HTTP(S) URL；不能确认本地脚本已存在")
        delivery = canonical_url(rule.argument)
        if delivery != rule.argument and repairs:
            rule.argument = delivery
            rule.fixes.append("GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变")
    elif rule.action in JQ_ACTIONS:
        expr = jq_expression(rule.argument)
        if repairs and not rule.argument.startswith("'"):
            rule.argument = "'" + expr + "'"
            rule.fixes.append("为 JSONJQ 表达式补齐官方示例使用的外层单引号")
        error = jq_error(rule.argument)
        if error:
            raise ConversionError(f"JSONJQ 编译失败：{error}")
    elif rule.action in SUPPORTED_REPLACEMENTS:
        delimiter = f" {rule.action} "
        if delimiter not in rule.argument:
            raise ConversionError("正文/请求头替换缺少第二个同名动作分隔符")
        before, _ = rule.argument.split(delimiter, 1)
        if not before:
            raise ConversionError("替换匹配式为空")
    elif rule.action == "echo-response":
        if not re.fullmatch(r"\S+\s+echo-response\s+\S+", rule.argument):
            raise ConversionError("echo-response 必须指定 MIME 类型和数据文件")
    elif rule.action in REDIRECTS:
        if not rule.argument or re.search(r"\s", rule.argument):
            raise ConversionError("重定向必须有单一目标 URL/替换式")
    else:
        raise ConversionError(f"官方固定示例中未确认的动作：{rule.action}；不猜测转换")
    rule.output = rule.render()
    return rule


def authority(pattern: str):
    """Extract an authority regex, exclusively for auditing MITM (never rewrite URLs)."""
    text = pattern.replace(r"\/", "/").replace(r"\:", ":")
    text = text.replace(r"^http(s://tiebac|://c\.tieba)", r"^https?://(tiebac|c\.tieba)")
    if "://" not in text:
        return None
    rest = text.split("://", 1)[1]
    host = rest.split("/", 1)[0].rstrip("$")
    # A group that begins the path isn't part of the authority.
    host = host.rstrip("(")
    # A root grouping that ends immediately after the host is an edge case;
    # compilation below rejects ambiguity instead of inventing a MITM wildcard.
    return host


def finite_hosts(pattern: str, limit=128):
    """Conservatively expand only literals, finite groups, and optional literals.

    Unbounded regex hosts are kept with their upstream wildcard scope, never
    replaced by an invented `hostname = *`.
    """
    host = authority(pattern)
    if not host:
        return []
    host = re.sub(r":\d+$", "", host)
    host = re.sub(r":\\d(?:\+|\{\d+(?:,\d*)?\})$", "", host)
    if host.endswith(r"(:\d+)?"):
        host = host[:-len(r"(:\d+)?")]
    try:
        from re import _parser, _constants as c
        parsed = _parser.parse(host, 0)
        def expand(tokens):
            result = [""]
            for op, value in tokens:
                if op is c.LITERAL:
                    values = [chr(value)]
                elif op is c.SUBPATTERN:
                    values = expand(value[-1])
                elif op is c.ATOMIC_GROUP:
                    values = expand(value)
                elif op is c.BRANCH:
                    values = [x for branch in value[1] for x in expand(branch)]
                elif op in (c.MAX_REPEAT, c.MIN_REPEAT) and value[1] <= 1:
                    values = ([""] if value[0] == 0 else []) + expand(value[2])
                elif op is c.AT:
                    values = [""]
                else:
                    raise ValueError("unbounded or complex authority")
                if len(result) * len(values) > limit:
                    raise ValueError("authority expansion limit")
                result = [a + b for a in result for b in values]
            return result
        return sorted({x for x in expand(parsed) if domain_valid(x)})
    except (ValueError, re.error, OverflowError):
        return []


def host_matches(authority_regex: str, token: str):
    token = token.lstrip("-")
    # Try several labels: \d, [a-z], literal api* and *.domains.
    probes = [token.replace("*", x).replace("?", "1") for x in ("qxprobe", "1", "api", "", "a0", "b0", "0", "c")]
    ports = ["", ":443", ":1", ":12345"] + [":" + x for x in re.findall(r":(\d+)", authority_regex)]
    try:
        matcher = re.compile("^(?:" + authority_regex + r")(?::\d+)?$")
        return any(matcher.fullmatch(p + port) is not None for p in probes for port in ports)
    except re.error:
        return False


def host_globs(pattern: str, limit=128):
    """Project a hostname-only regex to narrow QX globs, never to global `*`.

    Kept separately from the URL regex: these don't change URL matching. Literal
    host hints / existing declarations are preferred before adding a projection.
    """
    auth = authority(pattern)
    if not auth:
        return []
    auth = re.sub(r"\(:\\d\+\)\?$|:\\d(?:\+|\{\d+(?:,\d*)?\})$|:\d+$", "", auth)
    try:
        from re import _parser, _constants as c
        def expand(tokens):
            results = [""]
            for op, value in tokens:
                if op is c.LITERAL:
                    values = [chr(value)]
                elif op is c.ANY:
                    values = ["."]
                elif op in {c.IN, c.NOT_LITERAL, c.CATEGORY}:
                    values = ["?"]
                elif op is c.SUBPATTERN:
                    values = expand(value[-1])
                elif op is c.ATOMIC_GROUP:
                    values = expand(value)
                elif op is c.BRANCH:
                    values = [x for branch in value[1] for x in expand(branch)]
                elif op in {c.MAX_REPEAT, c.MIN_REPEAT}:
                    minimum, maximum, child = value
                    if maximum <= 1:
                        values = ([""] if minimum == 0 else []) + expand(child)
                    elif minimum == maximum and maximum <= 8:
                        values = ["".join(parts) for parts in itertools.product(expand(child), repeat=maximum)]
                    else:
                        values = ["*"]
                elif op is c.AT:
                    values = [""]
                else:
                    raise ValueError("unsupported host expression")
                if len(results) * len(values) > limit:
                    raise ValueError("projection limit")
                results = [x + y for x in results for y in values]
            return results
        values = expand(_parser.parse(auth, 0))
        return sorted({x for x in values if domain_valid(x, wildcards=True) and
                       re.search(r"(?:^|\.)[a-z0-9-]{2,}\.[a-z]{2,}$", x)})
    except (ValueError, re.error, OverflowError):
        return []


def features(rule: Rule):
    text = " ".join([rule.pattern, *rule.context]).lower()
    tags = []
    for name, pattern in {
        "开屏": r"splash|startup|launch|开屏|welcome|startimg",
        "弹窗": r"popup|pop-up|popwindow|dialog|弹窗|float|悬浮",
        "横幅": r"banner|横幅",
        "信息流/推荐": r"feed|recommend|信息流|推荐|nextfresh",
    }.items():
        if re.search(pattern, text):
            tags.append(name)
    if rule.kind == "rewrite":
        tags.append("脚本处理" if rule.action in SCRIPTS else "JSONJQ" if rule.action in JQ_ACTIONS
                    else "正文/头部替换" if rule.action in REPLACEMENTS else "URL拦截/重定向")
    else:
        tags.append("域名/IP拦截")
    return tags


def risk_notes(rule: Rule):
    notes = []
    text = rule.pattern + " " + rule.value
    auth = authority(rule.pattern) if rule.pattern else None
    if auth and re.search(r"(?<!\\)\.(?![+*?])", auth):
        notes.append("主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对")
    if re.search(r"login|passport|captcha|verify|auth|pay|cashier|order|cart|checkout|trade", text, re.I):
        notes.append("匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段")
    if re.search(r"recommend|feeds?|nextfresh|discover", text, re.I):
        notes.append("可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告")
    if rule.kind == "filter" and rule.filter_type == "host-keyword":
        notes.append("关键词会匹配任意包含该字符串的域名，作用范围较宽")
    if rule.kind == "filter" and rule.value == "temu.com":
        notes.append("整站阻断 temu.com，会影响正常购物访问；保留上游规则，建议已有 Cats 时先不开奶思分流")
    if rule.kind == "filter" and rule.filter_type.endswith("cidr"):
        net = ipaddress.ip_network(rule.value)
        if net.num_addresses > 1:
            notes.append("阻断整个 IP 子网，可能包含非广告/共享服务；CIDR 标准化未扩大原子网")
    if any("误杀" in x or "影响软件运行" in x for x in rule.context):
        notes.append("上游注释已提示误杀/影响运行，保留原文供核对")
    if rule.optional:
        notes.append("上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认")
    return notes


class Conversion:
    def __init__(self, text: str, *, dependencies=None, data_cache: Path | None = None):
        self.source = text
        self.lines = text.splitlines()
        self.rules: list[Rule] = []
        self.ledger = []
        self.original_hosts = []
        self.hosts = []
        self.hostname_audit = []
        self.mitm_rule_audit = []
        self.assets: dict[str, bytes] = {}
        self.dependencies = dependencies
        self.data_cache = data_cache
        self.icu = ICURegex()
        self.gate_errors = []
        self._parse()
        self._dependencies()
        self._deduplicate()
        self._hostnames()

    def quarantine(self, rule: Rule, reason: str, *, evidence="", alternative=""):
        rule.status = "quarantined"
        rule.evidence = evidence or "固定的 QX 官方示例、源规则及静态编译检查；详见 docs/compatibility.md"
        rule.alternative = alternative or "核对上游修复或取得 QX 实机证据后再启用"
        rule.risks.append(reason)
        rule.output = ""

    def _parse(self):
        app, hints, context = "上游未标注", [], []
        optional = False
        for no, raw in enumerate(self.lines, 1):
            text = raw.strip()
            row = {"line": no, "raw": raw}
            if not text:
                row["kind"] = "blank"
            elif is_comment(text):
                row["kind"] = "comment"
                if text.startswith("# > "):
                    app, hints, context, optional = text[4:].strip(), [], [], False
                if re.match(r"#\s*hostname\s*=", text, re.I):
                    hints = [x.strip().lower() for x in text.split("=", 1)[1].split(",") if x.strip()]
                if "如开启可自行添加主机名" in text or "已无法MITM" in text:
                    optional = True
                context.append(text)
            elif re.match(r"hostname\s*=", text, re.I):
                row["kind"] = "mitm"
                self.original_hosts.extend(x.strip().lower() for x in text.split("=", 1)[1].split(",") if x.strip())
            else:
                kind = "filter" if re.match(r"^[a-z][a-z0-9-]*\s*,", text, re.I) else "rewrite"
                try:
                    rule = parse_filter(text, no, app) if kind == "filter" else parse_rewrite(text, no, app)
                    rule.raw = raw
                    rule.hints = hints.copy()
                    rule.context = context.copy()
                    rule.optional = optional
                    for expression in ([rule.pattern, rule.header] if kind == "rewrite" else []):
                        if expression:
                            error = self.icu.error(expression)
                            if error:
                                raise ConversionError(f"ICU 正则编译失败：{error}：{expression}")
                    if rule.action in SUPPORTED_REPLACEMENTS:
                        before = rule.argument.split(f" {rule.action} ", 1)[0]
                        error = self.icu.error(before)
                        if error:
                            raise ConversionError(f"正文/头部正则编译失败：{error}")
                except (ConversionError, ValueError) as exc:
                    rule = Rule(no, raw, app, kind, hints=hints.copy(), context=context.copy())
                    alternative=(
                        "USER-AGENT 是 QX 官方支持的分流类型，但本任务要求分流只含域名/IP；"
                        "可自行将 user-agent, AVOS*, reject 加入现有 [filter_local]，本工具不改主配置"
                        if text.upper().startswith("USER-AGENT,") else
                        "可能意在匹配含 -normal-lq.zijieapi.com 的域名后缀字符串；改成 host-keyword 会改变匹配边界，需上游说明或 QX 实测后决定"
                        if text.lower().startswith("host-suffix, -normal-lq.zijieapi.com") else
                        "按官方对应语法修复后复测，不猜测删除参数")
                    self.quarantine(rule, str(exc), alternative=alternative)
                rule.features = features(rule)
                rule.risks.extend(risk_notes(rule))
                self.rules.append(rule)
                row.update(kind=kind, rule_line=no)
                context = []
            row["app"] = app
            self.ledger.append(row)
        if not self.rules or not any(r.kind == "rewrite" for r in self.rules):
            raise ConversionError("上游未识别到重写规则，拒绝生成空资源")

    def dependency_urls(self):
        result = {}
        for rule in self.rules:
            if rule.status == "quarantined":
                continue
            if rule.action in SCRIPTS:
                # Original URL is retained for audit; delivery normalization is separately logged.
                original = REWRITE_RE.fullmatch(rule.raw.strip())
                url = original[5] if original else rule.argument
                kind = "script"
            elif rule.action == "echo-response":
                url = rule.argument.rsplit(" ", 1)[1]
                kind = "json"
            elif rule.action in REDIRECTS and rule.argument.startswith("https://raw.githubusercontent.com/"):
                url, kind = rule.argument, "json"
            else:
                continue
            if url.startswith(("http://", "https://")):
                result.setdefault(url, {"kind": kind, "source_lines": []})["source_lines"].append(rule.line)
        return result

    def _dependencies(self):
        required = self.dependency_urls()
        if self.dependencies is None:
            # Inventory mode: no output may be promoted before an audited build.
            return
        for url, meta in required.items():
            check = self.dependencies.get(url)
            if not check or not check.get("ok"):
                reason = check.get("error", "没有检查结果") if check else "没有检查结果"
                self.gate_errors.append(f"远程依赖检查失败：{url}：{reason}")
                for rule in self.rules:
                    if rule.line in meta["source_lines"]:
                        self.quarantine(rule, f"远程依赖不可用/检查失败：{reason}", evidence=url,
                                        alternative="修复上游链接或提供同作者等效实现；不静默使用过期缓存")
            elif meta["kind"] == "json":
                for rule in self.rules:
                    if rule.line not in meta["source_lines"] or rule.action != "echo-response":
                        continue
                    if not self.data_cache:
                        self.gate_errors.append(f"缺少 echo-response 本地数据：{url}")
                        self.quarantine(rule, "缺少已下载 JSON 数据文件", evidence=url)
                        continue
                    data = (self.data_cache / check["cache_file"]).read_bytes()
                    if digest(data) != check["sha256"]:
                        raise ConversionError("echo-response 缓存校验不符")
                    name = "Naisi-" + digest(url.encode())[:12] + ".json"
                    self.assets["Data/" + name] = data
                    rule.argument = rule.argument.rsplit(" ", 1)[0] + " " + name
                    rule.fixes.append("echo-response 远程 JSON 改为官方明确支持的本地 Data 文件；原 URL 保存在依赖报告")
                    rule.risks.append("此条需要将配套 JSON 复制到 QX 的 Data 目录；更新后也需同步该文件")
                    rule.output = rule.render()

    def _deduplicate(self):
        seen, matchers = {}, {}
        for rule in self.rules:
            if rule.status == "quarantined":
                continue
            key = rule.duplicate_key()
            if key in seen:
                rule.status, rule.references, rule.output = "duplicate", [seen[key].line], ""
                continue
            seen[key] = rule
            if rule.kind == "rewrite":
                match = rule.match_key()
                if match in matchers:
                    previous = matchers[match]
                    if previous.action == rule.action and rule.action in JQ_ACTIONS:
                        expr = f"({jq_expression(previous.argument)}) | ({jq_expression(rule.argument)})"
                        combined = "'" + expr + "'"
                        error = jq_error(combined)
                        if error:
                            self.quarantine(rule, "同条件 JSONJQ 合并编译失败：" + error)
                        else:
                            previous.argument = combined
                            previous.fixes.append(f"与 L{rule.line} 的同条件 JSONJQ 按源顺序合并，避免仅首条生效")
                            previous.references.append(rule.line)
                            previous.output = previous.render()
                            rule.status, rule.references, rule.output = "merged", [previous.line], ""
                    else:
                        self.quarantine(rule, f"与 L{previous.line} 相同匹配条件但动作/参数冲突；保留上游靠前的行为",
                            evidence="原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）",
                            alternative=f"逐 App 实测不同返回类型后决定是否替换 L{previous.line}；本次不改变优先级")
                        rule.references = [previous.line]
                else:
                    matchers[match] = rule

    def kept(self, kind=None):
        return [r for r in self.rules if r.status == "kept" and (kind is None or r.kind == kind)]

    def _hostnames(self):
        declarations = list(dict.fromkeys(self.original_hosts))
        negatives = [h[1:] for h in declarations if h.startswith("-")]
        refs = defaultdict(list)
        # Preserve original scope only where a rewrite actually references it.
        for rule in self.kept("rewrite"):
            auth = authority(rule.pattern)
            if not auth:
                self.mitm_rule_audit.append({"line": rule.line, "app": rule.app,
                    "status": "unresolved", "reason": "不能安全提取主机部分，不自动生成 *"})
                continue
            http_only = rule.pattern.replace(r"\/", "/").startswith(("^http://", "http://", "^(http://"))
            if http_only:
                self.mitm_rule_audit.append({"line": rule.line, "app": rule.app,
                    "status": "http-only", "reason": "仅明文 HTTP，不需要 MITM"})
                continue
            explicit = finite_hosts(rule.pattern)
            declared_matches = [h for h in declarations if not h.startswith("-") and host_matches(auth, h)]
            # Whole URL alternations may put paths inside the authority group.
            # ICU partial matching then checks the author's app-local host hints.
            for hint in rule.hints:
                if hint.startswith("-") or hint in declared_matches:
                    continue
                ports = ["", ":443", ":1", ":12345"] + [":" + x for x in re.findall(r":(\d+)", rule.pattern)]
                viable = any(self.icu.prefix_viable(rule.pattern, f"https://{probe}{port}/")
                    for probe in [hint.replace("*", value).replace("?", "1") for value in ("qxprobe", "1", "a0", "b0")]
                    for port in ports)
                if viable:
                    declared_matches.append(hint)
            # Truly generic authority rules belong only to the author's app-local scope.
            if not re.search(r"(?:\\\.[a-z]|[a-z]{3,})", auth):
                declared_matches = [h for h in rule.hints if not h.startswith("-") and host_matches(auth, h)]
            tokens = declared_matches.copy()
            # Add a finite host only if the original declarations don't cover it.
            for host in explicit:
                if not any(fnmatch.fnmatchcase(host, h) for h in tokens):
                    tokens.append(host)
            if not tokens:
                tokens.extend(host_globs(rule.pattern))
            if rule.optional:
                self.mitm_rule_audit.append({"line": rule.line, "app": rule.app, "status": "optional",
                    "hosts": tokens, "reason": "上游可选/证书限制提示；不自动扩张 MITM 范围"})
                continue
            safe_tokens = []
            for token in tokens:
                if any(fnmatch.fnmatchcase(n, token) for n in negatives):
                    # Negative hostname syntax is not specified in the pinned official sample.
                    # Replace that wildcard with finite positive hosts, never lose its exclusion.
                    safe_tokens.extend(h for h in explicit if h not in negatives and fnmatch.fnmatchcase(h, token))
                elif token not in negatives and domain_valid(token, wildcards=True):
                    safe_tokens.append(token)
            safe_tokens = list(dict.fromkeys(safe_tokens))
            for token in safe_tokens:
                refs[token].append(rule.line)
            rule.hostname_refs = safe_tokens
            self.mitm_rule_audit.append({"line": rule.line, "app": rule.app,
                "status": "mapped" if safe_tokens else "unresolved", "hosts": safe_tokens,
                "reason": "已关联原声明或有限主机名" if safe_tokens else "动态主机名未找到可证实范围；需实机核对"})
        # Original order first, then conservative finite additions, deterministic on every run.
        self.hosts = [h for h in declarations if h in refs]
        self.hosts.extend(sorted(h for h in refs if h not in self.hosts))
        app_comment_tokens = {h for r in self.rules for h in r.hints}
        for token in list(dict.fromkeys(declarations + self.hosts)):
            origin = ("upstream-global" if token in declarations else "upstream-app-comment" if token in app_comment_tokens
                      else "projected-wildcard" if "*" in token or "?" in token else "finite-url-host")
            self.hostname_audit.append({"hostname": token, "source_declared": token in declarations,
                "origin": origin,
                "source_lines": sorted(set(refs.get(token, []))),
                "status": "active" if token in refs else "exclusion" if token.startswith("-") else "inactive",
                "reason": "关联有效 HTTPS 重写" if token in refs else
                    "保留排除含义：未输出相应宽泛通配符；仅输出有限正向主机" if token.startswith("-") else
                    "没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用"})

    def render(self, kind):
        title = "奶思 QX 重写（官方原版自动转换）" if kind == "rewrite" else "奶思 QX 域名/IP 分流"
        out = [f"#!name={title}", "# 来源：fmz200/wool_scripts；转换产物，非作者原文件。",
               "# 规则顺序与分类沿用上游；出处、修复、隔离见 validation-report.md / rule-inventory.json。"]
        if kind == "rewrite":
            out += ["# 资源语法需要 Quantumult X 1.5.3 或以上（JSONJQ）；脚本运行仍须实机检查。",
                    "# 仅用于重写资源；不要当作完整主配置。", "# 彩云 echo-response 需要配套 Data 文件，见 README。"]
        else:
            out += ["# 仅用于分流资源；策略 reject。已有 Cats 时先阅读 cats-comparison.md。"]
        by_line = {r.line: r for r in self.rules}
        for row in self.ledger:
            if row["kind"] == "comment":
                comment = row["raw"]
                # Prevent a remote-resource updater treating the original raw-url/name as this file's URL.
                if comment.startswith("#!"):
                    comment = "# 上游元数据 " + comment
                out.append(comment)
            elif row["kind"] == "blank":
                if out[-1] != "":
                    out.append("")
            elif row.get("rule_line"):
                rule = by_line[row["line"]]
                if rule.kind != kind:
                    continue
                if rule.status == "kept":
                    out.append(f"# 来源 L{rule.line} | {rule.app}" + (" | " + "；".join(rule.fixes) if rule.fixes else ""))
                    out.append(rule.output)
                else:
                    out.append(f"# 已{ {'duplicate':'去重','merged':'合并','quarantined':'隔离'}[rule.status]} L{rule.line}；见报告。")
        if kind == "rewrite" and self.hosts:
            out.extend(["", "# 有效 HTTPS 重写需要的主机名；不包含用户证书或任何节点配置。",
                        "hostname = " + ", ".join(self.hosts)])
        return "\n".join(out).rstrip() + "\n"

    def coverage(self):
        apps = defaultdict(lambda: Counter())
        categories = defaultdict(lambda: Counter())
        for rule in self.rules:
            for counter in [apps[rule.app]] + [categories[x] for x in rule.features]:
                counter["source"] += 1
                counter[rule.status] += 1
                if rule.status in {"kept", "duplicate", "merged"}:
                    counter["represented"] += 1
        return {"apps": {k: dict(v) for k, v in sorted(apps.items())},
                "features": {k: dict(v) for k, v in sorted(categories.items())},
                "note": "represented 包含去重/合并后仍可追溯的规则；数量是静态规则覆盖，不是广告成功率。特征由注释和匹配式推断，可重叠。"}

    def stats(self):
        counts = Counter(r.status for r in self.rules)
        return {"source_physical_lines": len(self.lines), "source_rules": len(self.rules),
                "source_rewrites": sum(r.kind == "rewrite" for r in self.rules),
                "source_filters": sum(r.kind == "filter" for r in self.rules),
                "output_rewrites": len(self.kept("rewrite")), "output_filters": len(self.kept("filter")),
                "duplicates": counts["duplicate"], "merged": counts["merged"],
                "quarantined": counts["quarantined"], "fixed_rules": sum(bool(r.fixes) for r in self.rules),
                "mitm_original": len(set(self.original_hosts)), "mitm_output": len(self.hosts),
                "mitm_added": sum(h not in self.original_hosts for h in self.hosts),
                "mitm_inactive": sum(h not in self.hosts for h in set(self.original_hosts)),
                "represented": sum(r.status in {"kept", "duplicate", "merged"} for r in self.rules)}


def cats_compare(filters: list[Rule], cats_text: str):
    rows, errors, duplicates = [], [], 0
    exact = {}
    for no, raw in enumerate(cats_text.splitlines(), 1):
        text = raw.strip()
        if not text or is_comment(text):
            continue
        try:
            rule = parse_filter(text, no, "Cats-Team")
        except ConversionError as exc:
            errors.append({"line": no, "raw": raw, "reason": str(exc)})
            continue
        key = (rule.filter_type, rule.value)
        if key in exact:
            duplicates += 1
        else:
            exact[key] = no
        rows.append(rule)
    if not rows:
        raise ConversionError("Cats 规则未识别到有效分流，不能声称已完成差集")
    suffixes = {r.value: r.line for r in rows if r.filter_type == "host-suffix"}
    keywords = {r.value: r.line for r in rows if r.filter_type == "host-keyword"}
    networks = [(ipaddress.ip_network(r.value), r.line) for r in rows if r.filter_type in {"ip-cidr", "ip6-cidr"}]
    comparison = []
    for rule in filters:
        covered, status = [], "residual"
        key = (rule.filter_type, rule.value)
        if key in exact:
            covered, status = [exact[key]], "exact"
        elif rule.filter_type in {"host", "host-suffix"}:
            labels = rule.value.split(".")
            covered = [suffixes[".".join(labels[i:])] for i in range(len(labels)) if ".".join(labels[i:]) in suffixes]
            covered += [no for kw, no in keywords.items() if kw in rule.value]
            if covered:
                status = "covered"
        elif rule.filter_type == "host-keyword":
            covered = [no for kw, no in keywords.items() if kw in rule.value]
            if covered:
                status = "covered"
        elif rule.filter_type in {"ip-cidr", "ip6-cidr"}:
            network = ipaddress.ip_network(rule.value)
            covered = [no for net, no in networks if net.version == network.version and network.subnet_of(net)]
            if covered:
                status = "covered"
        comparison.append({"source_line": rule.line, "app": rule.app, "rule": rule.output,
                           "status": status, "cats_lines": sorted(set(covered))})
    counts = Counter(x["status"] for x in comparison)
    return {"cats_rules": len(rows), "cats_duplicates": duplicates, "cats_parse_errors": errors,
            "naisi_rules": len(filters), "exact": counts["exact"], "covered": counts["covered"],
            "residual": counts["residual"], "rules": comparison,
            "scope": "residual 是未被单条 Cats 规则证明完整覆盖的候选，不是新增广告域名数；可能仍部分重叠。未比较 Cats 的 URL 重写或其他订阅。"}


def validate_outputs(conversion: Conversion, rewrite: str, filters: str):
    errors = []
    counts = Counter()
    for kind, content in (("rewrite", rewrite), ("filter", filters)):
        for no, raw in enumerate(content.splitlines(), 1):
            line = raw.strip()
            if not line or is_comment(line):
                continue
            if kind == "rewrite" and line.startswith("hostname = "):
                counts["hostname_lines"] += 1
                continue
            try:
                rule = parse_rewrite(line, repairs=False) if kind == "rewrite" else parse_filter(line)
                if rule.render() != line:
                    raise ConversionError("输出还需要隐式语法修复")
                if kind == "rewrite":
                    for p in [rule.pattern, rule.header]:
                        if p and conversion.icu.error(p):
                            raise ConversionError("输出正则编译失败")
                counts[kind] += 1
            except (ConversionError, ValueError) as exc:
                errors.append(f"{kind} 输出 L{no}: {exc}")
    if counts["rewrite"] != len(conversion.kept("rewrite")) or counts["filter"] != len(conversion.kept("filter")):
        errors.append("输出数量与可追溯清单不一致")
    if conversion.hosts and counts["hostname_lines"] != 1:
        errors.append("hostname 声明应且仅应出现一次")
    for item in conversion.hostname_audit:
        if item["status"] == "active" and not item["source_lines"]:
            errors.append("MITM 无规则出处：" + item["hostname"])
    # Every physical source line and every active rule must be accounted for.
    if len(conversion.ledger) != len(conversion.lines):
        errors.append("源行台账不完整")
    if any(r.status not in {"kept", "duplicate", "merged", "quarantined"} for r in conversion.rules):
        errors.append("存在未交代去向的规则")
    return errors
