# Quantumult X 语法调查与兼容边界

本项目先调查官方文档，再写转换器。规则格式以官方仓库固定版本
[`af6fb594233ec4a3ec6d4ccb3601e9c36b75ea2d`](https://github.com/crossutility/Quantumult-X/tree/af6fb594233ec4a3ec6d4ccb3601e9c36b75ea2d)
为可复现依据，而不是把个人记忆当作 QX 规范。

## 四种判断

| 判断 | 项目 | 证据与本项目处理 |
|---|---|---|
| 官方明确支持 | `[rewrite_remote]` / `[rewrite_local]`、`[filter_remote]` / `[filter_local]` | [官方 sample.conf](https://github.com/crossutility/Quantumult-X/blob/af6fb594233ec4a3ec6d4ccb3601e9c36b75ea2d/sample.conf)。前两者加载重写，后两者加载分流；remote 行是资源引用，local 中放实际规则。 |
| 官方明确支持 | `host`、`host-suffix`、`host-keyword`、`ip-cidr`、`ip6-cidr` | [官方分流示例](https://github.com/crossutility/Quantumult-X/blob/af6fb594233ec4a3ec6d4ccb3601e9c36b75ea2d/filter.snippet)及 sample.conf 的 filter_local。只转换类型别名、大小写和同一 CIDR 的网络地址。 |
| 官方明确支持 | `url reject/reject-img/reject-200/reject-dict/reject-array`、302/307 | sample.conf 的 rewrite_local。保留原作者选定的返回类型，不把所有 reject 动作强行变成同一种。 |
| 官方明确支持 | `script-request-header`、`script-request-body`、`script-response-header`、`script-response-body`、`script-echo-response`、`script-analyze-echo-response` | sample.conf 明确列出。`script-analyze-echo-response` 会等待请求正文，不等同于响应正文脚本。 |
| 官方明确支持 | `request-body`、`response-body`、`request-header` | [rewrite.md](https://github.com/crossutility/Quantumult-X/blob/af6fb594233ec4a3ec6d4ccb3601e9c36b75ea2d/rewrite.md)与 sample.conf。格式为 `URL url response-body 匹配式 response-body 替换文本`；保留替换文本中的空格和 `$1`。 |
| 依赖版本支持 | `jsonjq-request-body` / `jsonjq-response-body` | [开发者在 App Store 的版本历史](https://apps.apple.com/us/app/quantumult-x/id1443988620)：1.5.2，2025-07-18，新增 jqlang；当前官方 sample.conf 给出单引号表达式示例。本完整集最低资源语法要求是 **QX 1.5.2 正式版**，不是对远程脚本全部 API 的最低版本保证。 |
| 依赖版本支持 | `url-and-header` | App Store 版本历史 1.2.0（2022-12-19）引入；官方示例 URL 和 header 两个正则都匹配才执行。菜鸟、闲鱼的 HTTPDNS 规则属于此类，不能误认成未知动作删除。 |
| 依赖版本支持 | `host-wildcard` | App Store 版本历史 1.0.31（2022-08-19）引入，支持 `*` 和 `?`；不把 host-suffix 粗暴改成通配符。 |
| 官方明确支持 | 资源中的 `hostname = ...` | [官方远程重写片段](https://github.com/crossutility/Quantumult-X/blob/af6fb594233ec4a3ec6d4ccb3601e9c36b75ea2d/sample-import-rewrite.snippet)。资源内 hostname 是可选行；主配置 `[mitm]` 的证书、密码和解密开关仍由用户管理。 |
| 官方明确支持 | MITM 的 `*`、`?` | sample.conf 的 mitm 注释说明 SNI / 目标地址匹配与通配符。仅收录能关联有效 HTTPS 重写的主机名；不生成全局 `*`。 |
| 官方明确支持 | 本地脚本和本地 Data | sample.conf：本地脚本存放在设备或 iCloud 的 Quantumult X/Scripts；`echo-response` 数据存放在“我的 iPhone / Quantumult X / Data”。规则引用文件名，例如官方示例 `echo-response ... index.html`；不是 macOS 绝对路径。 |
| 依赖版本支持 | HTTP(S) 远程脚本、URL fragment 参数 | [官方 sample-task.js](https://github.com/crossutility/Quantumult-X/blob/af6fb594233ec4a3ec6d4ccb3601e9c36b75ea2d/sample-task.js)明确说明 HTTP(S) 脚本与 hash 参数适用于 rewrite/task。`$environment.variables` 则到 1.5.6 build 918 才支持；不能把可下载等同于老版都能执行脚本。 |
| 官方明确支持 | `opt-parser` | sample.conf 引用 `[general] resource_parser_url` 并演示资源 `opt-parser=true`；[官方 resource-parser.js](https://github.com/crossutility/Quantumult-X/blob/af6fb594233ec4a3ec6d4ccb3601e9c36b75ea2d/resource-parser.js)收到 `$resource.content`，通过 `$done({content:...})` 返回转换结果。它调用配置好的解析脚本，不会自行理解所有语法或修好坏链接。本项目已输出原生 QX 片段，使用 `opt-parser=false`，不用改用户全局解析器。 |
| 依赖版本支持 | 资源解析器接口 | resource-parser.js 注明基础接口支持 1.0.8 build 253；UA 重试字段到 1.5.6 build 921。当前转换在 Python 中进行，不依赖这些新字段。 |
| 无法确认 | `echo-response` 直接跟远程 JSON URL | 固定官方示例明确要求本地 Data；没有据此证实所有版本禁止远程 URL，也没有足够证据保证远程 URL 可用。本次最小修复为下载原 JSON、交付相同内容的 Data 文件、只改引用文件名，**不声称远程写法在所有版本均不支持**。 |
| 无法确认 | hostname 减号排除语法 | 固定官方示例只明确通配符，未给出 `-i.vip.iqiyi.com` 排除写法。保留该项审计记录；将包含它的宽泛通配符替换为实际规则的有限正向主机，避免丢掉排除含义。 |
| 无法确认 | 手机上的本地资源 UI 和本地资源引用字符串在各版的差异 | 官方资源解析器说明 `$resource.link` 可是本地路径，但固定样例没有给出统一跨版本的资源引用字符串。README 优先使用远程 RAW URL；离线手动方式只使用明确支持的 rewrite_local/filter_local 行，不编造 `file://`、绝对路径或特殊 `local://` 协议。 |
| 无法确认 | QX 内部正则引擎完整行为、内置 jq 的具体版本、所有脚本 API / 响应形状、证书锁定 | 通过 ICU 编译、jq 编译、Node 解析与源代码线索进行静态检查；QX 导入、网络命中和 App 行为仍须实机。源码中的原作者证书限制提示按“上游提示，未独立实测”报告。 |
| 明确不符合本次输出格式 | `DOMAIN, ...`、`IP-CIDR` 大写、`- reject-200` | 输出严格按官方 QX 样例统一为 `host` / `ip-cidr` / `url reject-200`；这表示本转换器的原生格式要求，不推断 QX 所有版本都拒绝大小写或别名。 |
| 明确不支持的解析上下文 | 在资源解析器中使用网络请求或持久存储 API | resource-parser.js 明确说明此限制；所以不用 opt-parser 在设备内额外下载脚本、做联网验证或维护下载缓存。 |

## 分离与加载

重写远程文件只放规则和 hostname，**不放** `[rewrite_remote]`、`[rewrite_local]` 或完整配置段。分流远程文件只放域名/IP规则与注释，**不放** `[filter_remote]` 段。这些段名属于主配置：remote 段内放订阅地址，local 段内才放实际规则。

本项目按用户要求彻底拆分资源。不能反向推断“任何 QX 版本都不允许混合资源”：资源解析能力会随版本变化，原版混排和语法真的无效是两件事。即使新版有容错/混合资源能力，拆分也便于明确策略、单独开关及与 Cats 去重。

官方 sample.conf 说明远程资源默认更新间隔为 86400 秒，可用 `update-interval` 设置；实际后台执行和脚本缓存行为还受 QX/iOS 状态影响。本次没有改写设备主配置，也没有为用户开启任何订阅。

## 校验引擎的限制

ICU 编译可发现无效括号、字符类、重复量词等问题，但不是 QX 内部导入器。MITM 关联使用有限主机展开、正向通配范围和 ICU 前缀检查；含未转义点、跨域路径分支、动态 IP 等会单列审计，关联不等于广告必然命中。

外部 `jq` 只编译表达式，不用虚构 API 响应替代实机数据。组合两条同条件 JSONJQ 会按原顺序串联，测试使用结构明确的合成样本验证两步均生效；快手真实数据形状仍未验证。

第三方 JavaScript 只被解析，未在本机执行。Node 能解析的语法不一定在特定 QX JS 引擎中可用；API 检测、动态代码和内部网络请求在依赖报告中可见。直连脚本可访问不代表脚本内部再次下载的内容全部可用。

## 本机调查证据

固定官方文件随交付保存到 [upstream/](../upstream/)，下载地址、仓库 commit 和 SHA-256 见 [sources.json](../upstream/sources.json)。App Store 版本结论与出处也保存在此文档，未将整页第三方评论当作技术依据。
