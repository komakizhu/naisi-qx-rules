# 奶思 Quantumult X 转换验证报告

本报告验证规则拆分、语法、出处、静态覆盖和下载结果，未运行真实 QX / iOS App。静态通过不代表 100% 实机兼容，也不代表所有广告都会消失。

## 来源与复现

- 原版仓库：[fmz200/wool_scripts](https://github.com/fmz200/wool_scripts)。
- 固定输入 commit：`4b7830670baf235ed945085cb926dc499cf619e0`；日期 `2026-10-30T16:03:23Z`。
- 规则地址：[QuantumultX/rewrite/rewrite.snippet](https://raw.githubusercontent.com/fmz200/wool_scripts/4b7830670baf235ed945085cb926dc499cf619e0/QuantumultX/rewrite/rewrite.snippet)。
- 输入 SHA-256：`371ee2dee23f6aee74017f23e54d42a6d19a1b84f9fc7c63e2f70f59abbe4b9a`。完整原始字节保存在 [upstream/naisi-original.snippet](upstream/naisi-original.snippet)。
- 转换器固定从上述官方路径拉取；不读取 clean、compatible、v2 或其他历史修正版。
- 每个物理行见 [source-ledger.json](source-ledger.json)；每条规则的原文、App、状态、修复、出处见 [rule-inventory.json](rule-inventory.json)。

## 数量与去向

| 项目 | 数量 |
|---|---:|
| 原版物理行 | 7401 |
| 原版有效规则行（不含注释、空行、hostname） | 4383 |
| 原版重写候选 | 1622 |
| 原版分流候选（包括隔离的 User-Agent） | 2761 |
| 输出唯一重写 | 1597 |
| 输出唯一域名/IP分流 | 2667 |
| 标准化后去重来源行 | 96 |
| 合并到其他规则的来源行 | 1 |
| 有修复说明的来源行 | 81 |
| 隔离来源行 | 22 |
| 可追溯保留来源行（输出+去重+合并） | 4361 |
| 上游 hostname 唯一项（含排除项） | 966 |
| 输出有效 hostname 项 | 993 |
| 补充的 hostname 项 | 74 |
| 保留出处但未激活的上游 hostname 项 | 47 |

静态可追溯保留比例：4361/4383（99.50%）。这是源规则的可追溯比例，不是实测功能成功率。隔离的冲突行在原匹配位置仍可能有保留的首条规则。
源规则总数 = 输出重写 + 输出分流 + 去重 + 合并 + 隔离；没有未交代去向的删除。

### 重写动作的保留对比

类型按解析后动作统计，大小写修复归入同一类。

| 动作 | 原版来源行 | 输出唯一规则 | 可追溯保留来源行 |
|---|---:|---:|---:|
| 302 | 3 | 3 | 3 |
| echo-response | 1 | 1 | 1 |
| jsonjq-response-body | 32 | 31 | 32 |
| reject | 532 | 524 | 527 |
| reject-200 | 243 | 234 | 234 |
| reject-dict | 454 | 452 | 453 |
| reject-img | 113 | 111 | 111 |
| response-body | 28 | 28 | 28 |
| script-analyze-echo-response | 1 | 1 | 1 |
| script-request-body | 1 | 1 | 1 |
| script-request-header | 2 | 2 | 2 |
| script-response-body | 211 | 208 | 208 |
| script-response-header | 1 | 1 | 1 |

## 校验结果与范围

- 生成检查：通过。
- 测试：passed；48 个测试。
- ICU 库：`/usr/lib/libicucore.dylib`。逐条编译 URL、头部和替换匹配式；QX 内部引擎与导入器未公开，ICU 不是实机验收。
- JSONJQ：用系统 jq 编译不可执行分支；保留全部能编译的源 JSONJQ 功能，同条件表达式顺序组合。QX 内置 jq 的边界差异仍需实测。
- JavaScript：下载完整文件、拒绝空响应/HTML/HTTP 错误，用 Node 解析语法；不执行第三方脚本，不证明 QX API、二进制响应、超时或 App 数据结构兼容。
- 输出重新独立解析；重写中没有裸域名/IP分流，分流中没有 URL Rewrite；每个输出 hostname 关联具体有效 HTTPS 重写。
- 规则语法证据、版本差异和无法确认项见 [docs/compatibility.md](docs/compatibility.md)。

## 全部修复

修复数量按来源行计，不按替换次数计；大小写、类型别名、CIDR、链接和正文参数的改动均保留出处。

| 原行 | App / 分类 | 修复说明 | 原文 | 转换结果 |
|---:|---|---|---|---|
| 85 | 2345天气王 | 将 http?: 修成 https?:；原式只匹配 htt/http，遗漏 HTTPS | `^http?:\/\/tianqi\.2345\.com\/api\/content\/getContentFeeds\.php url reject-dict` | `^https?:\/\/tianqi\.2345\.com\/api\/content\/getContentFeeds\.php url reject-dict` |
| 386 | 阿里云 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject；CIDR 网络地址标准化：203.107.1.1/24 → 203.107.1.0/24（同一子网） | `IP-CIDR, 203.107.1.1/24, reject` | `ip-cidr, 203.107.1.0/24, reject` |
| 457 | 爱奇艺 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 203.107.63.154/32, reject` | `ip-cidr, 203.107.63.154/32, reject` |
| 458 | 爱奇艺 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 101.227.97.240/32, reject` | `ip-cidr, 101.227.97.240/32, reject` |
| 459 | 爱奇艺 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 101.227.200.11/32, reject` | `ip-cidr, 101.227.200.11/32, reject` |
| 460 | 爱奇艺 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 101.227.200.28/32, reject` | `ip-cidr, 101.227.200.28/32, reject` |
| 461 | 爱奇艺 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 124.192.153.42/32, reject` | `ip-cidr, 124.192.153.42/32, reject` |
| 859 | 百度贴吧 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 180.76.76.200/32, reject` | `ip-cidr, 180.76.76.200/32, reject` |
| 1134 | 彩云天气 | echo-response 远程 JSON 改为官方明确支持的本地 Data 文件；原 URL 保存在依赖报告 | `^https?:\/\/wrapper\.cyapi\.cn\/v1\/activity\? url echo-response application/json echo-response https://raw.githubusercontent.com/Keywos/rule/main/mocks/caiyun.json` | `^https?:\/\/wrapper\.cyapi\.cn\/v1\/activity\? url echo-response application/json echo-response Naisi-4c4c1af80d75.json` |
| 1371 | 滴滴青桔 | CIDR 网络地址标准化：203.107.1.1/24 → 203.107.1.0/24（同一子网） | `ip-cidr, 203.107.1.1/24, reject` | `ip-cidr, 203.107.1.0/24, reject` |
| 1528 | 斗鱼直播 | 斗鱼 getStartSend 后的查询问号转义为字面字符；原式把前一个字母设为可选 | `^https?:\/\/capi\.douyucdn\.cn\/api\/v1\/getStartSend?client_sys=ios url reject-img` | `^https?:\/\/capi\.douyucdn\.cn\/api\/v1\/getStartSend\?client_sys=ios url reject-img` |
| 1559 | Dr.Peng | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 211.161.101.110/32, reject` | `ip-cidr, 211.161.101.110/32, reject` |
| 1632 | 番茄小说 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 49.71.37.101/32, reject` | `ip-cidr, 49.71.37.101/32, reject` |
| 1633 | 番茄小说 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 117.71.105.23/32, reject` | `ip-cidr, 117.71.105.23/32, reject` |
| 1634 | 番茄小说 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 218.94.207.205/32, reject` | `ip-cidr, 218.94.207.205/32, reject` |
| 1635 | 番茄小说 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 117.92.229.188/32, reject` | `ip-cidr, 117.92.229.188/32, reject` |
| 1636 | 番茄小说 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 101.36.166.16/32, reject` | `ip-cidr, 101.36.166.16/32, reject` |
| 1637 | 番茄小说 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 180.96.2.114/32, reject` | `ip-cidr, 180.96.2.114/32, reject` |
| 2061 | 航旅纵横 | 将 http?: 修成 https?:；原式只匹配 htt/http，遗漏 HTTPS | `^http?:\/\/(discardrp\|startup)\.umetrip\.com\/gateway\/api\/umetrip\/native url reject` | `^https?:\/\/(discardrp\|startup)\.umetrip\.com\/gateway\/api\/umetrip\/native url reject` |
| 2062 | 航旅纵横 | 将 http?: 修成 https?:；原式只匹配 htt/http，遗漏 HTTPS；航旅纵横主机二选一补成同一组，使协议、路径和结尾同时约束两个分支，避免 IP 分支匹配全部路径 | `^http?:\/\/(114\.115\.217\.129)\|(home\.umetrip\.com)\/gateway\/api\/umetrip\/native$ url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/umetrip/umetrip_ads.js` | `^https?:\/\/(114\.115\.217\.129\|home\.umetrip\.com)\/gateway\/api\/umetrip\/native$ url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/umetrip/umetrip_ads.js` |
| 2272 | Huawei AspiegelBot | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 114.119.160.0/21, reject` | `ip-cidr, 114.119.160.0/21, reject` |
| 2361 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,clk.gentags.net, reject` | `host-keyword, clk.gentags.net, reject` |
| 2362 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,dm.pstatp.com, reject` | `host-keyword, dm.pstatp.com, reject` |
| 2363 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,dm.bytedance.com, reject` | `host-keyword, dm.bytedance.com, reject` |
| 2364 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,uop.umeng.com, reject` | `host-keyword, uop.umeng.com, reject` |
| 2365 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,m.suning.com, reject` | `host-keyword, m.suning.com, reject` |
| 2366 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,adshare.toutiao.com, reject` | `host-keyword, adshare.toutiao.com, reject` |
| 2367 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,tunion-api.m.taobao.com, reject` | `host-keyword, tunion-api.m.taobao.com, reject` |
| 2368 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,s1.pstatp.com, reject` | `host-keyword, s1.pstatp.com, reject` |
| 2369 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,s2.pstatp.com, reject` | `host-keyword, s2.pstatp.com, reject` |
| 2370 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,s3.pstatp.com, reject` | `host-keyword, s3.pstatp.com, reject` |
| 2371 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,a3.pstatp.com, reject` | `host-keyword, a3.pstatp.com, reject` |
| 2372 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,a3.bytecdn.cn, reject` | `host-keyword, a3.bytecdn.cn, reject` |
| 2476 | 京东 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 101.124.19.122/32, reject` | `ip-cidr, 101.124.19.122/32, reject` |
| 2477 | 京东 | 规则类型/动作标准化：IP6-CIDR → ip6-cidr，策略 reject | `IP6-CIDR, 2402:db40:5100:1011::5/128, reject` | `ip6-cidr, 2402:db40:5100:1011::5/128, reject` |
| 2551 | 肯德基 | 肯德基域名误写的 \c 控制字符改为字面域名点，与源注释 res.kfc.com.cn 一致 | `^https?:\/\/res\.kfc\.com.\cn\/advertisement\/ url reject` | `^https?:\/\/res\.kfc\.com\.cn\/advertisement\/ url reject` |
| 2698 | 快手 | 与 L2700 的同条件 JSONJQ 按源顺序合并，避免仅首条生效 | `^https:\/\/(apissl\|az2-api(-js\|-idc)?)\.(gifshow\|ksapisrv)\.com\/rest\/system\/startup\? url jsonjq-response-body 'del(.reskinConfig.sidebarExSquareStyle.moreList, .reskinConfig.sidebarExSquareStyle.topList)'` | `^https:\/\/(apissl\|az2-api(-js\|-idc)?)\.(gifshow\|ksapisrv)\.com\/rest\/system\/startup\? url jsonjq-response-body '(del(.reskinConfig.sidebarExSquareStyle.moreList, .reskinConfig.sidebarExSquareStyle.topList)) \| (.sidebarExSquareStyle.commonlyUsedList \|= map(select(.title == "设置" or .title == "历史记录" or .title == "草稿箱" or .title == "我的钱包" or .title == "小程序" or .title == "未成年人模式" or .title == "官方客服" or .title == "内容偏好" or .title == "离线模式" or .title == "稍后再看" or .title == "举报中心" or .title == "挂件")))'` |
| 3141 | 美丽修行 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https:\/\/api\.bevol\.com\/(?:appmain\/app\/home\/page\|usercenter\/account\/info\|personal\/page\|appmain\/app\/home\/launch\|trialbox\/shop\/app\/homePage)$ url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/mlxx/mlxx.js` | `^https:\/\/api\.bevol\.com\/(?:appmain\/app\/home\/page\|usercenter\/account\/info\|personal\/page\|appmain\/app\/home\/launch\|trialbox\/shop\/app\/homePage)$ url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/mlxx/mlxx.js` |
| 3289 | 墨迹天气 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,me.api.moji.com, reject` | `host-keyword, me.api.moji.com, reject` |
| 3290 | 墨迹天气 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,android.bugly.qq.com, reject` | `host-keyword, android.bugly.qq.com, reject` |
| 3291 | 墨迹天气 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,av1.xdrig.com, reject` | `host-keyword, av1.xdrig.com, reject` |
| 3292 | 墨迹天气 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,adash.man.aliyuncs.com, reject` | `host-keyword, adash.man.aliyuncs.com, reject` |
| 3549 | 朴朴超市 | 重写操作符/动作改为官方示例的小写 | `^http:\/\/139\.196\.12\.179:8053\/httpdns\/ url REJECT` | `^http:\/\/139\.196\.12\.179:8053\/httpdns\/ url reject` |
| 3550 | 朴朴超市 | 重写操作符/动作改为官方示例的小写 | `^http:\/\/106\.55\.220\.18:8053\/httpdns\/ url REJECT` | `^http:\/\/106\.55\.220\.18:8053\/httpdns\/ url reject` |
| 3551 | 朴朴超市 | 重写操作符/动作改为官方示例的小写 | `^http:\/\/54\.222\.159\.138:8053\/httpdns\/ url REJECT` | `^http:\/\/54\.222\.159\.138:8053\/httpdns\/ url reject` |
| 3552 | 朴朴超市 | 重写操作符/动作改为官方示例的小写 | `^http:\/\/101\.42\.130\.147\/httpdns\/resolve\/ url REJECT` | `^http:\/\/101\.42\.130\.147\/httpdns\/resolve\/ url reject` |
| 3554 | 朴朴超市 | 重写操作符/动作改为官方示例的小写 | `^https:\/\/j1\.pupuapi\.com\/client\/member_card\/index\/my url REJECT` | `^https:\/\/j1\.pupuapi\.com\/client\/member_card\/index\/my url reject` |
| 3566 | 朴朴超市 | 为 JSONJQ 表达式补齐官方示例使用的外层单引号 | `^https:\/\/j1\.pupuapi\.com\/client\/notification\/message_center\/unread_number url jsonjq-response-body .data = []` | `^https:\/\/j1\.pupuapi\.com\/client\/notification\/message_center\/unread_number url jsonjq-response-body '.data = []'` |
| 3844 | QQ音乐 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 120.222.240.171/32, reject` | `ip-cidr, 120.222.240.171/32, reject` |
| 4313 | Soul | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 47.56.131.76/32, reject` | `ip-cidr, 47.56.131.76/32, reject` |
| 4314 | Soul | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 47.97.215.55/32, reject` | `ip-cidr, 47.97.215.55/32, reject` |
| 4315 | Soul | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 47.99.42.29/32, reject` | `ip-cidr, 47.99.42.29/32, reject` |
| 4316 | Soul | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 120.27.235.201/32, reject` | `ip-cidr, 120.27.235.201/32, reject` |
| 4317 | Soul | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 121.196.197.147/32, reject` | `ip-cidr, 121.196.197.147/32, reject` |
| 5399 | 下厨房 | 将 http?: 修成 https?:；原式只匹配 htt/http，遗漏 HTTPS | `^http?:\/\/.*\.pglstatp-toutiao\.com url reject-200` | `^https?:\/\/.*\.pglstatp-toutiao\.com url reject-200` |
| 5516 | 小红书 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https?:\/\/edith\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/search\/(banner_list\|hot_list) url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js` | `^https?:\/\/edith\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/search\/(banner_list\|hot_list) url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaohongshu/xiaohongshu.js` |
| 5517 | 小红书 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https?:\/\/edith\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/search\/(hint\|trending)\? url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js` | `^https?:\/\/edith\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/search\/(hint\|trending)\? url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaohongshu/xiaohongshu.js` |
| 5518 | 小红书 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https?:\/\/(so\|edith)\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/search\/notes\? url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js` | `^https?:\/\/(so\|edith)\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/search\/notes\? url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaohongshu/xiaohongshu.js` |
| 5520 | 小红书 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https?:\/\/edith\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/system_service\/config\? url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js` | `^https?:\/\/edith\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/system_service\/config\? url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaohongshu/xiaohongshu.js` |
| 5521 | 小红书 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https?:\/\/edith\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/system_service\/splash_config url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js` | `^https?:\/\/edith\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/system_service\/splash_config url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaohongshu/xiaohongshu.js` |
| 5523 | 小红书 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https?:\/\/edith\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/note\/widgets url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js` | `^https?:\/\/edith\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/note\/widgets url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaohongshu/xiaohongshu.js` |
| 5527 | 小红书 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https?:\/\/(edith\|rec\|www)\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/note\/(imagefeed\|live_photo\/save) url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js` | `^https?:\/\/(edith\|rec\|www)\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/note\/(imagefeed\|live_photo\/save) url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaohongshu/xiaohongshu.js` |
| 5528 | 小红书 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https?:\/\/(edith\|rec\|www)\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/(followfeed\|homefeed)\? url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js` | `^https?:\/\/(edith\|rec\|www)\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/(followfeed\|homefeed)\? url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaohongshu/xiaohongshu.js` |
| 5529 | 小红书 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https?:\/\/(edith\|rec\|www)\.(xiaohongshu\|rnote)\.com\/api\/sns\/(v2\/note\/feed\|v3\/note\/videofeed)\? url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js` | `^https?:\/\/(edith\|rec\|www)\.(xiaohongshu\|rnote)\.com\/api\/sns\/(v2\/note\/feed\|v3\/note\/videofeed)\? url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaohongshu/xiaohongshu.js` |
| 5530 | 小红书 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https?:\/\/(edith\|rec\|www)\.(xiaohongshu\|rnote)\.com\/api\/sns\/(v4\/note\/videofeed\|v10\/note\/video\/save)\? url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js` | `^https?:\/\/(edith\|rec\|www)\.(xiaohongshu\|rnote)\.com\/api\/sns\/(v4\/note\/videofeed\|v10\/note\/video\/save)\? url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaohongshu/xiaohongshu.js` |
| 5561 | 小米 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD, XiaoQiang, reject` | `host-keyword, xiaoqiang, reject` |
| 5728 | 晓晓优选 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 114.132.165.205/32, reject` | `ip-cidr, 114.132.165.205/32, reject` |
| 6186 | 优酷 | 规则类型/动作标准化：DOMAIN → host，策略 reject | `DOMAIN, httpdns.alicdn.com, reject` | `host, httpdns.alicdn.com, reject` |
| 6187 | 优酷 | 规则类型/动作标准化：DOMAIN → host，策略 reject | `DOMAIN, adsmind.ugdtimg.com, reject` | `host, adsmind.ugdtimg.com, reject` |
| 6188 | 优酷 | 规则类型/动作标准化：DOMAIN → host，策略 reject | `DOMAIN, amdc.m.youku.com, reject` | `host, amdc.m.youku.com, reject` |
| 6189 | 优酷 | 规则类型/动作标准化：DOMAIN → host，策略 reject | `DOMAIN, apiv4-iyes.youku.com, reject` | `host, apiv4-iyes.youku.com, reject` |
| 6192 | 优酷 | 规则类型/动作标准化：DOMAIN → host，策略 reject | `DOMAIN, yk-ssp.ad.youku.com, reject` | `host, yk-ssp.ad.youku.com, reject` |
| 6193 | 优酷 | 规则类型/动作标准化：DOMAIN → host，策略 reject | `DOMAIN, ykad-data.youku.com, reject` | `host, ykad-data.youku.com, reject` |
| 6194 | 优酷 | 规则类型/动作标准化：DOMAIN → host，策略 reject | `DOMAIN, ad.mobile.youku.com, reject` | `host, ad.mobile.youku.com, reject` |
| 6293 | 邮储银行 | 将其他软件的 ‘- reject-*’ 写法转换为 QX ‘url reject-*’ | `^https?:\/\/static.psbc.com:8090\/mbank_f\/images\/[0-9]+\.png - reject-200` | `^https?:\/\/static.psbc.com:8090\/mbank_f\/images\/[0-9]+\.png url reject-200` |
| 6551 | 知乎 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 118.89.204.198/32, reject` | `ip-cidr, 118.89.204.198/32, reject` |
| 6552 | 知乎 | 规则类型/动作标准化：IP6-CIDR → ip6-cidr，策略 reject | `IP6-CIDR,2402:4e00:1200:ed00:0:9089:6dac:96b6/128, reject` | `ip6-cidr, 2402:4e00:1200:ed00:0:9089:6dac:96b6/128, reject` |
| 6640 | 中国电信 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 122.229.8.47/32, reject` | `ip-cidr, 122.229.8.47/32, reject` |
| 6641 | 中国电信 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 122.229.29.89/32, reject` | `ip-cidr, 122.229.29.89/32, reject` |
| 6716 | 中国移动 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 120.240.95.37/32, reject` | `ip-cidr, 120.240.95.37/32, reject` |
| 7167 | 广告联盟 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD, mathtag, reject` | `host-keyword, mathtag, reject` |

## 全部隔离（原文、原因、证据与替代）

### L803 · 百度

```text
^https?:\/\/baichuan\.baidu\.com\/rs\/adpmobile\/launch url reject-img
```

原因：与 L802 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L802；本次不改变优先级

### L806 · 百度

```text
^https?:\/\/afd\.baidu\.com\/afd\/entry url reject-img
```

原因：与 L805 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L805；本次不改变优先级

### L848 · 百度输入法

```text
^https?:\/\/mime\.baidu\.com\/v5\/start_screen_ads/list url reject-dict
```

原因：与 L843 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L843；本次不改变优先级

### L2571 · 酷安

```text
^https?:\/\/api\.coolapk\.com\/v6\/feed\/(detail|replyList)\? url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/coolapk.js
```

原因：按用户要求暂时停用酷安重写，排查网络环境检测；不再对 api.coolapk.com 做 MITM

证据：用户提供的酷安提示将去广告、DNS、Hosts、代理列为可能原因，并反馈关闭 Quantumult X 后恢复；上游酷安分类对 api.coolapk.com 的首页、动态和帖子响应执行脚本修改。该证据说明存在关联风险，不能证明它是唯一原因。

替代：确认酷安恢复后，若要重新启用去广告，先逐条验证规则；本次不恢复 api.coolapk.com 的 MITM。

### L2572 · 酷安

```text
^https?:\/\/api\.coolapk\.com\/v6\/main\/(dataList|indexV8|init) url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/coolapk.js
```

原因：按用户要求暂时停用酷安重写，排查网络环境检测；不再对 api.coolapk.com 做 MITM

证据：用户提供的酷安提示将去广告、DNS、Hosts、代理列为可能原因，并反馈关闭 Quantumult X 后恢复；上游酷安分类对 api.coolapk.com 的首页、动态和帖子响应执行脚本修改。该证据说明存在关联风险，不能证明它是唯一原因。

替代：确认酷安恢复后，若要重新启用去广告，先逐条验证规则；本次不恢复 api.coolapk.com 的 MITM。

### L2573 · 酷安

```text
^https?:\/\/api\.coolapk\.com\/v6\/page\/dataList\? url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/coolapk.js
```

原因：按用户要求暂时停用酷安重写，排查网络环境检测；不再对 api.coolapk.com 做 MITM

证据：用户提供的酷安提示将去广告、DNS、Hosts、代理列为可能原因，并反馈关闭 Quantumult X 后恢复；上游酷安分类对 api.coolapk.com 的首页、动态和帖子响应执行脚本修改。该证据说明存在关联风险，不能证明它是唯一原因。

替代：确认酷安恢复后，若要重新启用去广告，先逐条验证规则；本次不恢复 api.coolapk.com 的 MITM。

### L2776 · 来疯

```text
^https?:\/\/api\.jxedt\.com\/ad\/ url reject-200
```

原因：与 L2320 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L2320；本次不改变优先级

### L4548 · 腾讯游戏

```text
^https?:\/\/qt\.qq\.com\/lua\/mengyou\/get_splash_screen_info url reject
```

原因：与 L4469 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L4469；本次不改变优先级

### L5135 · 网易新闻

```text
^https?:\/\/c\.m\.163\.com\/nc\/gl\/ url reject-200
```

原因：与 L5113 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L5113；本次不改变优先级

### L5139 · 网易严选

```text
^https?:\/\/support\.you\.163\.com\/xhr\/boot\/getBootMedia\.json url reject-200
```

原因：与 L2500 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L2500；本次不改变优先级

### L5146 · 网易邮箱

```text
^https?:\/\/appconf\.mail\.163\.com\/mmad\/ url reject-200
```

原因：与 L2499 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L2499；本次不改变优先级

### L5177 · 网易有钱

```text
^https?:\/\/client\.mail\.163\.com\/apptrack\/confinfo\/searchMultiAds url reject-200
```

原因：与 L5112 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L5112；本次不改变优先级

### L5317 · WPS

```text
^https?:\/\/mobile-pic\.cache\.iciba\.com\/feeds_ad\/ url reject-200
```

原因：可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告；与 L2411 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L2411；本次不改变优先级

### L5538 · 小桔科技

```text
^https?:\/\/ct\.xiaojukeji\.com\/agent\/v3\/feeds url reject
```

原因：可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告；与 L1349 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L1349；本次不改变优先级

### L5540 · 小桔科技

```text
^https?:\/\/res\.xiaojukeji\.com\/resapi\/activity\/mget url reject
```

原因：与 L1352 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L1352；本次不改变优先级

### L6070 · 一淘

```text
^https?:\/\/acs\.m\.taobao\.com\/gw\/mtop\.etao\.noah\.query\/.+tao_splash url reject
```

原因：与 L4428 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L4428；本次不改变优先级

### L6071 · 一淘

```text
^https?:\/\/acs\.m\.taobao\.com\/gw\/mtop\.alimama\.etao\.config\.query\/.+?etao_advertise url reject
```

原因：与 L4426 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L4426；本次不改变优先级

### L6498 · 掌上英雄联盟

```text
^https?:\/\/us\.l\.qq\.com\/exapp url reject-200
```

原因：与 L3846 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L3846；本次不改变优先级

### L6544 · 知乎

```text
USER-AGENT,AVOS*, reject
```

原因：不是本交付范围的域名/IP 分流类型：USER-AGENT

证据：固定的 QX 官方示例、源规则及静态编译检查；详见 docs/compatibility.md

替代：USER-AGENT 是 QX 官方支持的分流类型，但本任务要求分流只含域名/IP；可自行将 user-agent, AVOS*, reject 加入现有 [filter_local]，本工具不改主配置

### L6830 · 追书神器

```text
^https?:\/\/adx-cn\.anythinktech\.com\/bid url reject-200
```

原因：与 L1381 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L1381；本次不改变优先级

### L6836 · 字节跳动

```text
host-suffix, -normal-lq.zijieapi.com, reject
```

原因：目标不符合本工具的标准主机名/通配符检查：-normal-lq.zijieapi.com；不据此断言所有 QX 版本都会拒绝

证据：固定的 QX 官方示例、源规则及静态编译检查；详见 docs/compatibility.md

替代：可能意在匹配含 -normal-lq.zijieapi.com 的域名后缀字符串；改成 host-keyword 会改变匹配边界，需上游说明或 QX 实测后决定

### L6859 · 字节跳动

```text
^https?:\/\/dsp\.toutiao\.com\/api\/xunfei\/ads\/ url reject-200
```

原因：与 L4073 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L4073；本次不改变优先级

## 全部去重与合并

同一规则即使跨 App 重复，也通过这里和规则清单保留两个 App 的原始归属。

| 原行 | App / 分类 | 去向 | 代表原行 | 原文 |
|---:|---|---|---|---|
| 437 | 爱奇艺 | duplicate | [425] | `host-suffix, cupid.iqiyi.com, reject` |
| 786 | 百度 | duplicate | [780] | `host-suffix, mobads.baidu.com, reject` |
| 795 | 百度 | duplicate | [775] | `host-suffix, baidustatic.com, reject` |
| 796 | 百度 | duplicate | [637] | `host-suffix, duapps.com, reject` |
| 819 | 百度地图 | duplicate | [640] | `host, afd.baidu.com, reject` |
| 881 | 百度网盘 | duplicate | [812] | `^https?:\/\/update\.pan\.baidu\.com\/statistics url reject` |
| 1371 | 滴滴青桔 | duplicate | [386] | `ip-cidr, 203.107.1.1/24, reject` |
| 1614 | 番茄小说 | duplicate | [422] | `host, dig.bdurl.net, reject` |
| 1958 | Google | duplicate | [617] | `host, safebrowsing.googleapis.com, reject` |
| 2583 | 酷狗音乐 | duplicate | [2578] | `host, adsfile.bssdlbig.kugou.com, reject` |
| 2700 | 快手 | merged | [2698] | `^https:\/\/(apissl\|az2-api(-js\|-idc)?)\.(gifshow\|ksapisrv)\.com\/rest\/system\/startup\? url jsonjq-response-body '.sidebarExSquareStyle.commonlyUsedList \|= map(select(.title == "设置" or .title == "历史记录" or .title == "草稿箱" or .title == "我的钱包" or .title == "小程序" or .title == "未成年人模式" or .title == "官方客服" or .title == "内容偏好" or .title == "离线模式" or .title == "稍后再看" or .title == "举报中心" or .title == "挂件"))'` |
| 3029 | 买单吧 | duplicate | [3028] | `host-suffix, c-hzgt2.getui.com, reject` |
| 3629 | 七猫小说 | duplicate | [643] | `host, mobads.baidu.com, reject` |
| 3831 | QQ音乐 | duplicate | [3813] | `host, ad.tencentmusic.com, reject` |
| 3832 | QQ音乐 | duplicate | [3812] | `host, adstats.tencentmusic.com, reject` |
| 3833 | QQ音乐 | duplicate | [3821] | `host, tmead.y.qq.com, reject` |
| 3836 | QQ音乐 | duplicate | [3630] | `host-suffix, gdt.qq.com, reject` |
| 3986 | 什么值得买 | duplicate | [3199] | `host, aaid.uyunad.com, reject` |
| 4031 | 盛趣游戏 | duplicate | [1520] | `^https?:\/\/daoyu\.sdo\.com\/api\/userCommon\/getAppStartAd url reject` |
| 4105 | 顺丰快递小程序 | duplicate | [4096] | `^https?:\/\/ucmp\.sf-express\.com\/proxy\/esgcempcore\/memberGoods\/pointMallService\/goodsList url reject-dict` |
| 4148 | 搜狗 | duplicate | [1813] | `host-suffix, shouji.sougou.com, reject` |
| 4464 | 腾讯广告 | duplicate | [1835] | `^https?:\/\/mi\.gdt\.qq\.com\/gdt_mview\.fcg url reject` |
| 4523 | 腾讯系 | duplicate | [1980] | `host-suffix, cmshow.gtimg.cn, reject` |
| 4524 | 腾讯系 | duplicate | [1981] | `host-suffix, discuz.gtimg.cn, reject` |
| 4525 | 腾讯系 | duplicate | [1982] | `host-suffix, gu.qlogo.cn, reject` |
| 4526 | 腾讯系 | duplicate | [1983] | `host-suffix, py.qlogo.cn, reject` |
| 4527 | 腾讯系 | duplicate | [1984] | `host-suffix, py2.qlogo.cn, reject` |
| 4528 | 腾讯系 | duplicate | [1990] | `host-suffix, beacon.gtimg.com, reject` |
| 4529 | 腾讯系 | duplicate | [1991] | `host-suffix, bla.gtimg.com, reject` |
| 4530 | 腾讯系 | duplicate | [1992] | `host-suffix, lb.gtimg.com, reject` |
| 4531 | 腾讯系 | duplicate | [1993] | `host-suffix, pgdt.gtimg.com, reject` |
| 4532 | 腾讯系 | duplicate | [1994] | `host-suffix, ra.gtimg.com, reject` |
| 4533 | 腾讯系 | duplicate | [1995] | `host-suffix, splashqqlive.gtimg.com, reject` |
| 4534 | 腾讯系 | duplicate | [1996] | `host-suffix, swa.gtimg.com, reject` |
| 4535 | 腾讯系 | duplicate | [1997] | `host-suffix, tui.gtimg.com, reject` |
| 4536 | 腾讯系 | duplicate | [1998] | `host-suffix, wa.gtimg.com, reject` |
| 4537 | 腾讯系 | duplicate | [1999] | `host-suffix, wb.gtimg.com, reject` |
| 4736 | Talkatone | duplicate | [573] | `host-suffix, amazon-adsystem.com, reject` |
| 4744 | Talkatone | duplicate | [4741] | `host-suffix, spadsync.com, reject` |
| 4745 | Talkatone | duplicate | [1966] | `host-suffix, tpc.googlesyndication.com, reject` |
| 4746 | Talkatone | duplicate | [1961] | `host-suffix, googleadsserving.cn, reject` |
| 4748 | Talkatone | duplicate | [4734] | `host-suffix, inner-active.mobi, reject` |
| 4790 | TubeMax | duplicate | [1985] | `host-suffix, app-measurement.com, reject` |
| 4886 | UC浏览器 | duplicate | [4860] | `host-suffix, applog.uc.cn, reject` |
| 4898 | UC浏览器 | duplicate | [4863] | `host-suffix, track.uc.cn, reject` |
| 4905 | UC浏览器 | duplicate | [1619] | `host, tnc3-aliec2.snssdk.com, reject` |
| 5816 | 新浪 | duplicate | [5776] | `host-suffix, ad.sina.com.cn, reject` |
| 5817 | 新浪 | duplicate | [5777] | `host-suffix, ad4.sina.com.cn, reject` |
| 5818 | 新浪 | duplicate | [5778] | `host-suffix, adbox.sina.com.cn, reject` |
| 5819 | 新浪 | duplicate | [5779] | `host-suffix, counter.sina.com.cn, reject` |
| 5820 | 新浪 | duplicate | [5780] | `host-suffix, current.sina.com.cn, reject` |
| 5821 | 新浪 | duplicate | [5781] | `host-suffix, d0.sina.com.cn, reject` |
| 5822 | 新浪 | duplicate | [5782] | `host-suffix, d00.sina.com.cn, reject` |
| 5823 | 新浪 | duplicate | [5783] | `host-suffix, d1.sina.com.cn, reject` |
| 5824 | 新浪 | duplicate | [5784] | `host-suffix, d2.sina.com.cn, reject` |
| 5825 | 新浪 | duplicate | [5785] | `host-suffix, d3.sina.com.cn, reject` |
| 5826 | 新浪 | duplicate | [5786] | `host-suffix, d4.sina.com.cn, reject` |
| 5827 | 新浪 | duplicate | [5787] | `host-suffix, d5.sina.com.cn, reject` |
| 5828 | 新浪 | duplicate | [5788] | `host-suffix, d6.sina.com.cn, reject` |
| 5829 | 新浪 | duplicate | [5789] | `host-suffix, d7.sina.com.cn, reject` |
| 5830 | 新浪 | duplicate | [5790] | `host-suffix, d8.sina.com.cn, reject` |
| 5831 | 新浪 | duplicate | [5791] | `host-suffix, d9.sina.com.cn, reject` |
| 5832 | 新浪 | duplicate | [5792] | `host-suffix, dcads.sina.com.cn, reject` |
| 5833 | 新浪 | duplicate | [5793] | `host-suffix, p4p.sina.com.cn, reject` |
| 5834 | 新浪 | duplicate | [5794] | `host-suffix, pfp.sina.com.cn, reject` |
| 5835 | 新浪 | duplicate | [5795] | `host-suffix, rm.sina.com.cn, reject` |
| 5836 | 新浪 | duplicate | [5796] | `host-suffix, sax.sina.com.cn, reject` |
| 5837 | 新浪 | duplicate | [5797] | `host-suffix, saxn.sina.com.cn, reject` |
| 5838 | 新浪 | duplicate | [5798] | `host-suffix, saxs.sina.com.cn, reject` |
| 5839 | 新浪 | duplicate | [5799] | `host-suffix, sbeacon.sina.com.cn, reject` |
| 5840 | 新浪 | duplicate | [5800] | `host-suffix, slog.sina.com.cn, reject` |
| 5841 | 新浪 | duplicate | [5801] | `host-suffix, woocall.sina.com.cn, reject` |
| 5842 | 新浪 | duplicate | [5802] | `host-suffix, img.amp.ad.sina.com.cn, reject` |
| 5843 | 新浪 | duplicate | [5803] | `host-suffix, img.adbox.sina.com.cn, reject` |
| 5844 | 新浪 | duplicate | [5804] | `host-suffix, m.beacon.sina.com.cn, reject` |
| 5845 | 新浪 | duplicate | [5805] | `host-suffix, r.dmp.sina.com.cn, reject` |
| 5846 | 新浪 | duplicate | [5806] | `host-suffix, int.dpool.sina.com.cn, reject` |
| 5847 | 新浪 | duplicate | [5807] | `host-suffix, mg.games.sina.com.cn, reject` |
| 5848 | 新浪 | duplicate | [5808] | `host-suffix, adm.leju.sina.com.cn, reject` |
| 5849 | 新浪 | duplicate | [5809] | `host-suffix, staticadm.leju.sina.com.cn, reject` |
| 5850 | 新浪 | duplicate | [5810] | `host-suffix, cre.mix.sina.com.cn, reject` |
| 5851 | 新浪 | duplicate | [5811] | `host-suffix, interest.mix.sina.com.cn, reject` |
| 5852 | 新浪 | duplicate | [5812] | `host-suffix, s.img.mix.sina.com.cn, reject` |
| 5853 | 新浪 | duplicate | [5813] | `host-suffix, motu.p4p.sina.com.cn, reject` |
| 5854 | 新浪 | duplicate | [5814] | `host-suffix, count.video.sina.com.cn, reject` |
| 6845 | 字节跳动 | duplicate | [2373] | `host-suffix, ad.toutiao.com, reject` |
| 6846 | 字节跳动 | duplicate | [2374] | `host-suffix, dm.toutiao.com, reject` |
| 6847 | 字节跳动 | duplicate | [2375] | `host-suffix, dsp.toutiao.com, reject` |
| 6848 | 字节跳动 | duplicate | [2376] | `host-suffix, nativeapp.toutiao.com, reject` |
| 6849 | 字节跳动 | duplicate | [2377] | `host-suffix, partner.toutiao.com, reject` |
| 6850 | 字节跳动 | duplicate | [2378] | `host-suffix, track.toutiao.com, reject` |
| 6851 | 字节跳动 | duplicate | [2379] | `host-suffix, dm.pstatp.com, reject` |
| 6852 | 字节跳动 | duplicate | [2380] | `host-suffix, pb3.pstatp.com, reject` |
| 6853 | 字节跳动 | duplicate | [2381] | `host-suffix, s3a.pstatp.com, reject` |
| 6906 | 广告联盟 | duplicate | [4973] | `host-suffix, zlsdk.1rtb.net, reject` |
| 6989 | 广告联盟 | duplicate | [4739] | `host-suffix, gum.criteo.com, reject` |
| 7298 | 广告联盟 | duplicate | [4740] | `host-suffix, smaato.net, reject` |

## MITM hostname 核对

完整主机名清单及每项关联规则见 [hostname-audit.json](hostname-audit.json)。保留能关联 HTTPS 重写的原声明；补充有限可枚举的精确主机名，不自动生成全局 `*`。HTTP-only 规则不额外启用解密；可选/无法 MITM 的提示遵循原作者意图，不自动扩大范围。
上游 `-i.vip.iqiyi.com` 的减号排除语法在固定官方示例中未得到确认；因此保留排除含义，将覆盖它的宽泛 IQIYI 通配符替换成实际规则可枚举的正向主机名。未自动解密排除主机。

### 补充的 hostname（完整）

上游全局声明缺失或范围不符时，优先沿用 App 注释，再从规则展开有限主机；动态匹配仅投影为带固定域名尾部的窄通配符。这些是静态关联推断，仍需核对 QX 实际 SNI，不代表新增主机已经实机证实可 MITM。

| 补充主机名 | 对应原行 | 提取依据 |
|---|---|---|
| `*.amemv.com` | [6860] | projected-wildcard |
| `114.115.217.129` | [2062] | finite-url-host |
| `47.100.65.202` | [1682, 1683, 1684] | finite-url-host |
| `789.kakamobi.cn` | [2307] | finite-url-host |
| `access.if.iqiyi.com` | [468] | finite-url-host |
| `act.vip.iqiyi.com` | [463] | finite-url-host |
| `agn.aty.sohu.com` | [4250] | finite-url-host |
| `als.baidu.com` | [807] | finite-url-host |
| `api-bk*.tv.sohu.com` | [4249] | projected-wildcard |
| `api.k.sohu.com` | [4245, 4251] | finite-url-host |
| `api.tv.sohu.com` | [4249] | finite-url-host |
| `az2-api-idc.gifshow.com` | [2698] | finite-url-host |
| `az2-api-js.ksapisrv.com` | [2698] | finite-url-host |
| `az2-api.gifshow.com` | [2698] | finite-url-host |
| `c.tieba.baidu.com` | [861, 863] | finite-url-host |
| `cards.iqiyi.com` | [469, 470, 472, 474] | finite-url-host |
| `catdot.dianping.com` | [1295] | finite-url-host |
| `catfront.dianping.com` | [1306] | finite-url-host |
| `comment-card.iqiyi.com` | [476] | finite-url-host |
| `config-service.seeyouyima.com` | [3211, 3212] | finite-url-host |
| `csc-service.sgcc.com.cn` | [5000, 5001, 5002, 5003, 5004] | finite-url-host |
| `damang.api.mgtv.com` | [3098] | finite-url-host |
| `data-collector.soulapp.cn` | [4319] | finite-url-host |
| `dc.bz.mgtv.com` | [3105] | finite-url-host |
| `dc2.bz.mgtv.com` | [3105] | finite-url-host |
| `firefly.abchina.com.cn` | [3396] | finite-url-host |
| `gae2-spclient.spotify.com` | [4350] | finite-url-host |
| `hb-boom.api.mgtv.com` | [3100] | finite-url-host |
| `hui.sohu.com` | [4252] | finite-url-host |
| `iadmusicmat.music.126.net` | [5107] | finite-url-host |
| `iface2.iqiyi.com` | [478, 480, 482, 484, 486, 488, 490] | finite-url-host |
| `image.suning.cn` | [4279] | finite-url-host |
| `img.yun.01zhuanche.com` | [4065] | finite-url-host |
| `js-ad.ayximgs.com.ad-universe-cdn.hzhcbkj.cn` | [1231] | finite-url-host |
| `kjp.cupid.iqiyi.com` | [494] | finite-url-host |
| `live.ximalaya.com` | [5388] | finite-url-host |
| `livewsa.ximalaya.com` | [5388] | finite-url-host |
| `m.aty.sohu.com` | [4253] | finite-url-host |
| `m5.amap.com` | [1817, 1819] | finite-url-host |
| `mapi.dianping.com` | [1296, 1297, 1298, 1299] | finite-url-host |
| `me.bz.mgtv.com` | [3102] | finite-url-host |
| `mlife.jf365.boc.cn` | [6733] | finite-url-host |
| `mmg.aty.sohu.com` | [4254, 4255] | finite-url-host |
| `mob-st.bz.mgtv.com` | [3104] | finite-url-host |
| `mobile-consumer-sapp.chery.cn` | [3650] | finite-url-host |
| `mobile-thor.api.mgtv.com` | [3112] | finite-url-host |
| `mobile.api.mgtv.com` | [3107, 3109, 3111] | finite-url-host |
| `mobileapi.ly.com` | [4632] | finite-url-host |
| `mobileso.bz.mgtv.com` | [3114, 3115] | finite-url-host |
| `p.c.music.126.net` | [5104] | finite-url-host |
| `p?.music.126.net` | [5102, 5108] | projected-wildcard |
| `p?c.music.126.net` | [5102] | projected-wildcard |
| `photocdn.sohu.com` | [4256] | finite-url-host |
| `pic.k.sohu.com` | [4247, 4257] | finite-url-host |
| `ptf.flyertrip.com` | [1681] | finite-url-host |
| `richmanmain.jxedt.com` | [2322] | finite-url-host |
| `s.go.sohu.com` | [4258] | finite-url-host |
| `s1.api.tv.itc.cn` | [4248] | finite-url-host |
| `search.video.iqiyi.com` | [492] | finite-url-host |
| `so.xiaohongshu.com` | [5518] | finite-url-host |
| `t7z.cupid.iqiyi.com` | [494] | finite-url-host |
| `t??.baidu.com` | [811] | projected-wildcard |
| `tcmobileapi.17usoft.com` | [4628, 4629, 4630] | finite-url-host |
| `tower.ubixioe.com` | [3021] | finite-url-host |
| `ucmp-static.sf-express.com` | [4104] | finite-url-host |
| `web-mmap-pay.line-apps.com` | [2929] | finite-url-host |
| `wmapi.meituan.com` | [3176] | finite-url-host |
| `www.binance.net` | [1033] | finite-url-host |
| `www.flyert.com` | [1685, 1686, 1687] | finite-url-host |
| `www.flyert.com.cn` | [1686, 1687] | finite-url-host |
| `www.yingwangtech.com` | [1033] | finite-url-host |
| `www.yingwangtech.info` | [1033] | finite-url-host |
| `wx.17u.cn` | [4626, 4627, 4634] | finite-url-host |
| `zhstatic.zhihu.com` | [6596] | finite-url-host |

### 未自动解决 / 可选的重写

| 原行 | App | 状态 | 说明 |
|---:|---|---|---|
| 467 | 爱奇艺 | unresolved | 动态主机名未找到可证实范围；需实机核对 |
| 813 | 百度 | unresolved | 动态主机名未找到可证实范围；需实机核对 |
| 1540 | 豆瓣 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 1541 | 豆瓣 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 1542 | 豆瓣 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 1543 | 豆瓣 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 1718 | 丰巢 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 2012 | Google | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 2013 | Google | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 2014 | Google | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 3092 | 芒果TV | unresolved | 动态主机名未找到可证实范围；需实机核对 |
| 3096 | 芒果TV | unresolved | 动态主机名未找到可证实范围；需实机核对 |
| 3852 | QQ音乐 | unresolved | 动态主机名未找到可证实范围；需实机核对 |
| 6298 | 邮储银行 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |

### 未激活的上游 hostname（没有丢弃出处）

| 原主机名 | 状态 | 原因 |
|---|---|---|
| `gateway.36kr.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `-i.vip.iqiyi.com` | exclusion | 保留排除含义：未输出相应宽泛通配符；仅输出有限正向主机 |
| `*.iqiyi.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `lego.boohee.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `ad.myfriday.cn` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `js-ad.ayximgs.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `*.dianping.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `consumer.fcbox.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `mobile.flightradar24.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `m*.amap.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `gha.ghac.cn` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `jiucaigongshe.oss-cn-beijing.aliyuncs.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `api.coolapk.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `ebk.17u.cn` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `*.ubixioe.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `x.seeyouyima.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `*.pipix.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `image.pushplus.plus` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `api.mos.csvw.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `img.yun.01zhuanche` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `mapi.sichuanair.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `business-cdn.shouji.sogou.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `api-pay.soulapp.cn` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `api.shenyin.name` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `image.suning.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `*.ly.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `*.17usoft.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `*.17u.cn` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `quic-tcmapi.elong.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `*.music.126.net` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `analytics.163.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `osg-static.sgcc.com.cn` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `gslbali.ximalaya.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `39.103.79.14` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `39.106.97.84` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `47.95.49.75` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `101.201.62.20` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `101.201.62.26` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `101.201.175.228` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `124.250.48.3` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `182.92.145.50` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `182.92.251.113` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `www.vgtime.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `static.mobile-bank.psbc.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `wallet.95516.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `tysdk.95516.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `ads.95516.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |

## 远程脚本及数据依赖

每行是一次完整 GET 与语法/JSON 检查的证据。检测时间保存在 JSON 清单；相同内容的再次检测记录到 logs，不为制造差异刷新产物时间。脚本内部 eval、网络加载或按环境分支的逻辑，只标记待实测，未执行或声称已经验证其二次依赖。

| 源行 | 原始 URL | 检查 | 字节数 | 动态代码 / 内部网络 |
|---|---|---|---:|---|
| [3141] | [https://github.com/fmz200/wool_scripts/raw/main/Scripts/mlxx/mlxx.js](https://github.com/fmz200/wool_scripts/raw/main/Scripts/mlxx/mlxx.js) | 通过 | 2295 |  |
| [5516, 5517, 5518, 5520, 5521, 5523, 5527, 5528, 5529, 5530] | [https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js](https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js) | 通过 | 28643 | 内部网络 |
| [1134] | [https://raw.githubusercontent.com/Keywos/rule/main/mocks/caiyun.json](https://raw.githubusercontent.com/Keywos/rule/main/mocks/caiyun.json) | 通过 | 314 |  |
| [5186, 5187, 5188, 5189, 5190, 5191, 5192] | [https://raw.githubusercontent.com/Keywos/rule/main/script/wy/js/wyres.js](https://raw.githubusercontent.com/Keywos/rule/main/script/wy/js/wyres.js) | 通过 | 17300 |  |
| [6457] | [https://raw.githubusercontent.com/Maasea/sgmodule/refs/heads/master/Script/Youtube/youtube.response.js](https://raw.githubusercontent.com/Maasea/sgmodule/refs/heads/master/Script/Youtube/youtube.response.js) | 通过 | 132973 | 内部网络 |
| [1503] | [https://raw.githubusercontent.com/NobyDa/Script/master/Bahamut/BahamutAnimeAds.js](https://raw.githubusercontent.com/NobyDa/Script/master/Bahamut/BahamutAnimeAds.js) | 通过 | 1860 | 内部网络 |
| [5452] | [https://raw.githubusercontent.com/NobyDa/Script/master/QuantumultX/File/xjsp.js](https://raw.githubusercontent.com/NobyDa/Script/master/QuantumultX/File/xjsp.js) | 通过 | 1889 |  |
| [5236] | [https://raw.githubusercontent.com/Sliverkiss/QuantumultX/main/AdBlock/xmApp/wnbz.js](https://raw.githubusercontent.com/Sliverkiss/QuantumultX/main/AdBlock/xmApp/wnbz.js) | 通过 | 604 |  |
| [5554] | [https://raw.githubusercontent.com/Sliverkiss/QuantumultX/main/AdBlock/xmApp/xmApp.js](https://raw.githubusercontent.com/Sliverkiss/QuantumultX/main/AdBlock/xmApp/xmApp.js) | 通过 | 340 |  |
| [2709] | [https://raw.githubusercontent.com/app2smile/rules/master/js/adsense.js](https://raw.githubusercontent.com/app2smile/rules/master/js/adsense.js) | 通过 | 2354 |  |
| [3666] | [https://raw.githubusercontent.com/app2smile/rules/master/js/qidian.js](https://raw.githubusercontent.com/app2smile/rules/master/js/qidian.js) | 通过 | 5761 |  |
| [4544] | [https://raw.githubusercontent.com/app2smile/rules/master/js/qq-news.js](https://raw.githubusercontent.com/app2smile/rules/master/js/qq-news.js) | 通过 | 2283 |  |
| [4349] | [https://raw.githubusercontent.com/app2smile/rules/master/js/spotify-json.js](https://raw.githubusercontent.com/app2smile/rules/master/js/spotify-json.js) | 通过 | 381 |  |
| [4348] | [https://raw.githubusercontent.com/app2smile/rules/master/js/spotify-proto.js](https://raw.githubusercontent.com/app2smile/rules/master/js/spotify-proto.js) | 通过 | 71920 | 动态代码、内部网络 |
| [4347] | [https://raw.githubusercontent.com/app2smile/rules/master/js/spotify-qx-header.js](https://raw.githubusercontent.com/app2smile/rules/master/js/spotify-qx-header.js) | 通过 | 135 |  |
| [861] | [https://raw.githubusercontent.com/app2smile/rules/master/js/tieba-json.js](https://raw.githubusercontent.com/app2smile/rules/master/js/tieba-json.js) | 通过 | 9971 |  |
| [863] | [https://raw.githubusercontent.com/app2smile/rules/master/js/tieba-proto.js](https://raw.githubusercontent.com/app2smile/rules/master/js/tieba-proto.js) | 通过 | 97069 |  |
| [4939] | [https://raw.githubusercontent.com/app2smile/rules/master/js/vgtime.js](https://raw.githubusercontent.com/app2smile/rules/master/js/vgtime.js) | 通过 | 292 |  |
| [160, 161] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/51card.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/51card.js) | 通过 | 536 |  |
| [172] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/555Ad.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/555Ad.js) | 通过 | 360 |  |
| [3567, 3568, 3569, 3571, 3573, 3575] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/PupuSplashAds.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/PupuSplashAds.js) | 通过 | 1799 |  |
| [3774] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/QuDa.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/QuDa.js) | 通过 | 267 |  |
| [391, 392] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/adrive/adrive.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/adrive/adrive.js) | 通过 | 1105 |  |
| [831] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/baidumap.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/baidumap.js) | 通过 | 80326 | 动态代码、内部网络 |
| [1096] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/blued.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/blued.js) | 通过 | 246 |  |
| [912, 924, 926] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/bohe/bohe_ads.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/bohe/bohe_ads.js) | 通过 | 956 |  |
| [264, 1144, 1148, 1150] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/cainiao/cainiao.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/cainiao/cainiao.js) | 通过 | 4973 |  |
| [1130] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/caixin/caixinAd.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/caixin/caixinAd.js) | 通过 | 1710 |  |
| [6524] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/cmschina/cmschina.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/cmschina/cmschina.js) | 通过 | 408 |  |
| [467, 468, 469, 470, 472, 474, 476, 478, 480, 482, 488, 492, 494, 3102, 3104, 3105, 3107, 3111, 3112, 3115, 6236, 6240, 6242, 6246, 6248, 6250] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/cnftp.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/cnftp.js) | 通过 | 31606 |  |
| [1400] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/dianyinglieshou.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/dianyinglieshou.js) | 通过 | 1137 |  |
| [1349, 1350, 1351, 1352, 1353, 1355, 1356, 1357, 1358, 1360] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/didi/didiAds.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/didi/didiAds.js) | 通过 | 2745 |  |
| [1710] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/fenbi.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/fenbi.js) | 通过 | 826 |  |
| [1684] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/fly.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/fly.js) | 通过 | 488 |  |
| [2106] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/hengdian.json](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/hengdian.json) | 通过 | 711 |  |
| [2249, 2250] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/huifutianxia_ads.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/huifutianxia_ads.js) | 通过 | 322 |  |
| [2283] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/ithome/ithome.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/ithome/ithome.js) | 通过 | 1311 |  |
| [2479] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/jingdong/jingdong.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/jingdong/jingdong.js) | 通过 | 10303 |  |
| [2510] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/jingxiAd.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/jingxiAd.js) | 通过 | 285 |  |
| [2752, 2756, 2758, 2760] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/keep.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/keep.js) | 通过 | 12394 |  |
| [2656, 2658, 2659, 2660, 2661] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/kuwo/kuwo.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/kuwo/kuwo.js) | 通过 | 4640 |  |
| [2899, 2900] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/lawson.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/lawson.js) | 通过 | 1847 |  |
| [2894] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/lvtusuishenting/ltsst-ad.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/lvtusuishenting/ltsst-ad.js) | 通过 | 869 |  |
| [3050, 3052] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/maimai/maimai_ads.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/maimai/maimai_ads.js) | 通过 | 861 |  |
| [3211, 3212] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/meiyou/meiyou_ads.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/meiyou/meiyou_ads.js) | 通过 | 13949 | 内部网络 |
| [265, 266, 4434, 4435, 5632] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/myBlockAds.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/myBlockAds.js) | 通过 | 7652 |  |
| [6698, 6700] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/picc/picc_ads.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/picc/picc_ads.js) | 通过 | 609 |  |
| [2665] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/quark.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/quark.js) | 通过 | 14279 |  |
| [3929] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/reddit.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/reddit.js) | 通过 | 742 |  |
| [3877, 3883, 3885, 3887, 3889, 3891, 3893, 3895, 3897] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/rrtv_json.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/rrtv_json.js) | 通过 | 25962 | 内部网络 |
| [4005, 4007, 4008, 4009, 4010, 4011, 4012, 4013] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/smzdm/Smzdm.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/smzdm/Smzdm.js) | 通过 | 3220 |  |
| [4000, 4001, 4002, 4003, 4004] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/smzdm/smzdm_ads.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/smzdm/smzdm_ads.js) | 通过 | 1210 |  |
| [4262] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/soda.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/soda.js) | 通过 | 220 |  |
| [4328, 4329, 4330, 4331, 4332, 4333, 4334, 4335, 4336, 4337, 4338, 4339] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/soul/soul_ads.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/soul/soul_ads.js) | 通过 | 15235 | 内部网络 |
| [4319] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/template/req_replace_body.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/template/req_replace_body.js) | 通过 | 353 |  |
| [2062] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/umetrip/umetrip_ads.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/umetrip/umetrip_ads.js) | 通过 | 215 |  |
| [5661] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaotucc.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaotucc.js) | 通过 | 340 |  |
| [5151] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/youdao/dict-youdao-ad.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/youdao/dict-youdao-ad.js) | 通过 | 1202 |  |
| [6268] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/yx.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/yx.js) | 通过 | 134 |  |
| [6482] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/zhangshanggongjiao.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/zhangshanggongjiao.js) | 通过 | 688 |  |
| [6554, 6557, 6560, 6562, 6564, 6567, 6577, 6579, 6581, 6585, 6588] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/zhihu/zhihu.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/zhihu/zhihu.js) | 通过 | 7358 |  |
| [6821] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/zhuanzhuan/zhuanzhuan.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/zhuanzhuan/zhuanzhuan.js) | 通过 | 1020 |  |
| [3256] | [https://raw.githubusercontent.com/fmz200/wool_scripts/refs/heads/main/Scripts/miguvideo/miguvideo_ads.js](https://raw.githubusercontent.com/fmz200/wool_scripts/refs/heads/main/Scripts/miguvideo/miguvideo_ads.js) | 通过 | 13377 | 内部网络 |
| [5436, 5438, 5440, 5442, 5444, 5446, 5448] | [https://raw.githubusercontent.com/ishowshu/qx/refs/heads/main/script/goofish.js](https://raw.githubusercontent.com/ishowshu/qx/refs/heads/main/script/goofish.js) | 通过 | 7810 |  |
| [52] | [https://raw.githubusercontent.com/kokoryh/Script/master/js/12306.js](https://raw.githubusercontent.com/kokoryh/Script/master/js/12306.js) | 通过 | 357 |  |
| [5217] | [https://raw.githubusercontent.com/zZPiglet/Task/master/asset/UnblockURLinWeChat.js](https://raw.githubusercontent.com/zZPiglet/Task/master/asset/UnblockURLinWeChat.js) | 通过 | 86443 | 内部网络 |
| [3748, 3750] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/51job.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/51job.js) | 通过 | 1169 |  |
| [6673] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/airchina.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/airchina.js) | 通过 | 808 |  |
| [2337] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/alicdn.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/alicdn.js) | 通过 | 604 |  |
| [1054, 1055, 1056, 1057] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/bilibiliManga.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/bilibiliManga.js) | 通过 | 2295 |  |
| [2333] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/ccblife.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/ccblife.js) | 通过 | 3262 |  |
| [1438, 1440, 1448] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/ddxq.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/ddxq.js) | 通过 | 1836 |  |
| [1300, 1312] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/dianping.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/dianping.js) | 通过 | 2257 |  |
| [1687] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/flyert.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/flyert.js) | 通过 | 842 |  |
| [1763] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/foliday.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/foliday.js) | 通过 | 972 |  |
| [2102] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/freshippo.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/freshippo.js) | 通过 | 2094 |  |
| [3008] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/mafengwo.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/mafengwo.js) | 通过 | 1044 |  |
| [3035] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/mdb.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/mdb.js) | 通过 | 738 |  |
| [3655] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/qmai.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/qmai.js) | 通过 | 2092 |  |
| [4671, 4672, 4673] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/tuhu.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/tuhu.js) | 通过 | 2610 |  |
| [5756] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/usmile.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/usmile.js) | 通过 | 739 |  |
| [1597, 1599] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/wechatApplet.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/wechatApplet.js) | 通过 | 5966 |  |

