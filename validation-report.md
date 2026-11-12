# 奶思 Quantumult X 转换验证报告

本报告验证规则拆分、语法、出处、静态覆盖和下载结果，未运行真实 QX / iOS App。静态通过不代表 100% 实机兼容，也不代表所有广告都会消失。

## 来源与复现

- 原版仓库：[fmz200/wool_scripts](https://github.com/fmz200/wool_scripts)。
- 固定输入 commit：`009b501adaebb3428461e91c98a17a556249e076`；日期 `2026-11-11T14:06:32Z`。
- 规则地址：[QuantumultX/rewrite/rewrite.snippet](https://raw.githubusercontent.com/fmz200/wool_scripts/009b501adaebb3428461e91c98a17a556249e076/QuantumultX/rewrite/rewrite.snippet)。
- 输入 SHA-256：`8a8499e50d0311a078e4c4bf0c48097c3840843bd76bffab390c8a259fab0574`。完整原始字节保存在 [upstream/naisi-original.snippet](upstream/naisi-original.snippet)。
- 转换器固定从上述官方路径拉取；不读取 clean、compatible、v2 或其他历史修正版。
- 每个物理行见 [source-ledger.json](source-ledger.json)；每条规则的原文、App、状态、修复、出处见 [rule-inventory.json](rule-inventory.json)。

## 数量与去向

| 项目 | 数量 |
|---|---:|
| 原版物理行 | 7522 |
| 原版有效规则行（不含注释、空行、hostname） | 4384 |
| 原版重写候选 | 1623 |
| 原版分流候选（包括隔离的 User-Agent） | 2761 |
| 输出唯一重写 | 1598 |
| 输出唯一域名/IP分流 | 2667 |
| 标准化后去重来源行 | 96 |
| 合并到其他规则的来源行 | 1 |
| 有修复说明的来源行 | 81 |
| 隔离来源行 | 22 |
| 可追溯保留来源行（输出+去重+合并） | 4362 |
| 上游 hostname 唯一项（含排除项） | 968 |
| 输出有效 hostname 项 | 985 |
| 补充的 hostname 项 | 73 |
| 保留出处但未激活的上游 hostname 项 | 56 |

静态可追溯保留比例：4362/4384（99.50%）。这是源规则的可追溯比例，不是实测功能成功率。隔离的冲突行在原匹配位置仍可能有保留的首条规则。
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
| reject-dict | 455 | 453 | 454 |
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
- ICU 库：`libicui18n.so.74`。逐条编译 URL、头部和替换匹配式；QX 内部引擎与导入器未公开，ICU 不是实机验收。
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
| 858 | 百度贴吧 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 180.76.76.200/32, reject` | `ip-cidr, 180.76.76.200/32, reject` |
| 1140 | 彩云天气 | echo-response 远程 JSON 改为官方明确支持的本地 Data 文件；原 URL 保存在依赖报告 | `^https?:\/\/wrapper\.cyapi\.cn\/v1\/activity\? url echo-response application/json echo-response https://raw.githubusercontent.com/Keywos/rule/main/mocks/caiyun.json` | `^https?:\/\/wrapper\.cyapi\.cn\/v1\/activity\? url echo-response application/json echo-response Naisi-4c4c1af80d75.json` |
| 1390 | 滴滴青桔 | CIDR 网络地址标准化：203.107.1.1/24 → 203.107.1.0/24（同一子网） | `ip-cidr, 203.107.1.1/24, reject` | `ip-cidr, 203.107.1.0/24, reject` |
| 1546 | 斗鱼直播 | 斗鱼 getStartSend 后的查询问号转义为字面字符；原式把前一个字母设为可选 | `^https?:\/\/capi\.douyucdn\.cn\/api\/v1\/getStartSend?client_sys=ios url reject-img` | `^https?:\/\/capi\.douyucdn\.cn\/api\/v1\/getStartSend\?client_sys=ios url reject-img` |
| 1577 | Dr.Peng | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 211.161.101.110/32, reject` | `ip-cidr, 211.161.101.110/32, reject` |
| 1650 | 番茄小说 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 49.71.37.101/32, reject` | `ip-cidr, 49.71.37.101/32, reject` |
| 1651 | 番茄小说 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 117.71.105.23/32, reject` | `ip-cidr, 117.71.105.23/32, reject` |
| 1652 | 番茄小说 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 218.94.207.205/32, reject` | `ip-cidr, 218.94.207.205/32, reject` |
| 1653 | 番茄小说 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 117.92.229.188/32, reject` | `ip-cidr, 117.92.229.188/32, reject` |
| 1654 | 番茄小说 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 101.36.166.16/32, reject` | `ip-cidr, 101.36.166.16/32, reject` |
| 1655 | 番茄小说 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 180.96.2.114/32, reject` | `ip-cidr, 180.96.2.114/32, reject` |
| 2089 | 航旅纵横 | 将 http?: 修成 https?:；原式只匹配 htt/http，遗漏 HTTPS | `^http?:\/\/(discardrp\|startup)\.umetrip\.com\/gateway\/api\/umetrip\/native url reject` | `^https?:\/\/(discardrp\|startup)\.umetrip\.com\/gateway\/api\/umetrip\/native url reject` |
| 2090 | 航旅纵横 | 将 http?: 修成 https?:；原式只匹配 htt/http，遗漏 HTTPS；航旅纵横主机二选一补成同一组，使协议、路径和结尾同时约束两个分支，避免 IP 分支匹配全部路径 | `^http?:\/\/(114\.115\.217\.129)\|(home\.umetrip\.com)\/gateway\/api\/umetrip\/native$ url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/umetrip/umetrip_ads.js` | `^https?:\/\/(114\.115\.217\.129\|home\.umetrip\.com)\/gateway\/api\/umetrip\/native$ url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/umetrip/umetrip_ads.js` |
| 2306 | Huawei AspiegelBot | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 114.119.160.0/21, reject` | `ip-cidr, 114.119.160.0/21, reject` |
| 2398 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,clk.gentags.net, reject` | `host-keyword, clk.gentags.net, reject` |
| 2399 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,dm.pstatp.com, reject` | `host-keyword, dm.pstatp.com, reject` |
| 2400 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,dm.bytedance.com, reject` | `host-keyword, dm.bytedance.com, reject` |
| 2401 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,uop.umeng.com, reject` | `host-keyword, uop.umeng.com, reject` |
| 2402 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,m.suning.com, reject` | `host-keyword, m.suning.com, reject` |
| 2403 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,adshare.toutiao.com, reject` | `host-keyword, adshare.toutiao.com, reject` |
| 2404 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,tunion-api.m.taobao.com, reject` | `host-keyword, tunion-api.m.taobao.com, reject` |
| 2405 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,s1.pstatp.com, reject` | `host-keyword, s1.pstatp.com, reject` |
| 2406 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,s2.pstatp.com, reject` | `host-keyword, s2.pstatp.com, reject` |
| 2407 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,s3.pstatp.com, reject` | `host-keyword, s3.pstatp.com, reject` |
| 2408 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,a3.pstatp.com, reject` | `host-keyword, a3.pstatp.com, reject` |
| 2409 | 今日头条 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,a3.bytecdn.cn, reject` | `host-keyword, a3.bytecdn.cn, reject` |
| 2512 | 京东 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 101.124.19.122/32, reject` | `ip-cidr, 101.124.19.122/32, reject` |
| 2513 | 京东 | 规则类型/动作标准化：IP6-CIDR → ip6-cidr，策略 reject | `IP6-CIDR, 2402:db40:5100:1011::5/128, reject` | `ip6-cidr, 2402:db40:5100:1011::5/128, reject` |
| 2588 | 肯德基 | 肯德基域名误写的 \c 控制字符改为字面域名点，与源注释 res.kfc.com.cn 一致 | `^https?:\/\/res\.kfc\.com.\cn\/advertisement\/ url reject` | `^https?:\/\/res\.kfc\.com\.cn\/advertisement\/ url reject` |
| 2734 | 快手 | 与 L2735 的同条件 JSONJQ 按源顺序合并，避免仅首条生效 | `^https:\/\/(apissl\|az2-api(-js\|-idc)?)\.(gifshow\|ksapisrv)\.com\/rest\/system\/startup\? url jsonjq-response-body 'del(.reskinConfig.sidebarExSquareStyle.moreList, .reskinConfig.sidebarExSquareStyle.topList)'` | `^https:\/\/(apissl\|az2-api(-js\|-idc)?)\.(gifshow\|ksapisrv)\.com\/rest\/system\/startup\? url jsonjq-response-body '(del(.reskinConfig.sidebarExSquareStyle.moreList, .reskinConfig.sidebarExSquareStyle.topList)) \| (.sidebarExSquareStyle.commonlyUsedList \|= map(select(.title == "设置" or .title == "历史记录" or .title == "草稿箱" or .title == "我的钱包" or .title == "小程序" or .title == "未成年人模式" or .title == "官方客服" or .title == "内容偏好" or .title == "离线模式" or .title == "稍后再看" or .title == "举报中心" or .title == "挂件")))'` |
| 3186 | 美丽修行 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https:\/\/api\.bevol\.com\/(?:appmain\/app\/home\/page\|usercenter\/account\/info\|personal\/page\|appmain\/app\/home\/launch\|trialbox\/shop\/app\/homePage)$ url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/mlxx/mlxx.js` | `^https:\/\/api\.bevol\.com\/(?:appmain\/app\/home\/page\|usercenter\/account\/info\|personal\/page\|appmain\/app\/home\/launch\|trialbox\/shop\/app\/homePage)$ url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/mlxx/mlxx.js` |
| 3329 | 墨迹天气 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,me.api.moji.com, reject` | `host-keyword, me.api.moji.com, reject` |
| 3330 | 墨迹天气 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,android.bugly.qq.com, reject` | `host-keyword, android.bugly.qq.com, reject` |
| 3331 | 墨迹天气 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,av1.xdrig.com, reject` | `host-keyword, av1.xdrig.com, reject` |
| 3332 | 墨迹天气 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD,adash.man.aliyuncs.com, reject` | `host-keyword, adash.man.aliyuncs.com, reject` |
| 3597 | 朴朴超市 | 重写操作符/动作改为官方示例的小写 | `^http:\/\/139\.196\.12\.179:8053\/httpdns\/ url REJECT` | `^http:\/\/139\.196\.12\.179:8053\/httpdns\/ url reject` |
| 3598 | 朴朴超市 | 重写操作符/动作改为官方示例的小写 | `^http:\/\/106\.55\.220\.18:8053\/httpdns\/ url REJECT` | `^http:\/\/106\.55\.220\.18:8053\/httpdns\/ url reject` |
| 3599 | 朴朴超市 | 重写操作符/动作改为官方示例的小写 | `^http:\/\/54\.222\.159\.138:8053\/httpdns\/ url REJECT` | `^http:\/\/54\.222\.159\.138:8053\/httpdns\/ url reject` |
| 3600 | 朴朴超市 | 重写操作符/动作改为官方示例的小写 | `^http:\/\/101\.42\.130\.147\/httpdns\/resolve\/ url REJECT` | `^http:\/\/101\.42\.130\.147\/httpdns\/resolve\/ url reject` |
| 3602 | 朴朴超市 | 重写操作符/动作改为官方示例的小写 | `^https:\/\/j1\.pupuapi\.com\/client\/member_card\/index\/my url REJECT` | `^https:\/\/j1\.pupuapi\.com\/client\/member_card\/index\/my url reject` |
| 3614 | 朴朴超市 | 为 JSONJQ 表达式补齐官方示例使用的外层单引号 | `^https:\/\/j1\.pupuapi\.com\/client\/notification\/message_center\/unread_number url jsonjq-response-body .data = []` | `^https:\/\/j1\.pupuapi\.com\/client\/notification\/message_center\/unread_number url jsonjq-response-body '.data = []'` |
| 3898 | QQ音乐 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 120.222.240.171/32, reject` | `ip-cidr, 120.222.240.171/32, reject` |
| 4373 | Soul | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 47.56.131.76/32, reject` | `ip-cidr, 47.56.131.76/32, reject` |
| 4374 | Soul | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 47.97.215.55/32, reject` | `ip-cidr, 47.97.215.55/32, reject` |
| 4375 | Soul | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 47.99.42.29/32, reject` | `ip-cidr, 47.99.42.29/32, reject` |
| 4376 | Soul | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 120.27.235.201/32, reject` | `ip-cidr, 120.27.235.201/32, reject` |
| 4377 | Soul | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 121.196.197.147/32, reject` | `ip-cidr, 121.196.197.147/32, reject` |
| 5476 | 下厨房 | 将 http?: 修成 https?:；原式只匹配 htt/http，遗漏 HTTPS | `^http?:\/\/.*\.pglstatp-toutiao\.com url reject-200` | `^https?:\/\/.*\.pglstatp-toutiao\.com url reject-200` |
| 5597 | 小红书 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https?:\/\/edith\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/search\/(banner_list\|hot_list) url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js` | `^https?:\/\/edith\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/search\/(banner_list\|hot_list) url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaohongshu/xiaohongshu.js` |
| 5598 | 小红书 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https?:\/\/edith\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/search\/(hint\|trending)\? url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js` | `^https?:\/\/edith\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/search\/(hint\|trending)\? url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaohongshu/xiaohongshu.js` |
| 5599 | 小红书 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https?:\/\/(so\|edith)\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/search\/notes\? url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js` | `^https?:\/\/(so\|edith)\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/search\/notes\? url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaohongshu/xiaohongshu.js` |
| 5601 | 小红书 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https?:\/\/edith\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/system_service\/config\? url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js` | `^https?:\/\/edith\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/system_service\/config\? url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaohongshu/xiaohongshu.js` |
| 5602 | 小红书 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https?:\/\/edith\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/system_service\/splash_config url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js` | `^https?:\/\/edith\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/system_service\/splash_config url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaohongshu/xiaohongshu.js` |
| 5604 | 小红书 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https?:\/\/edith\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/note\/widgets url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js` | `^https?:\/\/edith\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/note\/widgets url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaohongshu/xiaohongshu.js` |
| 5608 | 小红书 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https?:\/\/(edith\|rec\|www)\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/note\/(imagefeed\|live_photo\/save) url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js` | `^https?:\/\/(edith\|rec\|www)\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/note\/(imagefeed\|live_photo\/save) url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaohongshu/xiaohongshu.js` |
| 5609 | 小红书 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https?:\/\/(edith\|rec\|www)\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/(followfeed\|homefeed)\? url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js` | `^https?:\/\/(edith\|rec\|www)\.(xiaohongshu\|rnote)\.com\/api\/sns\/v\d+\/(followfeed\|homefeed)\? url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaohongshu/xiaohongshu.js` |
| 5610 | 小红书 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https?:\/\/(edith\|rec\|www)\.(xiaohongshu\|rnote)\.com\/api\/sns\/(v2\/note\/feed\|v3\/note\/videofeed)\? url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js` | `^https?:\/\/(edith\|rec\|www)\.(xiaohongshu\|rnote)\.com\/api\/sns\/(v2\/note\/feed\|v3\/note\/videofeed)\? url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaohongshu/xiaohongshu.js` |
| 5611 | 小红书 | GitHub /raw/ 链接改用 raw.githubusercontent.com；仓库/引用/路径不变 | `^https?:\/\/(edith\|rec\|www)\.(xiaohongshu\|rnote)\.com\/api\/sns\/(v4\/note\/videofeed\|v10\/note\/video\/save)\? url script-response-body https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js` | `^https?:\/\/(edith\|rec\|www)\.(xiaohongshu\|rnote)\.com\/api\/sns\/(v4\/note\/videofeed\|v10\/note\/video\/save)\? url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaohongshu/xiaohongshu.js` |
| 5644 | 小米 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD, XiaoQiang, reject` | `host-keyword, xiaoqiang, reject` |
| 5817 | 晓晓优选 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 114.132.165.205/32, reject` | `ip-cidr, 114.132.165.205/32, reject` |
| 6289 | 优酷 | 规则类型/动作标准化：DOMAIN → host，策略 reject | `DOMAIN, httpdns.alicdn.com, reject` | `host, httpdns.alicdn.com, reject` |
| 6290 | 优酷 | 规则类型/动作标准化：DOMAIN → host，策略 reject | `DOMAIN, adsmind.ugdtimg.com, reject` | `host, adsmind.ugdtimg.com, reject` |
| 6291 | 优酷 | 规则类型/动作标准化：DOMAIN → host，策略 reject | `DOMAIN, amdc.m.youku.com, reject` | `host, amdc.m.youku.com, reject` |
| 6292 | 优酷 | 规则类型/动作标准化：DOMAIN → host，策略 reject | `DOMAIN, apiv4-iyes.youku.com, reject` | `host, apiv4-iyes.youku.com, reject` |
| 6295 | 优酷 | 规则类型/动作标准化：DOMAIN → host，策略 reject | `DOMAIN, yk-ssp.ad.youku.com, reject` | `host, yk-ssp.ad.youku.com, reject` |
| 6296 | 优酷 | 规则类型/动作标准化：DOMAIN → host，策略 reject | `DOMAIN, ykad-data.youku.com, reject` | `host, ykad-data.youku.com, reject` |
| 6297 | 优酷 | 规则类型/动作标准化：DOMAIN → host，策略 reject | `DOMAIN, ad.mobile.youku.com, reject` | `host, ad.mobile.youku.com, reject` |
| 6397 | 邮储银行 | 将其他软件的 ‘- reject-*’ 写法转换为 QX ‘url reject-*’ | `^https?:\/\/static.psbc.com:8090\/mbank_f\/images\/[0-9]+\.png - reject-200` | `^https?:\/\/static.psbc.com:8090\/mbank_f\/images\/[0-9]+\.png url reject-200` |
| 6665 | 知乎 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 118.89.204.198/32, reject` | `ip-cidr, 118.89.204.198/32, reject` |
| 6666 | 知乎 | 规则类型/动作标准化：IP6-CIDR → ip6-cidr，策略 reject | `IP6-CIDR,2402:4e00:1200:ed00:0:9089:6dac:96b6/128, reject` | `ip6-cidr, 2402:4e00:1200:ed00:0:9089:6dac:96b6/128, reject` |
| 6757 | 中国电信 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 122.229.8.47/32, reject` | `ip-cidr, 122.229.8.47/32, reject` |
| 6758 | 中国电信 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 122.229.29.89/32, reject` | `ip-cidr, 122.229.29.89/32, reject` |
| 6834 | 中国移动 | 规则类型/动作标准化：IP-CIDR → ip-cidr，策略 reject | `IP-CIDR, 120.240.95.37/32, reject` | `ip-cidr, 120.240.95.37/32, reject` |
| 7288 | 广告联盟 | 规则类型/动作标准化：host-KEYWORD → host-keyword，策略 reject | `host-KEYWORD, mathtag, reject` | `host-keyword, mathtag, reject` |

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

### L847 · 百度输入法

```text
^https?:\/\/mime\.baidu\.com\/v5\/start_screen_ads/list url reject-dict
```

原因：与 L842 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L842；本次不改变优先级

### L2608 · 酷安

```text
^https?:\/\/api\.coolapk\.com\/v6\/feed\/(detail|replyList)\? url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/coolapk.js
```

原因：按用户要求暂时停用酷安重写，排查网络环境检测；不再对 api.coolapk.com 做 MITM

证据：用户提供的酷安提示将去广告、DNS、Hosts、代理列为可能原因，并反馈关闭 Quantumult X 后恢复；上游酷安分类对 api.coolapk.com 的首页、动态和帖子响应执行脚本修改。该证据说明存在关联风险，不能证明它是唯一原因。

替代：确认酷安恢复后，若要重新启用去广告，先逐条验证规则；本次不恢复 api.coolapk.com 的 MITM。

### L2609 · 酷安

```text
^https?:\/\/api\.coolapk\.com\/v6\/main\/(dataList|indexV8|init) url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/coolapk.js
```

原因：按用户要求暂时停用酷安重写，排查网络环境检测；不再对 api.coolapk.com 做 MITM

证据：用户提供的酷安提示将去广告、DNS、Hosts、代理列为可能原因，并反馈关闭 Quantumult X 后恢复；上游酷安分类对 api.coolapk.com 的首页、动态和帖子响应执行脚本修改。该证据说明存在关联风险，不能证明它是唯一原因。

替代：确认酷安恢复后，若要重新启用去广告，先逐条验证规则；本次不恢复 api.coolapk.com 的 MITM。

### L2610 · 酷安

```text
^https?:\/\/api\.coolapk\.com\/v6\/page\/dataList\? url script-response-body https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/coolapk.js
```

原因：按用户要求暂时停用酷安重写，排查网络环境检测；不再对 api.coolapk.com 做 MITM

证据：用户提供的酷安提示将去广告、DNS、Hosts、代理列为可能原因，并反馈关闭 Quantumult X 后恢复；上游酷安分类对 api.coolapk.com 的首页、动态和帖子响应执行脚本修改。该证据说明存在关联风险，不能证明它是唯一原因。

替代：确认酷安恢复后，若要重新启用去广告，先逐条验证规则；本次不恢复 api.coolapk.com 的 MITM。

### L2811 · 来疯

```text
^https?:\/\/api\.jxedt\.com\/ad\/ url reject-200
```

原因：与 L2356 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L2356；本次不改变优先级

### L4612 · 腾讯游戏

```text
^https?:\/\/qt\.qq\.com\/lua\/mengyou\/get_splash_screen_info url reject
```

原因：与 L4533 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L4533；本次不改变优先级

### L5210 · 网易新闻

```text
^https?:\/\/c\.m\.163\.com\/nc\/gl\/ url reject-200
```

原因：与 L5188 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L5188；本次不改变优先级

### L5214 · 网易严选

```text
^https?:\/\/support\.you\.163\.com\/xhr\/boot\/getBootMedia\.json url reject-200
```

原因：与 L2535 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L2535；本次不改变优先级

### L5221 · 网易邮箱

```text
^https?:\/\/appconf\.mail\.163\.com\/mmad\/ url reject-200
```

原因：与 L2534 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L2534；本次不改变优先级

### L5253 · 网易有钱

```text
^https?:\/\/client\.mail\.163\.com\/apptrack\/confinfo\/searchMultiAds url reject-200
```

原因：与 L5187 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L5187；本次不改变优先级

### L5391 · WPS

```text
^https?:\/\/mobile-pic\.cache\.iciba\.com\/feeds_ad\/ url reject-200
```

原因：可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告；与 L2446 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L2446；本次不改变优先级

### L5619 · 小桔科技

```text
^https?:\/\/ct\.xiaojukeji\.com\/agent\/v3\/feeds url reject
```

原因：可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告；与 L1366 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L1366；本次不改变优先级

### L5621 · 小桔科技

```text
^https?:\/\/res\.xiaojukeji\.com\/resapi\/activity\/mget url reject
```

原因：与 L1369 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L1369；本次不改变优先级

### L6167 · 一淘

```text
^https?:\/\/acs\.m\.taobao\.com\/gw\/mtop\.etao\.noah\.query\/.+tao_splash url reject
```

原因：与 L4488 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L4488；本次不改变优先级

### L6168 · 一淘

```text
^https?:\/\/acs\.m\.taobao\.com\/gw\/mtop\.alimama\.etao\.config\.query\/.+?etao_advertise url reject
```

原因：与 L4486 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L4486；本次不改变优先级

### L6608 · 掌上英雄联盟

```text
^https?:\/\/us\.l\.qq\.com\/exapp url reject-200
```

原因：与 L3900 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L3900；本次不改变优先级

### L6658 · 知乎

```text
USER-AGENT,AVOS*, reject
```

原因：不是本交付范围的域名/IP 分流类型：USER-AGENT

证据：固定的 QX 官方示例、源规则及静态编译检查；详见 docs/compatibility.md

替代：USER-AGENT 是 QX 官方支持的分流类型，但本任务要求分流只含域名/IP；可自行将 user-agent, AVOS*, reject 加入现有 [filter_local]，本工具不改主配置

### L6952 · 追书神器

```text
^https?:\/\/adx-cn\.anythinktech\.com\/bid url reject-200
```

原因：与 L1400 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L1400；本次不改变优先级

### L6958 · 字节跳动

```text
host-suffix, -normal-lq.zijieapi.com, reject
```

原因：目标不符合本工具的标准主机名/通配符检查：-normal-lq.zijieapi.com；不据此断言所有 QX 版本都会拒绝

证据：固定的 QX 官方示例、源规则及静态编译检查；详见 docs/compatibility.md

替代：可能意在匹配含 -normal-lq.zijieapi.com 的域名后缀字符串；改成 host-keyword 会改变匹配边界，需上游说明或 QX 实测后决定

### L6980 · 字节跳动

```text
^https?:\/\/dsp\.toutiao\.com\/api\/xunfei\/ads\/ url reject-200
```

原因：与 L4131 相同匹配条件但动作/参数冲突；保留上游靠前的行为

证据：原版相同匹配式；QX 官方仓库 issue #43 记录首条响应重写行为（用户报告，非完整引擎规范）

替代：逐 App 实测不同返回类型后决定是否替换 L4131；本次不改变优先级

## 全部去重与合并

同一规则即使跨 App 重复，也通过这里和规则清单保留两个 App 的原始归属。

| 原行 | App / 分类 | 去向 | 代表原行 | 原文 |
|---:|---|---|---|---|
| 437 | 爱奇艺 | duplicate | [425] | `host-suffix, cupid.iqiyi.com, reject` |
| 787 | 百度 | duplicate | [781] | `host-suffix, mobads.baidu.com, reject` |
| 796 | 百度 | duplicate | [776] | `host-suffix, baidustatic.com, reject` |
| 797 | 百度 | duplicate | [638] | `host-suffix, duapps.com, reject` |
| 819 | 百度地图 | duplicate | [641] | `host, afd.baidu.com, reject` |
| 879 | 百度网盘 | duplicate | [812] | `^https?:\/\/update\.pan\.baidu\.com\/statistics url reject` |
| 1390 | 滴滴青桔 | duplicate | [386] | `ip-cidr, 203.107.1.1/24, reject` |
| 1632 | 番茄小说 | duplicate | [422] | `host, dig.bdurl.net, reject` |
| 1983 | Google | duplicate | [618] | `host, safebrowsing.googleapis.com, reject` |
| 2620 | 酷狗音乐 | duplicate | [2615] | `host, adsfile.bssdlbig.kugou.com, reject` |
| 2735 | 快手 | merged | [2734] | `^https:\/\/(apissl\|az2-api(-js\|-idc)?)\.(gifshow\|ksapisrv)\.com\/rest\/system\/startup\? url jsonjq-response-body '.sidebarExSquareStyle.commonlyUsedList \|= map(select(.title == "设置" or .title == "历史记录" or .title == "草稿箱" or .title == "我的钱包" or .title == "小程序" or .title == "未成年人模式" or .title == "官方客服" or .title == "内容偏好" or .title == "离线模式" or .title == "稍后再看" or .title == "举报中心" or .title == "挂件"))'` |
| 3071 | 买单吧 | duplicate | [3070] | `host-suffix, c-hzgt2.getui.com, reject` |
| 3678 | 七猫小说 | duplicate | [644] | `host, mobads.baidu.com, reject` |
| 3885 | QQ音乐 | duplicate | [3867] | `host, ad.tencentmusic.com, reject` |
| 3886 | QQ音乐 | duplicate | [3866] | `host, adstats.tencentmusic.com, reject` |
| 3887 | QQ音乐 | duplicate | [3875] | `host, tmead.y.qq.com, reject` |
| 3890 | QQ音乐 | duplicate | [3679] | `host-suffix, gdt.qq.com, reject` |
| 4045 | 什么值得买 | duplicate | [3243] | `host, aaid.uyunad.com, reject` |
| 4090 | 盛趣游戏 | duplicate | [1539] | `^https?:\/\/daoyu\.sdo\.com\/api\/userCommon\/getAppStartAd url reject` |
| 4164 | 顺丰快递小程序 | duplicate | [4155] | `^https?:\/\/ucmp\.sf-express\.com\/proxy\/esgcempcore\/memberGoods\/pointMallService\/goodsList url reject-dict` |
| 4208 | 搜狗 | duplicate | [1834] | `host-suffix, shouji.sougou.com, reject` |
| 4528 | 腾讯广告 | duplicate | [1856] | `^https?:\/\/mi\.gdt\.qq\.com\/gdt_mview\.fcg url reject` |
| 4587 | 腾讯系 | duplicate | [2005] | `host-suffix, cmshow.gtimg.cn, reject` |
| 4588 | 腾讯系 | duplicate | [2006] | `host-suffix, discuz.gtimg.cn, reject` |
| 4589 | 腾讯系 | duplicate | [2007] | `host-suffix, gu.qlogo.cn, reject` |
| 4590 | 腾讯系 | duplicate | [2008] | `host-suffix, py.qlogo.cn, reject` |
| 4591 | 腾讯系 | duplicate | [2009] | `host-suffix, py2.qlogo.cn, reject` |
| 4592 | 腾讯系 | duplicate | [2015] | `host-suffix, beacon.gtimg.com, reject` |
| 4593 | 腾讯系 | duplicate | [2016] | `host-suffix, bla.gtimg.com, reject` |
| 4594 | 腾讯系 | duplicate | [2017] | `host-suffix, lb.gtimg.com, reject` |
| 4595 | 腾讯系 | duplicate | [2018] | `host-suffix, pgdt.gtimg.com, reject` |
| 4596 | 腾讯系 | duplicate | [2019] | `host-suffix, ra.gtimg.com, reject` |
| 4597 | 腾讯系 | duplicate | [2020] | `host-suffix, splashqqlive.gtimg.com, reject` |
| 4598 | 腾讯系 | duplicate | [2021] | `host-suffix, swa.gtimg.com, reject` |
| 4599 | 腾讯系 | duplicate | [2022] | `host-suffix, tui.gtimg.com, reject` |
| 4600 | 腾讯系 | duplicate | [2023] | `host-suffix, wa.gtimg.com, reject` |
| 4601 | 腾讯系 | duplicate | [2024] | `host-suffix, wb.gtimg.com, reject` |
| 4807 | Talkatone | duplicate | [575] | `host-suffix, amazon-adsystem.com, reject` |
| 4815 | Talkatone | duplicate | [4812] | `host-suffix, spadsync.com, reject` |
| 4816 | Talkatone | duplicate | [1991] | `host-suffix, tpc.googlesyndication.com, reject` |
| 4817 | Talkatone | duplicate | [1986] | `host-suffix, googleadsserving.cn, reject` |
| 4819 | Talkatone | duplicate | [4805] | `host-suffix, inner-active.mobi, reject` |
| 4862 | TubeMax | duplicate | [2010] | `host-suffix, app-measurement.com, reject` |
| 4957 | UC浏览器 | duplicate | [4931] | `host-suffix, applog.uc.cn, reject` |
| 4969 | UC浏览器 | duplicate | [4934] | `host-suffix, track.uc.cn, reject` |
| 4976 | UC浏览器 | duplicate | [1637] | `host, tnc3-aliec2.snssdk.com, reject` |
| 5906 | 新浪 | duplicate | [5866] | `host-suffix, ad.sina.com.cn, reject` |
| 5907 | 新浪 | duplicate | [5867] | `host-suffix, ad4.sina.com.cn, reject` |
| 5908 | 新浪 | duplicate | [5868] | `host-suffix, adbox.sina.com.cn, reject` |
| 5909 | 新浪 | duplicate | [5869] | `host-suffix, counter.sina.com.cn, reject` |
| 5910 | 新浪 | duplicate | [5870] | `host-suffix, current.sina.com.cn, reject` |
| 5911 | 新浪 | duplicate | [5871] | `host-suffix, d0.sina.com.cn, reject` |
| 5912 | 新浪 | duplicate | [5872] | `host-suffix, d00.sina.com.cn, reject` |
| 5913 | 新浪 | duplicate | [5873] | `host-suffix, d1.sina.com.cn, reject` |
| 5914 | 新浪 | duplicate | [5874] | `host-suffix, d2.sina.com.cn, reject` |
| 5915 | 新浪 | duplicate | [5875] | `host-suffix, d3.sina.com.cn, reject` |
| 5916 | 新浪 | duplicate | [5876] | `host-suffix, d4.sina.com.cn, reject` |
| 5917 | 新浪 | duplicate | [5877] | `host-suffix, d5.sina.com.cn, reject` |
| 5918 | 新浪 | duplicate | [5878] | `host-suffix, d6.sina.com.cn, reject` |
| 5919 | 新浪 | duplicate | [5879] | `host-suffix, d7.sina.com.cn, reject` |
| 5920 | 新浪 | duplicate | [5880] | `host-suffix, d8.sina.com.cn, reject` |
| 5921 | 新浪 | duplicate | [5881] | `host-suffix, d9.sina.com.cn, reject` |
| 5922 | 新浪 | duplicate | [5882] | `host-suffix, dcads.sina.com.cn, reject` |
| 5923 | 新浪 | duplicate | [5883] | `host-suffix, p4p.sina.com.cn, reject` |
| 5924 | 新浪 | duplicate | [5884] | `host-suffix, pfp.sina.com.cn, reject` |
| 5925 | 新浪 | duplicate | [5885] | `host-suffix, rm.sina.com.cn, reject` |
| 5926 | 新浪 | duplicate | [5886] | `host-suffix, sax.sina.com.cn, reject` |
| 5927 | 新浪 | duplicate | [5887] | `host-suffix, saxn.sina.com.cn, reject` |
| 5928 | 新浪 | duplicate | [5888] | `host-suffix, saxs.sina.com.cn, reject` |
| 5929 | 新浪 | duplicate | [5889] | `host-suffix, sbeacon.sina.com.cn, reject` |
| 5930 | 新浪 | duplicate | [5890] | `host-suffix, slog.sina.com.cn, reject` |
| 5931 | 新浪 | duplicate | [5891] | `host-suffix, woocall.sina.com.cn, reject` |
| 5932 | 新浪 | duplicate | [5892] | `host-suffix, img.amp.ad.sina.com.cn, reject` |
| 5933 | 新浪 | duplicate | [5893] | `host-suffix, img.adbox.sina.com.cn, reject` |
| 5934 | 新浪 | duplicate | [5894] | `host-suffix, m.beacon.sina.com.cn, reject` |
| 5935 | 新浪 | duplicate | [5895] | `host-suffix, r.dmp.sina.com.cn, reject` |
| 5936 | 新浪 | duplicate | [5896] | `host-suffix, int.dpool.sina.com.cn, reject` |
| 5937 | 新浪 | duplicate | [5897] | `host-suffix, mg.games.sina.com.cn, reject` |
| 5938 | 新浪 | duplicate | [5898] | `host-suffix, adm.leju.sina.com.cn, reject` |
| 5939 | 新浪 | duplicate | [5899] | `host-suffix, staticadm.leju.sina.com.cn, reject` |
| 5940 | 新浪 | duplicate | [5900] | `host-suffix, cre.mix.sina.com.cn, reject` |
| 5941 | 新浪 | duplicate | [5901] | `host-suffix, interest.mix.sina.com.cn, reject` |
| 5942 | 新浪 | duplicate | [5902] | `host-suffix, s.img.mix.sina.com.cn, reject` |
| 5943 | 新浪 | duplicate | [5903] | `host-suffix, motu.p4p.sina.com.cn, reject` |
| 5944 | 新浪 | duplicate | [5904] | `host-suffix, count.video.sina.com.cn, reject` |
| 6967 | 字节跳动 | duplicate | [2410] | `host-suffix, ad.toutiao.com, reject` |
| 6968 | 字节跳动 | duplicate | [2411] | `host-suffix, dm.toutiao.com, reject` |
| 6969 | 字节跳动 | duplicate | [2412] | `host-suffix, dsp.toutiao.com, reject` |
| 6970 | 字节跳动 | duplicate | [2413] | `host-suffix, nativeapp.toutiao.com, reject` |
| 6971 | 字节跳动 | duplicate | [2414] | `host-suffix, partner.toutiao.com, reject` |
| 6972 | 字节跳动 | duplicate | [2415] | `host-suffix, track.toutiao.com, reject` |
| 6973 | 字节跳动 | duplicate | [2416] | `host-suffix, dm.pstatp.com, reject` |
| 6974 | 字节跳动 | duplicate | [2417] | `host-suffix, pb3.pstatp.com, reject` |
| 6975 | 字节跳动 | duplicate | [2418] | `host-suffix, s3a.pstatp.com, reject` |
| 7027 | 广告联盟 | duplicate | [5045] | `host-suffix, zlsdk.1rtb.net, reject` |
| 7110 | 广告联盟 | duplicate | [4810] | `host-suffix, gum.criteo.com, reject` |
| 7419 | 广告联盟 | duplicate | [4811] | `host-suffix, smaato.net, reject` |

## MITM hostname 核对

完整主机名清单及每项关联规则见 [hostname-audit.json](hostname-audit.json)。保留能关联 HTTPS 重写的原声明；补充有限可枚举的精确主机名，不自动生成全局 `*`。HTTP-only 规则不额外启用解密；可选/无法 MITM 的提示遵循原作者意图，不自动扩大范围。
上游 `-i.vip.iqiyi.com` 的减号排除语法在固定官方示例中未得到确认；因此保留排除含义，将覆盖它的宽泛 IQIYI 通配符替换成实际规则可枚举的正向主机名。未自动解密排除主机。

### 补充的 hostname（完整）

上游全局声明缺失或范围不符时，优先沿用 App 注释，再从规则展开有限主机；动态匹配仅投影为带固定域名尾部的窄通配符。这些是静态关联推断，仍需核对 QX 实际 SNI，不代表新增主机已经实机证实可 MITM。

| 补充主机名 | 对应原行 | 提取依据 |
|---|---|---|
| `*.amemv.com` | [6981] | projected-wildcard |
| `114.115.217.129` | [2090] | finite-url-host |
| `47.100.65.202` | [1698, 1699, 1700] | finite-url-host |
| `789.kakamobi.cn` | [2344] | finite-url-host |
| `access.if.iqiyi.com` | [467] | finite-url-host |
| `act.vip.iqiyi.com` | [464] | finite-url-host |
| `agn.aty.sohu.com` | [4308] | finite-url-host |
| `als.baidu.com` | [807] | finite-url-host |
| `api-bk*.tv.sohu.com` | [4307] | projected-wildcard |
| `api.k.sohu.com` | [4304, 4309] | finite-url-host |
| `api.tv.sohu.com` | [4307] | finite-url-host |
| `az2-api-idc.gifshow.com` | [2734] | finite-url-host |
| `az2-api-js.ksapisrv.com` | [2734] | finite-url-host |
| `az2-api.gifshow.com` | [2734] | finite-url-host |
| `c.tieba.baidu.com` | [860, 861] | finite-url-host |
| `cards.iqiyi.com` | [468, 469, 471, 473] | finite-url-host |
| `catdot.dianping.com` | [1310] | finite-url-host |
| `catfront.dianping.com` | [1321] | finite-url-host |
| `comment-card.iqiyi.com` | [475] | finite-url-host |
| `config-service.seeyouyima.com` | [3254, 3255] | finite-url-host |
| `csc-service.sgcc.com.cn` | [5076, 5077, 5078, 5079, 5080] | finite-url-host |
| `damang.api.mgtv.com` | [3140] | finite-url-host |
| `data-collector.soulapp.cn` | [4380] | finite-url-host |
| `dc.bz.mgtv.com` | [3147] | finite-url-host |
| `dc2.bz.mgtv.com` | [3147] | finite-url-host |
| `firefly.abchina.com.cn` | [3440] | finite-url-host |
| `gae2-spclient.spotify.com` | [4410] | finite-url-host |
| `hb-boom.api.mgtv.com` | [3142] | finite-url-host |
| `hui.sohu.com` | [4310] | finite-url-host |
| `iadmusicmat.music.126.net` | [5182] | finite-url-host |
| `iface2.iqiyi.com` | [477, 479, 481, 483, 485, 487, 489] | finite-url-host |
| `image.suning.cn` | [4337] | finite-url-host |
| `img.yun.01zhuanche.com` | [4124] | finite-url-host |
| `js-ad.ayximgs.com.ad-universe-cdn.hzhcbkj.cn` | [1243] | finite-url-host |
| `kjp.cupid.iqiyi.com` | [493] | finite-url-host |
| `live.ximalaya.com` | [5464] | finite-url-host |
| `livewsa.ximalaya.com` | [5464] | finite-url-host |
| `m.aty.sohu.com` | [4311] | finite-url-host |
| `m5.amap.com` | [1838, 1839] | finite-url-host |
| `mapi.dianping.com` | [1311, 1312, 1313, 1314] | finite-url-host |
| `me.bz.mgtv.com` | [3144] | finite-url-host |
| `mmg.aty.sohu.com` | [4312, 4313] | finite-url-host |
| `mob-st.bz.mgtv.com` | [3146] | finite-url-host |
| `mobile-consumer-sapp.chery.cn` | [3699] | finite-url-host |
| `mobile-thor.api.mgtv.com` | [3154] | finite-url-host |
| `mobile.api.mgtv.com` | [3149, 3151, 3153] | finite-url-host |
| `mobileapi.ly.com` | [4704] | finite-url-host |
| `mobileso.bz.mgtv.com` | [3156, 3157] | finite-url-host |
| `p.c.music.126.net` | [5179] | finite-url-host |
| `p?.music.126.net` | [5178, 5183] | projected-wildcard |
| `p?c.music.126.net` | [5178] | projected-wildcard |
| `photocdn.sohu.com` | [4314] | finite-url-host |
| `pic.k.sohu.com` | [4305, 4315] | finite-url-host |
| `ptf.flyertrip.com` | [1697] | finite-url-host |
| `richmanmain.jxedt.com` | [2358] | finite-url-host |
| `s.go.sohu.com` | [4316] | finite-url-host |
| `s1.api.tv.itc.cn` | [4306] | finite-url-host |
| `search.video.iqiyi.com` | [491] | finite-url-host |
| `so.xiaohongshu.com` | [5599] | finite-url-host |
| `t7z.cupid.iqiyi.com` | [493] | finite-url-host |
| `t??.baidu.com` | [811] | projected-wildcard |
| `tcmobileapi.17usoft.com` | [4700, 4701, 4702] | finite-url-host |
| `tower.ubixioe.com` | [3063] | finite-url-host |
| `ucmp-static.sf-express.com` | [4163] | finite-url-host |
| `web-mmap-pay.line-apps.com` | [2966] | finite-url-host |
| `wmapi.meituan.com` | [3220] | finite-url-host |
| `www.binance.net` | [1036] | finite-url-host |
| `www.flyert.com` | [1701, 1702, 1703] | finite-url-host |
| `www.flyert.com.cn` | [1702, 1703] | finite-url-host |
| `www.yingwangtech.com` | [1036] | finite-url-host |
| `www.yingwangtech.info` | [1036] | finite-url-host |
| `wx.17u.cn` | [4698, 4699, 4706] | finite-url-host |
| `zhstatic.zhihu.com` | [6709] | finite-url-host |

### 未自动解决 / 可选的重写

| 原行 | App | 状态 | 说明 |
|---:|---|---|---|
| 466 | 爱奇艺 | unresolved | 动态主机名未找到可证实范围；需实机核对 |
| 813 | 百度 | unresolved | 动态主机名未找到可证实范围；需实机核对 |
| 1556 | 豆瓣 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 1557 | 豆瓣 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 1558 | 豆瓣 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 1559 | 豆瓣 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 1560 | 豆瓣 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 1736 | 丰巢 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 1851 | 工商银行 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 1866 | 工银e生活小程序 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 2035 | Google | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 2036 | Google | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 2037 | Google | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 2038 | Google | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 2314 | i3 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 3136 | 芒果TV | unresolved | 动态主机名未找到可证实范围；需实机核对 |
| 3138 | 芒果TV | unresolved | 动态主机名未找到可证实范围；需实机核对 |
| 3669 | PushPlus微信推送广告 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 3905 | QQ音乐 | unresolved | 动态主机名未找到可证实范围；需实机核对 |
| 4856 | TT语音 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 5850 | 携程 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 5852 | 携程 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 5854 | 携程 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 5855 | 携程 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 6220 | 翼支付 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 6222 | 翼支付 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 6402 | 邮储银行 | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 6724 | 智行APP | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |
| 6903 | 中银跨境GO | optional | 上游可选/证书限制提示；不自动扩张 MITM 范围 |

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
| `api.douban.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `consumer.fcbox.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `mobile.flightradar24.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `m*.amap.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `gha.ghac.cn` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `pagead2.googlesyndication.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `elife.icbc.com.cn` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `jiucaigongshe.oss-cn-beijing.aliyuncs.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `api.coolapk.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `ebk.17u.cn` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `*.ubixioe.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `x.seeyouyima.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `*.pipix.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `image.pushplus.plus` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `www.pushplus.plus` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `api.mos.csvw.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `img.yun.01zhuanche` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `mapi.sichuanair.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `business-cdn.shouji.sogou.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `api-pay.soulapp.cn` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `api.shenyin.name` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `image.suning.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `ga-album-cdnqn.52tt.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `*.ly.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `*.17usoft.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `*.17u.cn` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `quic-tcmapi.elong.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `*.music.126.net` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `analytics.163.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `osg-static.sgcc.com.cn` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `m.ctrip.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `ma-adx.ctrip.com` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
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
| `mapi-app.bestpay.com.cn` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |
| `openapi.boc.cn` | inactive | 没有可追溯的有效 HTTPS 重写，或属上游可选/排除范围；保留原声明但不启用 |

## 远程脚本及数据依赖

每行是一次完整 GET 与语法/JSON 检查的证据。检测时间保存在 JSON 清单；相同内容的再次检测记录到 logs，不为制造差异刷新产物时间。脚本内部 eval、网络加载或按环境分支的逻辑，只标记待实测，未执行或声称已经验证其二次依赖。

| 源行 | 原始 URL | 检查 | 字节数 | 动态代码 / 内部网络 |
|---|---|---|---:|---|
| [3186] | [https://github.com/fmz200/wool_scripts/raw/main/Scripts/mlxx/mlxx.js](https://github.com/fmz200/wool_scripts/raw/main/Scripts/mlxx/mlxx.js) | 通过 | 2295 |  |
| [5597, 5598, 5599, 5601, 5602, 5604, 5608, 5609, 5610, 5611] | [https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js](https://github.com/fmz200/wool_scripts/raw/main/Scripts/xiaohongshu/xiaohongshu.js) | 通过 | 28643 | 内部网络 |
| [1140] | [https://raw.githubusercontent.com/Keywos/rule/main/mocks/caiyun.json](https://raw.githubusercontent.com/Keywos/rule/main/mocks/caiyun.json) | 通过 | 314 |  |
| [5262, 5263, 5264, 5265, 5266, 5267, 5268] | [https://raw.githubusercontent.com/Keywos/rule/main/script/wy/js/wyres.js](https://raw.githubusercontent.com/Keywos/rule/main/script/wy/js/wyres.js) | 通过 | 17300 |  |
| [6562] | [https://raw.githubusercontent.com/Maasea/sgmodule/refs/heads/master/Script/Youtube/youtube.response.js](https://raw.githubusercontent.com/Maasea/sgmodule/refs/heads/master/Script/Youtube/youtube.response.js) | 通过 | 132973 | 内部网络 |
| [1521] | [https://raw.githubusercontent.com/NobyDa/Script/master/Bahamut/BahamutAnimeAds.js](https://raw.githubusercontent.com/NobyDa/Script/master/Bahamut/BahamutAnimeAds.js) | 通过 | 1860 | 内部网络 |
| [5530] | [https://raw.githubusercontent.com/NobyDa/Script/master/QuantumultX/File/xjsp.js](https://raw.githubusercontent.com/NobyDa/Script/master/QuantumultX/File/xjsp.js) | 通过 | 1889 |  |
| [5311] | [https://raw.githubusercontent.com/Sliverkiss/QuantumultX/main/AdBlock/xmApp/wnbz.js](https://raw.githubusercontent.com/Sliverkiss/QuantumultX/main/AdBlock/xmApp/wnbz.js) | 通过 | 604 |  |
| [5637] | [https://raw.githubusercontent.com/Sliverkiss/QuantumultX/main/AdBlock/xmApp/xmApp.js](https://raw.githubusercontent.com/Sliverkiss/QuantumultX/main/AdBlock/xmApp/xmApp.js) | 通过 | 340 |  |
| [2744] | [https://raw.githubusercontent.com/app2smile/rules/master/js/adsense.js](https://raw.githubusercontent.com/app2smile/rules/master/js/adsense.js) | 通过 | 2354 |  |
| [3715] | [https://raw.githubusercontent.com/app2smile/rules/master/js/qidian.js](https://raw.githubusercontent.com/app2smile/rules/master/js/qidian.js) | 通过 | 5761 |  |
| [4608] | [https://raw.githubusercontent.com/app2smile/rules/master/js/qq-news.js](https://raw.githubusercontent.com/app2smile/rules/master/js/qq-news.js) | 通过 | 2283 |  |
| [4409] | [https://raw.githubusercontent.com/app2smile/rules/master/js/spotify-json.js](https://raw.githubusercontent.com/app2smile/rules/master/js/spotify-json.js) | 通过 | 381 |  |
| [4408] | [https://raw.githubusercontent.com/app2smile/rules/master/js/spotify-proto.js](https://raw.githubusercontent.com/app2smile/rules/master/js/spotify-proto.js) | 通过 | 71920 | 动态代码、内部网络 |
| [4407] | [https://raw.githubusercontent.com/app2smile/rules/master/js/spotify-qx-header.js](https://raw.githubusercontent.com/app2smile/rules/master/js/spotify-qx-header.js) | 通过 | 135 |  |
| [860] | [https://raw.githubusercontent.com/app2smile/rules/master/js/tieba-json.js](https://raw.githubusercontent.com/app2smile/rules/master/js/tieba-json.js) | 通过 | 9971 |  |
| [861] | [https://raw.githubusercontent.com/app2smile/rules/master/js/tieba-proto.js](https://raw.githubusercontent.com/app2smile/rules/master/js/tieba-proto.js) | 通过 | 97069 |  |
| [5011] | [https://raw.githubusercontent.com/app2smile/rules/master/js/vgtime.js](https://raw.githubusercontent.com/app2smile/rules/master/js/vgtime.js) | 通过 | 292 |  |
| [161, 162] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/51card.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/51card.js) | 通过 | 536 |  |
| [173] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/555Ad.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/555Ad.js) | 通过 | 360 |  |
| [3615, 3616, 3617, 3619, 3621, 3623] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/PupuSplashAds.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/PupuSplashAds.js) | 通过 | 1799 |  |
| [3826] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/QuDa.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/QuDa.js) | 通过 | 267 |  |
| [391, 392] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/adrive/adrive.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/adrive/adrive.js) | 通过 | 1105 |  |
| [830] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/baidumap.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/baidumap.js) | 通过 | 80326 | 动态代码、内部网络 |
| [1102] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/blued.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/blued.js) | 通过 | 246 |  |
| [913, 925, 927] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/bohe/bohe_ads.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/bohe/bohe_ads.js) | 通过 | 956 |  |
| [264, 1154, 1158, 1160] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/cainiao/cainiao.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/cainiao/cainiao.js) | 通过 | 4973 |  |
| [1136] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/caixin/caixinAd.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/caixin/caixinAd.js) | 通过 | 1710 |  |
| [6636] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/cmschina/cmschina.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/cmschina/cmschina.js) | 通过 | 408 |  |
| [466, 467, 468, 469, 471, 473, 475, 477, 479, 481, 487, 491, 493, 3144, 3146, 3147, 3149, 3153, 3154, 3157, 6340, 6342, 6344, 6348, 6350, 6352] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/cnftp.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/cnftp.js) | 通过 | 31606 |  |
| [1419] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/dianyinglieshou.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/dianyinglieshou.js) | 通过 | 1137 |  |
| [1366, 1367, 1368, 1369, 1370, 1372, 1373, 1374, 1375, 1377] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/didi/didiAds.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/didi/didiAds.js) | 通过 | 2745 |  |
| [1728] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/fenbi.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/fenbi.js) | 通过 | 826 |  |
| [1700] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/fly.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/fly.js) | 通过 | 488 |  |
| [2136] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/hengdian.json](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/hengdian.json) | 通过 | 711 |  |
| [2283, 2284] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/huifutianxia_ads.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/huifutianxia_ads.js) | 通过 | 322 |  |
| [2319] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/ithome/ithome.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/ithome/ithome.js) | 通过 | 1311 |  |
| [2515] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/jingdong/jingdong.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/jingdong/jingdong.js) | 通过 | 10303 |  |
| [2545] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/jingxiAd.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/jingxiAd.js) | 通过 | 285 |  |
| [2786, 2790, 2792, 2794] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/keep.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/keep.js) | 通过 | 12394 |  |
| [2692, 2694, 2695, 2696, 2697] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/kuwo/kuwo.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/kuwo/kuwo.js) | 通过 | 4640 |  |
| [2936, 2937] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/lawson.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/lawson.js) | 通过 | 1847 |  |
| [2931] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/lvtusuishenting/ltsst-ad.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/lvtusuishenting/ltsst-ad.js) | 通过 | 869 |  |
| [3093, 3095] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/maimai/maimai_ads.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/maimai/maimai_ads.js) | 通过 | 861 |  |
| [3254, 3255] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/meiyou/meiyou_ads.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/meiyou/meiyou_ads.js) | 通过 | 13949 | 内部网络 |
| [265, 266, 4494, 4495, 5716] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/myBlockAds.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/myBlockAds.js) | 通过 | 7652 |  |
| [6814, 6816] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/picc/picc_ads.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/picc/picc_ads.js) | 通过 | 609 |  |
| [2701] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/quark.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/quark.js) | 通过 | 14279 |  |
| [3985] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/reddit.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/reddit.js) | 通过 | 742 |  |
| [3931, 3935, 3937, 3939, 3941, 3943, 3945, 3947, 3949] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/rrtv_json.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/rrtv_json.js) | 通过 | 25962 | 内部网络 |
| [4063, 4065, 4066, 4067, 4068, 4069, 4070, 4071] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/smzdm/Smzdm.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/smzdm/Smzdm.js) | 通过 | 3220 |  |
| [4058, 4059, 4060, 4061, 4062] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/smzdm/smzdm_ads.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/smzdm/smzdm_ads.js) | 通过 | 1210 |  |
| [4321] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/soda.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/soda.js) | 通过 | 220 |  |
| [4387, 4388, 4389, 4390, 4391, 4392, 4393, 4394, 4395, 4396, 4397, 4398] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/soul/soul_ads.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/soul/soul_ads.js) | 通过 | 15235 | 内部网络 |
| [4380] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/template/req_replace_body.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/template/req_replace_body.js) | 通过 | 353 |  |
| [2090] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/umetrip/umetrip_ads.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/umetrip/umetrip_ads.js) | 通过 | 215 |  |
| [5746] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaotucc.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/xiaotucc.js) | 通过 | 340 |  |
| [5227] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/youdao/dict-youdao-ad.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/youdao/dict-youdao-ad.js) | 通过 | 1202 |  |
| [6371] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/yx.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/yx.js) | 通过 | 134 |  |
| [6589] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/zhangshanggongjiao.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/zhangshanggongjiao.js) | 通过 | 688 |  |
| [6669, 6670, 6673, 6675, 6677, 6680, 6690, 6692, 6694, 6698, 6701] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/zhihu/zhihu.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/zhihu/zhihu.js) | 通过 | 7358 |  |
| [6943] | [https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/zhuanzhuan/zhuanzhuan.js](https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/zhuanzhuan/zhuanzhuan.js) | 通过 | 1020 |  |
| [3298] | [https://raw.githubusercontent.com/fmz200/wool_scripts/refs/heads/main/Scripts/miguvideo/miguvideo_ads.js](https://raw.githubusercontent.com/fmz200/wool_scripts/refs/heads/main/Scripts/miguvideo/miguvideo_ads.js) | 通过 | 13377 | 内部网络 |
| [5514, 5516, 5518, 5520, 5522, 5524, 5526] | [https://raw.githubusercontent.com/ishowshu/qx/refs/heads/main/script/goofish.js](https://raw.githubusercontent.com/ishowshu/qx/refs/heads/main/script/goofish.js) | 通过 | 7810 |  |
| [51] | [https://raw.githubusercontent.com/kokoryh/Script/master/js/12306.js](https://raw.githubusercontent.com/kokoryh/Script/master/js/12306.js) | 通过 | 357 |  |
| [5293] | [https://raw.githubusercontent.com/zZPiglet/Task/master/asset/UnblockURLinWeChat.js](https://raw.githubusercontent.com/zZPiglet/Task/master/asset/UnblockURLinWeChat.js) | 通过 | 86443 | 内部网络 |
| [3799, 3801] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/51job.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/51job.js) | 通过 | 1169 |  |
| [6789] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/airchina.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/airchina.js) | 通过 | 808 |  |
| [2372] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/alicdn.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/alicdn.js) | 通过 | 604 |  |
| [1057, 1058, 1059, 1060] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/bilibiliManga.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/bilibiliManga.js) | 通过 | 2295 |  |
| [2370] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/ccblife.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/ccblife.js) | 通过 | 3262 |  |
| [1455, 1457, 1465] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/ddxq.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/ddxq.js) | 通过 | 1836 |  |
| [1315, 1327] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/dianping.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/dianping.js) | 通过 | 2257 |  |
| [1703] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/flyert.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/flyert.js) | 通过 | 842 |  |
| [1782] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/foliday.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/foliday.js) | 通过 | 972 |  |
| [2131] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/freshippo.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/freshippo.js) | 通过 | 2094 |  |
| [3050] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/mafengwo.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/mafengwo.js) | 通过 | 1044 |  |
| [3076] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/mdb.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/mdb.js) | 通过 | 738 |  |
| [3704] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/qmai.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/qmai.js) | 通过 | 2092 |  |
| [4741, 4742, 4743] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/tuhu.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/tuhu.js) | 通过 | 2610 |  |
| [5845] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/usmile.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/usmile.js) | 通过 | 739 |  |
| [1614, 1616] | [https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/wechatApplet.js](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Scripts/AntiAd/wechatApplet.js) | 通过 | 5966 |  |

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
| 160 | 51信用卡管家 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 173 | 555影视 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 222 | 9to5Mac | kept | 整站阻断 temu.com，会影响正常购物访问；保留上游规则，建议已有 Cats 时先不开奶思分流 |
| 386 | 阿里云 | kept | 阻断整个 IP 子网，可能包含非广告/共享服务；CIDR 标准化未扩大原子网 |
| 407 | 爱美剧 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 435 | 爱奇艺 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 466 | 爱奇艺 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 467 | 爱奇艺 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 469 | 爱奇艺 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 587 | Amazon | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 711 | 百度 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 815 | 百度 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 861 | 百度贴吧 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 869 | 百度网盘 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 943 | 宝宝树孕育 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 1052 | 哔哩哔哩漫画 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 1056 | 哔哩哔哩漫画 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 1059 | 哔哩哔哩漫画 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 1098 | Blued | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 1100 | Blued | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 1140 | 彩云天气 | kept | 此条需要将配套 JSON 复制到 QX 的 Data 目录；更新后也需同步该文件 |
| 1155 | 菜鸟裹裹 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 1248 | Clubmed | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 1346 | 到梦空间 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 1366 | 滴滴出行 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 1390 | 滴滴青桔 | duplicate | 阻断整个 IP 子网，可能包含非广告/共享服务；CIDR 标准化未扩大原子网；上游注释已提示误杀/影响运行，保留原文供核对 |
| 1419 | 电影猎手 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 1423 | 电E宝 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 1427 | 丁香医生 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 1435 | 叮嗒出行 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 1467 | 叮咚买菜 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 1469 | 叮咚买菜 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段；可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 1484 | 钉钉 | kept | 上游注释已提示误杀/影响运行，保留原文供核对 |
| 1508 | 懂车帝 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 1509 | 懂车帝 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 1513 | 懂球帝 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 1530 | 抖音 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 1531 | 抖音 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 1556 | 豆瓣 | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 1557 | 豆瓣 | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 1558 | 豆瓣 | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 1559 | 豆瓣 | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 1560 | 豆瓣 | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 1644 | 番茄小说 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 1650 | 番茄小说 | kept | 上游注释已提示误杀/影响运行，保留原文供核对 |
| 1664 | 番茄小说 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 1668 | 番茄小说 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 1736 | 丰巢 | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 1851 | 工商银行 | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 1866 | 工银e生活小程序 | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 1909 | 光大银行 阳光惠生活 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2035 | Google | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对；上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 2036 | Google | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对；上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 2037 | Google | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对；上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 2038 | Google | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 2088 | 航旅纵横 | kept | 上游注释已提示误杀/影响运行，保留原文供核对 |
| 2110 | 合利宝展业通 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 2128 | 盒马 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 2129 | 盒马 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 2130 | 盒马 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 2131 | 盒马 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 2293 | 火猫 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 2306 | Huawei AspiegelBot | kept | 阻断整个 IP 子网，可能包含非广告/共享服务；CIDR 标准化未扩大原子网 |
| 2314 | i3 | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 2319 | IT之家 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 2398 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2399 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2400 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2401 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2402 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2403 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2404 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2405 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2406 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2407 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2408 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2409 | 今日头条 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2421 | 今日头条 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 2422 | 今日头条 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 2445 | 金山词霸 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 2446 | 金山词霸 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 2515 | 京东 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 2530 | 京东金融 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 2608 | 酷安 | quarantined | 按用户要求暂时停用酷安重写，排查网络环境检测；不再对 api.coolapk.com 做 MITM |
| 2609 | 酷安 | quarantined | 按用户要求暂时停用酷安重写，排查网络环境检测；不再对 api.coolapk.com 做 MITM |
| 2610 | 酷安 | quarantined | 按用户要求暂时停用酷安重写，排查网络环境检测；不再对 api.coolapk.com 做 MITM |
| 2623 | 酷狗音乐 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告；关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2624 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2625 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2626 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2627 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2628 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2629 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2630 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2631 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2632 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2633 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2634 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2635 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2636 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2637 | 酷狗音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2674 | 酷我音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2675 | 酷我音乐 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2691 | 酷我音乐 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 2694 | 酷我音乐 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 2695 | 酷我音乐 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 2736 | 快手 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 2739 | 快手 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 2770 | Keep | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 2824 | 蓝基因 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 2921 | 鲁班到家用户版 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 2966 | Line | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 2979 | LING Club-原菱菱邦 | kept | 上游注释已提示误杀/影响运行，保留原文供核对 |
| 3005 | lofter | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3076 | 买单吧 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 3089 | 脉脉 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 3093 | 脉脉 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3095 | 脉脉 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3157 | 芒果TV | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3175 | 每日精选 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3176 | 每日精选 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3293 | 咪咕视频 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3297 | 咪咕视频 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3304 | 米家 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3313 | 民生银行 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3314 | 民生银行 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3315 | 民生银行 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3316 | 民生银行 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3329 | 墨迹天气 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3330 | 墨迹天气 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3331 | 墨迹天气 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3332 | 墨迹天气 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3346 | 全民生活 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3538 | 皮皮虾 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3539 | 皮皮虾 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3540 | 皮皮虾 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3606 | 朴朴超市 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 3610 | 朴朴超市 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3621 | 朴朴超市 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 3623 | 朴朴超市 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 3646 | pikpak | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3669 | PushPlus微信推送广告 | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 3711 | 起点读书 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3712 | 起点读书 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3713 | 起点读书 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3715 | 起点读书 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3731 | 汽车之家 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3733 | 汽车之家 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3734 | 汽车之家 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3735 | 汽车之家 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 3773 | 汽水音乐 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3786 | 前程无忧 51Job | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 3796 | 前程无忧 51Job | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 3798 | 前程无忧 51Job | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3799 | 前程无忧 51Job | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段；可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3935 | 人人视频 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3947 | 人人视频 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3949 | 人人视频 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3951 | 人人视频 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3956 | 日产智联 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 3971 | 瑞幸咖啡 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 3992 | 三联中读 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 3999 | 山姆会员商店 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 4000 | 山姆会员商店 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4034 | 少数派 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对；可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4121 | 首汽约车 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4123 | 首汽约车 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4142 | 书旗小说 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4158 | 顺丰快递 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4166 | 顺丰快递小程序 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4247 | 搜狗 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4355 | 苏e行 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4517 | 腾讯乘车码 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 4555 | 腾讯手机管家 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 4608 | 腾讯新闻 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4642 | 天府银行小程序 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 4649 | 天猫精灵 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 4693 | 天翼云盘 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4702 | 同程旅行 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4722 | 同花顺 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4733 | 途虎养车 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4734 | 途虎养车 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4757 | 团油 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 4856 | TT语音 | kept | 上游注释已提示误杀/影响运行，保留原文供核对；上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 4906 | UC浏览器 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 4916 | UC浏览器 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 4939 | UC浏览器 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 4946 | UC浏览器 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 4995 | udn news | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 4996 | udn news | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5025 | Vivo | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5026 | Vivo | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5029 | VIVO商城 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5063 | 万词王 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5179 | 网易 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5180 | 网易 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5181 | 网易 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5182 | 网易 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5184 | 网易 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5185 | 网易 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5186 | 网易 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对；可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5189 | 网易 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5199 | 网易考拉 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5215 | 网易严选 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5235 | 网易有道词典 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5257 | 网易云音乐 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5259 | 网易云音乐 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5260 | 网易云音乐 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5261 | 网易云音乐 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5265 | 网易云音乐 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5293 | 微信解除链接限制 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5350 | Whale Cloud (鲸云) | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5354 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5355 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5356 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5357 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5358 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5359 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5360 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5361 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5362 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5363 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5364 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5365 | WiFi万能钥匙 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段；关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5366 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5367 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5368 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5369 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5370 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5371 | WiFi万能钥匙 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5379 | WiFi万能钥匙 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5383 | Wostore (联通沃商店) | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 5385 | Wostore (联通沃商店) | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 5386 | Wostore (联通沃商店) | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 5391 | WPS | quarantined | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5447 | 喜马拉雅 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5448 | 喜马拉雅 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5450 | 喜马拉雅 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5454 | 喜马拉雅 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5458 | 喜马拉雅 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5459 | 喜马拉雅 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5466 | 喜马拉雅 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5467 | 喜马拉雅 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5486 | 闲鱼 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5488 | 闲鱼 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5490 | 闲鱼 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5492 | 闲鱼 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5494 | 闲鱼 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5504 | 闲鱼 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5506 | 闲鱼 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5514 | 闲鱼 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5540 | 向日葵 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 5547 | 小爱音箱 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 5578 | 小合拓展 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5593 | 小红书 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5608 | 小红书 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5609 | 小红书 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5610 | 小红书 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5611 | 小红书 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5619 | 小桔科技 | quarantined | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5625 | 小利生活 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段；关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5627 | 小利生活 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 5635 | 小芒 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5637 | 小芒 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5644 | 小米 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 5724 | 小米运动 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5772 | 小艺 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5773 | 小艺 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 5778 | 小宇宙 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5850 | 携程 | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 5852 | 携程 | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 5854 | 携程 | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 5855 | 携程 | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 5955 | 新浪 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 5956 | 新浪 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 6019 | 兴业银行 | kept | 上游注释已提示误杀/影响运行，保留原文供核对 |
| 6025 | 兴业证券 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 6038 | 雪球 | kept | 上游注释已提示误杀/影响运行，保留原文供核对 |
| 6045 | 雪球 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 6046 | 雪球 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6047 | 雪球 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6048 | 雪球 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6066 | 讯飞输入法 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 6067 | 讯飞输入法 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 6068 | 讯飞输入法 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 6069 | 讯飞输入法 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 6162 | 一汽大众 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6220 | 翼支付 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段；上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 6222 | 翼支付 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段；上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 6233 | 银盛通 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 6238 | 银盛小Y管家 | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 6340 | 优酷 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6367 | 悠洗APP | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 6370 | 悠洗APP | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 6397 | 邮储银行 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 6398 | 邮储银行 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 6402 | 邮储银行 | kept | 上游注释已提示误杀/影响运行，保留原文供核对；上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 6414 | 游民星空 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 6415 | 游民星空 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 6470 | 元聚网络（漫画岛，追书神器，甜瓜小说） | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段 |
| 6610 | 掌上英雄联盟 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6658 | 知乎 | quarantined | 不是本交付范围的域名/IP 分流类型：USER-AGENT |
| 6673 | 知乎 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6675 | 知乎 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6686 | 知乎 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6691 | 知乎 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6692 | 知乎 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6694 | 知乎 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6703 | 知乎 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6704 | 知乎 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6708 | 知乎 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6724 | 智行APP | kept | 上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 6858 | 中华万年历 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 6859 | 中华万年历 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 6860 | 中华万年历 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 6861 | 中华万年历 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 6862 | 中华万年历 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 6863 | 中华万年历 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 6895 | 中信银行 | kept | 主机匹配式存在未转义的点，可能匹配其他字符；保留原意，不批量重写正则，需实机核对 |
| 6903 | 中银跨境GO | kept | 匹配式含登录/支付/订单/购物车/验证相关字样；关键词筛查，需实机确认是否只改广告字段；上游标注可选/无法 MITM；保留规则，但不自动增加相应解密主机名，实际效果未确认 |
| 6941 | 转转 | kept | 可能同时精简正常推荐/信息流；尤其闲鱼商品详情推荐，并非全部是付费广告 |
| 6958 | 字节跳动 | quarantined | 目标不符合本工具的标准主机名/通配符检查：-normal-lq.zijieapi.com；不据此断言所有 QX 版本都会拒绝 |
| 7017 | 广告联盟 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 7018 | 广告联盟 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 7019 | 广告联盟 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 7031 | 广告联盟 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 7046 | 广告联盟 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 7128 | 广告联盟 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |
| 7288 | 广告联盟 | kept | 关键词会匹配任意包含该字符串的域名，作用范围较宽 |

## 功能对比、Cats 与实机待验

- 全量 App / 功能类型对比：[coverage.md](coverage.md) / [coverage.json](coverage.json)。
- Cats 语义去重与完整差集：[cats-comparison.md](cats-comparison.md)。
- 实机验收步骤：[docs/device-checklist.md](docs/device-checklist.md)。
- 尚未实机验证：QX 导入解析、脚本 API 与内置 jq 版本、MITM 合并和证书锁定、App 启动/登录/支付/订单/购物车/验证码、广告实际命中、缓存、不同 App/iOS/QX 版本、自动刷新是否加载到新脚本。
- 本工具没有读取或改写用户 QX 节点、策略组、DNS、证书、主配置、Cats 订阅或 Google 重定向。
