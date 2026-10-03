# Qwen Writer：部署备份与中文小说实验

本仓库保存2026年10月3日对Qwen3.8-27B Heretic/Uncensored Q8_0服务的检查、实验和配置工作。密码、真实API密钥和完整个人应用配置不纳入Git。

## 当前服务

- 模型：Qwen3.8-27B-Uncensored-Q8_0，API别名qwen-novel。
- 推理API：服务器8081；本地SSH隧道18081；Chatbox地址http://127.0.0.1:18081/v1。
- 非思考模式；temperature=.7、top_p=.8、top_k=20、min_p=0、repeat_penalty=1.0、presence_penalty=1.5。
- 上下文131072 tokens，单并发，GPU完整加载，MTP保留。
- 常驻服务代码与原配置：deployment/snapshot-20261003。没有添加开机自启。

## 目录

| 路径 | 内容 |
|---|---|
| 检查报告.md | 故障证据、实验结论、显存与选型分析 |
| 连接与迁移说明.md | Chatbox、MobaXterm、SSH与迁移步骤 |
| deployment/ | 远程实际代码、源码归档、环境与恢复构建脚本 |
| audit/ | 已完成的6次长文实验请求、原始响应、小说及统计 |
| deepseek-experiment/ | 发给DeepSeek的执行提示、实验指引、题库、9组参数、盲评模板 |
| test_longform.py | 参数隔离和悬疑题测试脚本 |
| test_user_prompt.py | 用户原题与中文系统提示对照脚本 |
| ssh_tunnel.py / start-tunnel.ps1 | 独立SSH隧道，两种实现均不保存密码 |
| configure_clients.py | 备份后修改Chatbox与MobaXterm配置，会重设写作默认项 |
| verify_chatbox_connection.py | 根据保存的Chatbox配置验证流式API |
| backup_remote.py | SSH下载部署代码、源码、日志与校验信息 |
| inspect_chatbox.py / remote_check.py | 本次排查辅助工具 |

## 在本地运行

使用Python3.10或更新版本，`python -m pip install -r requirements.txt`。运行`python ssh_tunnel.py`并输入SSH密码，保持该进程运行；或使用已有MobaXterm隧道。不同隧道不能同时占用18081。

`python test_longform.py official_non_thinking`执行一个已定义配置；不带参数运行全部四组。`python test_user_prompt.py`执行用户原题两组对照。**旧脚本会覆盖audit中的同名结果，重跑请先复制脚本和输出到新实验目录，保留本仓库已提交的原始样本。**DeepSeek的新实验应按指引保存独立results目录和attempt，不使用旧脚本覆盖历史证据。

配置前退出应用后台进程，随后执行configure_clients.py并重启Chatbox；脚本先在应用配置目录备份。运行它会更改新会话的默认模型、采样、最大输出和系统写作提示。完整个人配置不提交到本仓库。

## 结果解释

已完成的是固定seed的预实验，不是42次正式评测。减小repeat惩罚改善标点退化，但不能保证所有中文长篇均无重复、跑题或逻辑矛盾。真实提示的调整后例子约4932汉字、全中文；与原例同时改变了采样及系统提示，不能作纯采样归因。

后续正式实验先做27次多种子初筛，再做12次跨题复核和3次系统提示消融。将deepseek-experiment中的文件或ZIP交给DeepSeek。云端DeepSeek通常不能直接访问本机localhost，应交付本地执行脚本或评审上传的原始结果。

## Git与备份

代码、已完成实验原文与统计、部署源码归档提交到Git。新实验results默认忽略，人工审查和确认无密钥后可单独纳入Git或外部存储。模型权重不提交Git，详见deployment/README.md。

远程仓库：https://github.com/chibimiku/qwen-3.8-tools 。后续改动需要再次提交并推送，快照不会自动同步服务器。
