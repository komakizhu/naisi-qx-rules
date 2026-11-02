# 奶思 Quantumult X 规则转换器

从 [fmz200 官方原版](https://github.com/fmz200/wool_scripts/blob/main/QuantumultX/rewrite/rewrite.snippet)重新生成，保留开屏、弹窗、信息流、横幅及应用内脚本，分开交付重写和域名/IP分流。没有使用以往的 clean、compatible、v2 等修正版。**资源语法需要 QX 1.5.3 或以上；尚未经过完整 QX 实机验证。**

当前规则版本：`0.0.1`。为排查酷安的“网络环境异常”提示，本版隔离了奶思原版中全部酷安重写脚本，并从有效 MITM 主机名中移除 `api.coolapk.com`；不影响其他 App 规则。酷安去广告暂时停用。

## 先用哪个文件

| 文件 | 添加位置 | 建议 |
|---|---|---|
| [Naisi-QX-Rewrite.conf](Naisi-QX-Rewrite.conf) | QX「重写 → 远程资源／资源引用」 | 先启用这个。包含重写规则及所需 hostname，不是主配置。 |
| [Naisi-QX-Filter.list](Naisi-QX-Filter.list) | QX「分流 → 远程资源／资源引用」，策略 `reject` | 可选。已有 Cats-Team 时先不开，避免仅凭规则数量叠加。 |
| [Naisi-QX-Filter-Delta.list](Naisi-QX-Filter-Delta.list) | 同上，策略 `reject` | 可选，只含未被 Cats 证明完整覆盖的候选。与奶思全量分流选一个，不要同时添加。 |

保留你现在的 **Cats-Team AdRules、Google 重定向、节点、策略组、DNS 和 MITM 证书**。本项目不会修改这些配置。闲鱼等原版含有“普通推荐精简”，启用后商品推荐减少不一定属于误拦截；完整说明在报告中。

## 手机上最简单的安装方法

公开订阅地址（GitHub RAW 内容地址，不是网页预览地址）：

- 重写：[Naisi-QX-Rewrite.conf](https://raw.githubusercontent.com/komakizhu/naisi-qx-rules/main/Naisi-QX-Rewrite.conf)
- 全量分流：[Naisi-QX-Filter.list](https://raw.githubusercontent.com/komakizhu/naisi-qx-rules/main/Naisi-QX-Filter.list)
- Cats 差集候选：[Naisi-QX-Filter-Delta.list](https://raw.githubusercontent.com/komakizhu/naisi-qx-rules/main/Naisi-QX-Filter-Delta.list)
- 彩云配套数据：[Naisi-4c4c1af80d75.json](https://raw.githubusercontent.com/komakizhu/naisi-qx-rules/main/Data/Naisi-4c4c1af80d75.json)

1. 在 QX 的重写资源中添加上面的重写 RAW 地址，启用。关闭该资源的解析器选项（`opt-parser=false`），因为已经转换成 QX 原生语法。
2. 保持原有证书，确认 QX 的 MITM 开关已经启用、证书在系统中已信任。资源自带 hostname；不要覆盖主配置的原 hostname、passphrase 或 p12。
3. 下载上面的彩云 JSON 文件，复制到手机“文件 → 我的 iPhone → Quantumult X → Data”中，**保持文件名**。这只供原版彩云 `echo-response` 使用；不要把 JSON 当成分流/重写资源。只有这条本地 Data 需要额外同步。
4. 先测试闲鱼、菜鸟、淘宝、美团等正常功能，再按需决定是否添加奶思分流；分流资源强制策略选 `reject`。参见 [Cats 对比](cats-comparison.md) 和 [实机清单](docs/device-checklist.md)。

QX 主配置的引用行格式如下。用你实际托管的 RAW URL 替换说明文字，只在现有相应段内**增加行**，不要整段替换，也不要把以下示例当完整主配置导入：

```ini
[rewrite_remote]
https://raw.githubusercontent.com/komakizhu/naisi-qx-rules/main/Naisi-QX-Rewrite.conf, tag=奶思重写, update-interval=86400, opt-parser=false, enabled=true

[filter_remote]
https://raw.githubusercontent.com/komakizhu/naisi-qx-rules/main/Naisi-QX-Filter.list, tag=奶思分流, force-policy=reject, update-interval=86400, opt-parser=false, enabled=false
```

没有托管时也能手动使用：把重写文件的实际重写行加入现有 `[rewrite_local]`；把末尾 hostname 中所需项目合并到现有 `[mitm] hostname`，保留已有项目和证书；需要分流时将分流行加入现有 `[filter_local]`。这些是手动编辑步骤，本工具没有替你修改设备配置。不同 QX 版本的本地资源 UI 可能不同；本项目不编造一个未经验证的本地资源 URL 协议。

### 遇到 `Invalid Line` 和 `jsonjq-response-body`

请先在 QX「设置 → 关于」查看版本，并升级到 **1.5.3 或以上**。官方版本记录说明，QX 1.5.3 加入了处理 HTTP(S) JSON 正文的 jqlang 支持；低版本会把 `jsonjq-response-body` 识别为无效规则。升级后回到资源页面点“更新”。如果仍提示无效，请确认资源路径指向上方 RAW 地址，并把 QX 版本号和完整报错发来排查。

## 日后更新

在电脑上用 Python 3.11+、Node.js、jq、系统 ICU 运行，无 Python 第三方包。macOS 自带 ICU；当前环境已实际运行。新机器若缺少 Node/jq，先用自己的包管理器安装；本工具不会自动安装依赖。

先进入克隆或解压后的项目目录：

```bash
cd /path/to/naisi-qx-rules
python3 update.py
```

程序每次从固定官方路径解析最新 commit，再按 commit 下载原始字节；不会读取任意“修正版”作为输入。它还下载 Cats 当前规则，重新检查每个脚本/远程数据依赖，生成候选、运行全套测试，然后才替换有效文件。

公共 GitHub API 限流时，会尝试本机已有 `gh` 的只读查询，再尝试公共 `git ls-remote`；不要求登录，不改 Git 配置，不输出凭据。Actions 使用内置只读 token 查询公共来源；token 不发送给脚本站点。

- 网络、脚本、静态检查或测试失败：命令返回非零，旧产物保留。错误记录在 `logs/`；若已生成候选，详细候选报告位于 `.build/candidate/validation-report.md`。
- 新增隔离：默认停在候选，先审阅原因。需要接受已审阅隔离后运行 `python3 update.py --bootstrap`；此选项不绕过依赖失败和测试失败。
- 首次从源码生成、且没有交付基线时，使用 `python3 update.py --bootstrap`。正常日常更新不用此参数。
- 离线复现：`python3 update.py --offline`，要求已有官方快照及首次在线下载的 `.cache/dependencies/`。离线复用的是此前 HTTP 证据，不声称当前仍可访问；压缩包不包含第三方脚本缓存，首次使用需在线运行。
- 只审阅候选：`python3 update.py --candidate-dir .build/review`。通过后用 `python3 update.py --promote .build/review` 提升；不通过的候选不能提升。
- 相同输入重复执行，产物字节保持一致，逐次检查时间只追加到日志。测试命令：`python3 -m unittest discover -s tests -v`。

自动更新有两步：电脑或 GitHub Actions 生成并托管新文件；QX 再按远程资源更新间隔刷新。仅在电脑运行，不会让手机从这台电脑自动取得文件。彩云 Data 文件须另行同步，不能声称它会随远程订阅自动更新。

原作者脚本的 main/master URL 继续保留更新能力，因此仍可被上游改动。失败保护保留的是本项目已有文件，不能回滚别人的脚本仓库，也不能保证 QX 日后下载到的脚本仍与本次检查相同。完整脚本锁定/镜像不属于本次交付。

## GitHub Actions 自动更新

[自动更新工作流](.github/workflows/update.yml)每天北京时间 05:23 检查奶思原版和依赖；只有转换、依赖检查和测试全部通过后，才会更新本仓库中的订阅文件。QX 按资源的 `update-interval=86400` 每天刷新一次。也可以在 GitHub Actions 页面手动运行工作流；手动发布选项默认关闭。工作流失败会保留当前有效订阅，并上传诊断文件供排查。

如果 GitHub 的分支保护拒绝推送，工作流失败并保留检查文件，不强推、不绕过保护。自动更新提交只改转换清单指定的规则、报告和官方快照，不触碰用户的 QX 主配置。

## 报告与出处

- [完整验证报告](validation-report.md)：总数、修复、去重、隔离、依赖和 MITM，明确尚未实机验证。
- [覆盖对比](coverage.md)：全部原作者分类及功能类型，数量可复核，不是广告成功率。
- [Cats 语义差集](cats-comparison.md)：区分完全相同、被父域/关键词/网段覆盖和剩余候选，不能断言两套等效。
- [官方语法与版本调查](docs/compatibility.md)、[官方原版及来源摘要](upstream/sources.json)、[逐行台账](source-ledger.json)、[规则原文与去向](rule-inventory.json)。

规则及衍生成果保留奶思原作者署名和上游 [GPL-3.0 许可证](LICENSE)。远程脚本 URL 尽量不变，GitHub `/raw/` 端点只规范化交付地址；脚本内部网络和 QX API 未进行实机运行。其他作者资源保留原出处，详见 [NOTICE.md](NOTICE.md)。
