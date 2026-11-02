from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import json


def dumps(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def cell(value):
    return str(value).replace("\n", " ").replace("|", "\\|").replace("`", "&#96;")


def coverage_report(coverage):
    out = ["# 功能覆盖对比", "", coverage["note"], "",
           "‘保留输出’是输出文件中的唯一规则；‘可追溯保留’还包含已去重、已合并的来源规则。",
           "‘隔离’不是声称该 App 没有去广告能力。原作者的分类可能包含网站、SDK 和小程序，不能当作实测 App 数量。", "",
           "## 按功能特征", "", "| 特征 | 源规则 | 保留输出 | 可追溯保留 | 隔离 |", "|---|---:|---:|---:|---:|"]
    for name, stats in coverage["features"].items():
        out.append(f"| {name} | {stats['source']} | {stats.get('kept',0)} | {stats.get('represented',0)} | {stats.get('quarantined',0)} |")
    out += ["", "## 按原作者分类（完整）", "", "| 分类 / App | 源规则 | 保留输出 | 可追溯保留 | 隔离 |", "|---|---:|---:|---:|---:|"]
    for name, stats in coverage["apps"].items():
        out.append(f"| {cell(name)} | {stats['source']} | {stats.get('kept',0)} | {stats.get('represented',0)} | {stats.get('quarantined',0)} |")
    return "\n".join(out) + "\n"


def cats_report(comparison, source_info):
    total = comparison["naisi_rules"]
    covered = comparison["exact"] + comparison["covered"]
    out = ["# 与 Cats-Team AdRules 的差集", "",
           f"奶思唯一域名/IP规则 {total} 条；Cats 解析到 {comparison['cats_rules']} 条。",
           f"完全相同 {comparison['exact']} 条；被 Cats 的其他单条规则完整覆盖 {comparison['covered']} 条；未证明完整覆盖的剩余候选 {comparison['residual']} 条。",
           f"已证明覆盖比例：{covered}/{total}（{covered / total:.2%}）。", "",
           comparison["scope"], "",
           "不能断言两套规则等效，也不能把剩余候选数换算成实际多拦截多少广告。"
           "关键词规则和 IP 网段可能有副作用；匹配不到广告流量时没有实际增益。", "",
           "建议先保留现有 Cats + Google 重定向，只增加奶思重写。"
           "剩余分流候选并非可以忽略的数量，但尚无流量命中和误杀实测，不能仅凭数量建议叠加全量分流。"
           "如重写后仍有广告，可按使用的 App 选测差集文件；全量分流与差集选一个。", "",
           f"Cats 来源：[{source_info.get('commit','main')}]({source_info.get('url','https://raw.githubusercontent.com/Cats-Team/AdRules/main/qx.conf')})。",
           "算法：先标准化类型/大小写/CIDR；再比较完全相同规则、域名父后缀、包含的 host-keyword 与同地址族的包含网段。"
           "不把更窄的 Cats 子域名误判为覆盖奶思整个父域，不把 host 与 host-suffix 当作同一种匹配范围。", "",
           f"Cats 重复规则 {comparison['cats_duplicates']} 条；解析异常 {len(comparison['cats_parse_errors'])} 条。", "",
           "## 剩余候选（完整）", "", "| 奶思原行 | App / 分类 | 规则 |", "|---:|---|---|"]
    for row in comparison["rules"]:
        if row["status"] == "residual":
            out.append(f"| {row['source_line']} | {cell(row['app'])} | `{cell(row['rule'])}` |")
    if comparison["cats_parse_errors"]:
        out += ["", "## Cats 解析异常", ""]
        for row in comparison["cats_parse_errors"]:
            out += [f"L{row['line']}：{row['reason']}", "```text", row["raw"], "```", ""]
    out += ["", "完全相同/完整覆盖的每条规则及对应 Cats 原行，见 [cats-comparison.json](cats-comparison.json)。"]
    return "\n".join(out) + "\n"


def validation_report(conversion, sources, dependencies, errors, test_results=None):
    stats = conversion.stats()
    naisi = sources.get("naisi", {})
    tests = test_results or {"status": "pending"}
    out = ["# 奶思 Quantumult X 转换验证报告", "",
           "本报告验证规则拆分、语法、出处、静态覆盖和下载结果，未运行真实 QX / iOS App。"
           "静态通过不代表 100% 实机兼容，也不代表所有广告都会消失。", "",
           "## 来源与复现", "",
           f"- 原版仓库：[{naisi.get('repo','fmz200/wool_scripts')}](https://github.com/fmz200/wool_scripts)。",
           f"- 固定输入 commit：`{naisi.get('commit','未记录')}`；日期 `{naisi.get('commit_date','未记录')}`。",
           f"- 规则地址：[{naisi.get('path','QuantumultX/rewrite/rewrite.snippet')}]({naisi.get('url','https://raw.githubusercontent.com/fmz200/wool_scripts/main/QuantumultX/rewrite/rewrite.snippet')})。",
           f"- 输入 SHA-256：`{naisi.get('sha256','未记录')}`。完整原始字节保存在 [upstream/naisi-original.snippet](upstream/naisi-original.snippet)。",
           "- 转换器固定从上述官方路径拉取；不读取 clean、compatible、v2 或其他历史修正版。",
           "- 每个物理行见 [source-ledger.json](source-ledger.json)；每条规则的原文、App、状态、修复、出处见 [rule-inventory.json](rule-inventory.json)。", "",
           "## 数量与去向", "", "| 项目 | 数量 |", "|---|---:|"]
    labels = {"source_physical_lines":"原版物理行", "source_rules":"原版有效规则行（不含注释、空行、hostname）",
        "source_rewrites":"原版重写候选", "source_filters":"原版分流候选（包括隔离的 User-Agent）",
        "output_rewrites":"输出唯一重写", "output_filters":"输出唯一域名/IP分流", "duplicates":"标准化后去重来源行",
        "merged":"合并到其他规则的来源行", "fixed_rules":"有修复说明的来源行", "quarantined":"隔离来源行",
        "represented":"可追溯保留来源行（输出+去重+合并）", "mitm_original":"上游 hostname 唯一项（含排除项）",
        "mitm_output":"输出有效 hostname 项", "mitm_added":"补充的 hostname 项", "mitm_inactive":"保留出处但未激活的上游 hostname 项"}
    for key, label in labels.items():
        out.append(f"| {label} | {stats[key]} |")
    out += ["", f"静态可追溯保留比例：{stats['represented']}/{stats['source_rules']}（{stats['represented']/stats['source_rules']:.2%}）。"
            "这是源规则的可追溯比例，不是实测功能成功率。隔离的冲突行在原匹配位置仍可能有保留的首条规则。",
            "源规则总数 = 输出重写 + 输出分流 + 去重 + 合并 + 隔离；没有未交代去向的删除。", "",
            "### 重写动作的保留对比", "", "类型按解析后动作统计，大小写修复归入同一类。", "",
            "| 动作 | 原版来源行 | 输出唯一规则 | 可追溯保留来源行 |", "|---|---:|---:|---:|"]
    source_actions = Counter(r.action for r in conversion.rules if r.kind == "rewrite")
    output_actions = Counter(r.action for r in conversion.kept("rewrite"))
    represented_actions = Counter(r.action for r in conversion.rules if r.kind == "rewrite" and r.status in {"kept", "duplicate", "merged"})
    for action in sorted(source_actions):
        out.append(f"| {action or '未识别'} | {source_actions[action]} | {output_actions[action]} | {represented_actions[action]} |")
    out += ["", "## 校验结果与范围", "",
            f"- 生成检查：{'通过' if not errors else '未通过，禁止替换有效文件'}。",
            f"- 测试：{tests.get('status')}；{tests.get('tests_run','尚未记录')} 个测试。",
            f"- ICU 库：`{conversion.icu.library}`。逐条编译 URL、头部和替换匹配式；QX 内部引擎与导入器未公开，ICU 不是实机验收。",
            "- JSONJQ：用系统 jq 编译不可执行分支；保留全部能编译的源 JSONJQ 功能，同条件表达式顺序组合。QX 内置 jq 的边界差异仍需实测。",
            "- JavaScript：下载完整文件、拒绝空响应/HTML/HTTP 错误，用 Node 解析语法；不执行第三方脚本，不证明 QX API、二进制响应、超时或 App 数据结构兼容。",
            "- 输出重新独立解析；重写中没有裸域名/IP分流，分流中没有 URL Rewrite；每个输出 hostname 关联具体有效 HTTPS 重写。",
            "- 规则语法证据、版本差异和无法确认项见 [docs/compatibility.md](docs/compatibility.md)。", ""]
    if errors:
        out += ["### 禁止发布的错误", ""] + ["- " + x for x in errors] + [""]
    out += ["## 全部修复", "", "修复数量按来源行计，不按替换次数计；大小写、类型别名、CIDR、链接和正文参数的改动均保留出处。", "",
            "| 原行 | App / 分类 | 修复说明 | 原文 | 转换结果 |", "|---:|---|---|---|---|"]
    for rule in conversion.rules:
        if rule.fixes:
            out.append(f"| {rule.line} | {cell(rule.app)} | {cell('；'.join(rule.fixes))} | `{cell(rule.raw)}` | `{cell(rule.output or rule.render())}` |")
    out += ["", "## 全部隔离（原文、原因、证据与替代）", ""]
    for rule in conversion.rules:
        if rule.status == "quarantined":
            out += [f"### L{rule.line} · {rule.app}", "", "```text", rule.raw, "```", "",
                    "原因：" + "；".join(rule.risks), "", "证据：" + rule.evidence, "", "替代：" + rule.alternative, ""]
    out += ["## 全部去重与合并", "", "同一规则即使跨 App 重复，也通过这里和规则清单保留两个 App 的原始归属。", "",
            "| 原行 | App / 分类 | 去向 | 代表原行 | 原文 |", "|---:|---|---|---|---|"]
    for rule in conversion.rules:
        if rule.status in {"duplicate", "merged"}:
            out.append(f"| {rule.line} | {cell(rule.app)} | {rule.status} | {cell(rule.references)} | `{cell(rule.raw)}` |")
    out += ["", "## MITM hostname 核对", "",
            "完整主机名清单及每项关联规则见 [hostname-audit.json](hostname-audit.json)。"
            "保留能关联 HTTPS 重写的原声明；补充有限可枚举的精确主机名，不自动生成全局 `*`。"
            "HTTP-only 规则不额外启用解密；可选/无法 MITM 的提示遵循原作者意图，不自动扩大范围。",
            "上游 `-i.vip.iqiyi.com` 的减号排除语法在固定官方示例中未得到确认；因此保留排除含义，"
            "将覆盖它的宽泛 IQIYI 通配符替换成实际规则可枚举的正向主机名。未自动解密排除主机。", "",
            "### 补充的 hostname（完整）", "", "上游全局声明缺失或范围不符时，优先沿用 App 注释，再从规则展开有限主机；动态匹配仅投影为带固定域名尾部的窄通配符。"
            "这些是静态关联推断，仍需核对 QX 实际 SNI，不代表新增主机已经实机证实可 MITM。", "",
            "| 补充主机名 | 对应原行 | 提取依据 |", "|---|---|---|"]
    for item in conversion.hostname_audit:
        if item["status"] == "active" and not item["source_declared"]:
            out.append(f"| `{cell(item['hostname'])}` | {cell(item['source_lines'])} | {item['origin']} |")
    out += ["",
            "### 未自动解决 / 可选的重写", "", "| 原行 | App | 状态 | 说明 |", "|---:|---|---|---|"]
    for item in conversion.mitm_rule_audit:
        if item["status"] in {"unresolved", "optional"}:
            out.append(f"| {item['line']} | {cell(item['app'])} | {item['status']} | {cell(item['reason'])} |")
    out += ["", "### 未激活的上游 hostname（没有丢弃出处）", "", "| 原主机名 | 状态 | 原因 |", "|---|---|---|"]
    for item in conversion.hostname_audit:
        if item["status"] != "active":
            out.append(f"| `{cell(item['hostname'])}` | {item['status']} | {cell(item['reason'])} |")
    out += ["", "## 远程脚本及数据依赖", "",
            "每行是一次完整 GET 与语法/JSON 检查的证据。检测时间保存在 JSON 清单；"
            "相同内容的再次检测记录到 logs，不为制造差异刷新产物时间。"
            "脚本内部 eval、网络加载或按环境分支的逻辑，只标记待实测，未执行或声称已经验证其二次依赖。", "",
            "| 源行 | 原始 URL | 检查 | 字节数 | 动态代码 / 内部网络 |", "|---|---|---|---:|---|"]
    for url, item in sorted(dependencies.items()):
        result = "通过" if item.get("ok") else item.get("error", "未检查")
        flags = [name for flag, name in ((item.get("dynamic_code"), "动态代码"), (item.get("runtime_fetch"), "内部网络")) if flag]
        out.append(f"| {cell(item.get('source_lines',[]))} | [{cell(url)}]({url}) | {cell(result)} | {item.get('bytes',0)} | {cell('、'.join(flags))} |")
    out += ["", "完整 HTTP 状态、最终 URL、内容摘要、脚本 API 线索及时间见 [dependency-audit.json](dependency-audit.json)。",
            "保留原作者的 main/master 等可变脚本 URL，以延续其更新能力；本报告只证明采集时的内容。"
            "失败时保留的是本项目上一版文件，无法回滚别人仓库的脚本，也无法保证 QX 后来重新下载的脚本仍与本次摘要相同。",
            "`echo-response` 官方示例要求本地 Data 文件。本次保持原 JSON 内容，"
            "只把引用改为配套 Data 文件名；该文件的后续更新需在手机同步，不能假称订阅会自动更新手机本地数据。", "",
            "## 潜在误拦截（完整关键词筛查结果）", "",
            "以下是静态风险线索，不是确认存在 bug。保留上游正常商品推荐精简行为，"
            "特别是闲鱼，不把‘推荐’一概称为广告。是否关闭某条由实机回归决定。", "",
            "| 原行 | App / 分类 | 状态 | 风险线索 |", "|---:|---|---|---|"]
    for rule in conversion.rules:
        risks = [x for x in rule.risks if "相同匹配条件" not in x]
        if risks:
            out.append(f"| {rule.line} | {cell(rule.app)} | {rule.status} | {cell('；'.join(risks))} |")
    out += ["", "## 功能对比、Cats 与实机待验", "",
            "- 全量 App / 功能类型对比：[coverage.md](coverage.md) / [coverage.json](coverage.json)。",
            "- Cats 语义去重与完整差集：[cats-comparison.md](cats-comparison.md)。",
            "- 实机验收步骤：[docs/device-checklist.md](docs/device-checklist.md)。",
            "- 尚未实机验证：QX 导入解析、脚本 API 与内置 jq 版本、MITM 合并和证书锁定、"
            "App 启动/登录/支付/订单/购物车/验证码、广告实际命中、缓存、不同 App/iOS/QX 版本、自动刷新是否加载到新脚本。",
            "- 本工具没有读取或改写用户 QX 节点、策略组、DNS、证书、主配置、Cats 订阅或 Google 重定向。", ""]
    return "\n".join(out)