完整 HTTP 状态、最终 URL、内容摘要、脚本 API 线索及时间见 [dependency-audit.json](dependency-audit.json)。
保留原作者的 main/master 等可变脚本 URL，以延续其更新能力；本报告只证明采集时的内容。失败时保留的是本项目上一版文件，无法回滚别人仓库的脚本，也无法保证 QX 后来重新下载的脚本仍与本次摘要相同。
`echo-response` 官方示例要求本地 Data 文件。本次保持原 JSON 内容，只把引用改为配套 Data 文件名；该文件的后续更新需在手机同步，不能假称订阅会自动更新手机本地数据。

## 潜在误拦截（完整关键词筛查结果）

以下是静态风险线索，不是确认存在 bug。保留上游正常商品推荐精简行为，特别是闲鱼，不把‘推荐’一概称为广告。是否关闭某条由实机回归决定。

| 原行 | App / 分类 | 状态 | 风险线索 |
|---:|---|---|---|
| 44 | 12123 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 85 | 2345天气王 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 118 | 360 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 159 | 51信用卡管家 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 172 | 555影视 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 222 | 9to5Mac | kept | 整站阻断 temu.com，会影响正常购物访问；保留上游规则，建议已有 Cats 时先不开奶思分流 |
| 386 | 阿里云 | kept | 阻断整个 IP 子网，可能包含非广告/共享服务；CIDR 标准化未扩大原子网 |
| 407 | 爱美剧 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 435 | 爱奇艺 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 467 | 爱奇艺 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 468 | 爱奇艺 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 470 | 爱奇艺 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 586 | Amazon | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 710 | 百度 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 815 | 百度 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 863 | 百度贴吧 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 871 | 百度网盘 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 942 | 宝宝树孕育 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 1049 | 哔哩哔哩漫画 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 1053 | 哔哩哔哩漫画 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 1056 | 哔哩哔哩漫画 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 1092 | Blued | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 1094 | Blued | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 1134 | 彩云天气 | kept | 此条需要将配套 JSON 复制到 QX 的 Data 目录；更新后也需同步该文件 |
| 1145 | 菜鸟裹裹 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 1235 | Clubmed | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 1330 | 到梦空间 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 1349 | 滴滴出行 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 1371 | 滴滴青桔 | duplicate | 阻断整个 IP 子网，可能包含非广告/共享服务；CIDR 标准化未扩大原子网；上游注释已提示误杀/影响运行，保留原文供核对 |
| 1400 | 电影猎手 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 1404 | 电E宝 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 1408 | 丁香医生 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 1416 | 叮嗒出行 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 1450 | 叮咚买菜 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 1452 | 叮咚买菜 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段；可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 1490 | 懂车帝 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 1491 | 懂车帝 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 1495 | 懂球帝 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 1511 | 抖音 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 1512 | 抖音 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 1540 | 豆瓣 | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 1541 | 豆瓣 | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 1542 | 豆瓣 | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 1543 | 豆瓣 | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 1626 | 番茄小说 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 1632 | 番茄小说 | kept | 上游注释已提示误杀/影响运行，保留原文供核对 |
| 1647 | 番茄小说 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 1651 | 番茄小说 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 1718 | 丰巢 | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 1885 | 光大银行 阳光惠生活 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2009 | Google | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 2012 | Google | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对；上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 2013 | Google | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对；上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 2014 | Google | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 2082 | 合利宝展业通 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 2099 | 盒马 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 2100 | 盒马 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 2101 | 盒马 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 2102 | 盒马 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 2259 | 火猫 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 2272 | Huawei AspiegelBot | kept | 阻断整个 IP 子网，可能包含非广告/共享服务；CIDR 标准化未扩大原子网 |
| 2283 | IT之家 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 2361 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2362 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2363 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2364 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2365 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2366 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2367 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2368 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2369 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2370 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2371 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2372 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2383 | 今日头条 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 2386 | 今日头条 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 2409 | 金山词霸 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 2411 | 金山词霸 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 2479 | 京东 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 2495 | 京东金融 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 2571 | 酷安 | quarantined | 按用户要求暂时停用酷安重写，排查网络环境检测；不再对 api.coolapk.com 做 MITM |
| 2572 | 酷安 | quarantined | 按用户要求暂时停用酷安重写，排查网络环境检测；不再对 api.coolapk.com 做 MITM |
| 2573 | 酷安 | quarantined | 按用户要求暂时停用酷安重写，排查网络环境检测；不再对 api.coolapk.com 做 MITM |
| 2586 | 酷狗音乐 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告；关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2587 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2588 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2589 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2590 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2591 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2592 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2593 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2594 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2595 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2596 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2597 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2598 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2599 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2600 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2637 | 酷我音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2638 | 酷我音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2653 | 酷我音乐 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 2658 | 酷我音乐 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 2659 | 酷我音乐 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 2701 | 快手 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 2704 | 快手 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 2736 | Keep | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 2789 | 蓝基因 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2884 | 鲁班到家用户版 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 2929 | Line | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 2965 | lofter | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3035 | 买单吧 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 3046 | 脉脉 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 3050 | 脉脉 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3052 | 脉脉 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3115 | 芒果TV | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3131 | 每日精选 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3132 | 每日精选 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3251 | 咪咕视频 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3255 | 咪咕视频 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3262 | 米家 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3272 | 民生银行 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3273 | 民生银行 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3274 | 民生银行 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3275 | 民生银行 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3289 | 墨迹天气 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3290 | 墨迹天气 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3291 | 墨迹天气 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3292 | 墨迹天气 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3305 | 全民生活 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3492 | 皮皮虾 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3493 | 皮皮虾 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3494 | 皮皮虾 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3558 | 朴朴超市 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 3562 | 朴朴超市 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3573 | 朴朴超市 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 3575 | 朴朴超市 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 3598 | pikpak | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3662 | 起点读书 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3663 | 起点读书 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3664 | 起点读书 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3666 | 起点读书 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3682 | 汽车之家 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3684 | 汽车之家 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3685 | 汽车之家 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3686 | 汽车之家 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3723 | 汽水音乐 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3735 | 前程无忧 51Job | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 3745 | 前程无忧 51Job | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 3747 | 前程无忧 51Job | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3748 | 前程无忧 51Job | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段；可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3883 | 人人视频 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3895 | 人人视频 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3897 | 人人视频 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3899 | 人人视频 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3903 | 日产智联 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3917 | 瑞幸咖啡 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 3936 | 三联中读 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3943 | 山姆会员商店 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 3944 | 山姆会员商店 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3975 | 少数派 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对；可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4062 | 首汽约车 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4064 | 首汽约车 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4084 | 书旗小说 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4099 | 顺丰快递 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4107 | 顺丰快递小程序 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4187 | 搜狗 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4295 | 苏e行 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4453 | 腾讯乘车码 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 4491 | 腾讯手机管家 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 4544 | 腾讯新闻 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4573 | 天府银行小程序 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 4580 | 天猫精灵 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 4622 | 天翼云盘 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4630 | 同程旅行 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4650 | 同花顺 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4661 | 途虎养车 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4664 | 途虎养车 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4686 | 团油 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 4835 | UC浏览器 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 4845 | UC浏览器 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 4868 | UC浏览器 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 4875 | UC浏览器 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4924 | udn news | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 4925 | udn news | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 4953 | Vivo | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 4954 | Vivo | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 4957 | VIVO商城 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 4988 | 万词王 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5104 | 网易 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5105 | 网易 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5106 | 网易 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5107 | 网易 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5109 | 网易 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5110 | 网易 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5111 | 网易 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对；可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5114 | 网易 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5124 | 网易考拉 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5140 | 网易严选 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5159 | 网易有道词典 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5181 | 网易云音乐 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5183 | 网易云音乐 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5184 | 网易云音乐 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5185 | 网易云音乐 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5189 | 网易云音乐 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5217 | 微信解除链接限制 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5275 | Whale Cloud (鲸云) | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5279 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5280 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5281 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5282 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5283 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5284 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5285 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5286 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5287 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5288 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5289 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5290 | WiFi万能钥匙 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段；关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5291 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5292 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5293 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5294 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5295 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5296 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5303 | WiFi万能钥匙 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5309 | Wostore (联通沃商店) | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 5311 | Wostore (联通沃商店) | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 5312 | Wostore (联通沃商店) | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 5317 | WPS | quarantined | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5371 | 喜马拉雅 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5372 | 喜马拉雅 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5374 | 喜马拉雅 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5378 | 喜马拉雅 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5382 | 喜马拉雅 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5383 | 喜马拉雅 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5390 | 喜马拉雅 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5391 | 喜马拉雅 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5408 | 闲鱼 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5410 | 闲鱼 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5412 | 闲鱼 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5414 | 闲鱼 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5416 | 闲鱼 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5426 | 闲鱼 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5428 | 闲鱼 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5436 | 闲鱼 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5462 | 向日葵 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 5470 | 小爱音箱 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 5496 | 小合拓展 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5512 | 小红书 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5527 | 小红书 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5528 | 小红书 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5529 | 小红书 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5530 | 小红书 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5538 | 小桔科技 | quarantined | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5544 | 小利生活 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段；关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5546 | 小利生活 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 5552 | 小芒 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5554 | 小芒 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5561 | 小米 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5640 | 小米运动 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5685 | 小艺 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5686 | 小艺 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5690 | 小宇宙 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5865 | 新浪 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5866 | 新浪 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 5930 | 兴业证券 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5942 | 雪球 | kept | 上游注释已提示误杀/影响运行，保留原文供核对 |
| 5951 | 雪球 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 5952 | 雪球 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5953 | 雪球 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5954 | 雪球 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5972 | 讯飞输入法 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5973 | 讯飞输入法 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5974 | 讯飞输入法 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5975 | 讯飞输入法 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 6065 | 一汽大众 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6121 | 翼支付 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 6123 | 翼支付 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 6134 | 银盛通 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 6138 | 银盛小Y管家 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 6236 | 优酷 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6264 | 悠洗APP | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 6267 | 悠洗APP | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 6293 | 邮储银行 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 6294 | 邮储银行 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 6298 | 邮储银行 | kept | 上游注释已提示误杀/影响运行，保留原文供核对；上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 6311 | 游民星空 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 6312 | 游民星空 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 6366 | 元聚网络（漫画岛，追书神器，甜瓜小说） | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 6500 | 掌上英雄联盟 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6544 | 知乎 | quarantined | 不是本交付范围的域名/IP 分流类型：USER-AGENT |
| 6560 | 知乎 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6562 | 知乎 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6573 | 知乎 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6578 | 知乎 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6579 | 知乎 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6581 | 知乎 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6590 | 知乎 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6591 | 知乎 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6595 | 知乎 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6740 | 中华万年历 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 6741 | 中华万年历 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 6742 | 中华万年历 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 6743 | 中华万年历 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 6744 | 中华万年历 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 6745 | 中华万年历 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 6776 | 中信银行 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 6784 | 中银跨境GO | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 6819 | 转转 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6836 | 字节跳动 | quarantined | 目标不符合本工具的标准主机名/通配符检查：-normal-lq.zijieapi.com；不据此断言所有 QX 版本都会拒绝 |
| 6896 | 广告联盟 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 6897 | 广告联盟 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 6898 | 广告联盟 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 6910 | 广告联盟 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 6925 | 广告联盟 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 7007 | 广告联盟 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 7167 | 广告联盟 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |

## 功能对比、Cats 与实机待验

- 全量 App / 功能类型对比：[coverage.md](coverage.md) / [coverage.json](coverage.json)。
- Cats 语义去重与完整差集：[cats-comparison.md](cats-comparison.md)。
- 实机验收步骤：[docs/device-checklist.md](docs/device-checklist.md)。
- 尚未实机验证：QX 导入解析、脚本 API 与内置 jq 版本、MITM 合并和证书锁定、App 启动/登录/支付/订单/购物车/验证码、广告实际命中、缓存、不同 App/iOS/QX 版本、自动刷新是否加载到新脚本。
- 本工具没有读取或改写用户 QX 节点、策略组、DNS、证书、主配置、Cats 订阅或 Google 重定向。
