# 实例恢复说明

## 目前保存的内容

`snapshot-20261003/`从正在工作的服务器下载，包含实际启动脚本、修改前脚本、旧安装/编译/下载脚本、历史监控及nginx代码、服务日志、环境与CMake选项、API快照、模型SHA256，以及锁定版本的llama.cpp完整已跟踪源码归档。

`manifest.json`记录源代码commit及各备份文件的大小、SHA256。源码归档独立保存在本仓库，不依赖原实例存活。日志是截取时快照，不会自动跟随线上更新。

公开仓库排除原始服务器运行日志（*.log）及完整environment.txt；这些文件仍在本地快照内，manifest保留其校验值。公开恢复环境记录在environment-summary.md。小说测试请求、响应及原文在audit中完整保存。

历史`setup_coletti.sh`含删除已有源码目录的逻辑，**不要作为本次恢复入口执行**。`restore-build.sh`是新写的保守恢复构建入口，会拒绝覆盖已有源码目录。

## 失去原实例后恢复

1. 在新服务器准备NVIDIA驱动、兼容CUDA工具链、cmake、g++、curl和tar。原构建使用CUDA12.1、GCC11.4、RTX4090计算能力89，详见environment-summary.md。本次没有在另一台机器实测完整重建。
2. 上传本仓库，执行`bash deployment/restore-build.sh`，默认解压与编译到`/root/autodl-tmp/llama.cpp`。GPU不同需设置GPU_ARCH；工具链目录不同设置CUDA_ROOT；内存不足可降低BUILD_JOBS。
3. 取得模型`JonathanColetti/Qwen3.8-27B-Uncensored-GGUF`中的`Qwen3.8-27B-Uncensored-Q8_0.gguf`，保存到`/root/autodl-tmp/models/`。按`model-sha256.txt`核对哈希；没有相同哈希不能声称复原了同一模型。历史下载脚本使用main，它会随发布者更新，优先使用`model-provenance.json`里与哈希匹配的锁定revision（若已核验匹配）。
4. 将快照的`run_server_coletti.sh`与`start-qwen-service.sh`复制到`/root/autodl-tmp/`，赋予执行权限，再运行`bash /root/autodl-tmp/start-qwen-service.sh`。这些是原实例实际路径；改LLM_ROOT构建时也必须改启动脚本的BIN、MODEL、DIR。
5. 在新服务器检查`curl -fsS http://127.0.0.1:8081/health`与`curl -fsS http://127.0.0.1:8081/v1/models`，确认存在qwen-novel别名。
6. 按根目录《连接与迁移说明.md》重建SSH隧道，只改服务器地址和SSH端口，保留本地18081、远程8081和模型别名。Chatbox配置脚本只添加这项服务，不需要恢复整份含其他密钥的用户配置。
7. 在本地运行`python verify_chatbox_connection.py`，再用真实用户题目复核中文长文输出。

## 大文件边界

模型权重约29GB没有放入Git，二进制也未纳入；源码归档和编译参数已经保存。要做到“上游删除文件也能恢复权重”，还需要将已校验模型另存到用户控制的磁盘/对象存储。这个仓库的校验值可用于核对，但不能代替模型本身。

原vision projector也保存了校验值，但当前文本小说服务没有加载它。恢复纯文本服务不需要先下载这个投影文件。

当前为手动幂等启动，没有新增开机自动启动，也没有启用历史空闲关机脚本。
