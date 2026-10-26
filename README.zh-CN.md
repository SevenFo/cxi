# cxi

让不同的 Codex 配置、登录和会话各自保存。支持 macOS、Linux，以及 Bash、zsh。

## 安装

先安装 Codex CLI，然后运行：

```sh
curl -fsSLO https://github.com/SevenFo/cxi/releases/latest/download/install.sh
bash install.sh --shell both
```

重新打开终端，或执行安装器输出的 `source` 命令。

## 常用命令

```sh
cxi new work              # 创建实例
cxi add existing /绝对路径/配置目录  # 注册已有 CODEX_HOME
cxi login work            # 登录
cxi work                  # 启动，也可以写 cxi run work

cxi new personal --from work
cxi login personal
cxi personal --model YOUR_MODEL

cxi ls                    # 查看实例
cxi path work             # 查看目录
cxi env work              # 编辑实例环境变量
```

默认目录是 `~/.codex-instances`，也可以用 `CXI_ROOT` 指定其他位置。启动时为实例设置独立的 `CODEX_HOME`，工作目录仍是当前目录。

`add` 注册已有目录，移除注册时会保留该目录。`--from` 复制设置、说明和技能，登录信息和会话不会一起复制。其他命令见 `cxi help`。

## 配合 Magpie 使用

[CXI for Magpie](https://github.com/SevenFo/magpie-multicodex) 在 Magpie 中提供统一管理页面，可以为各实例选择模型。添加同一个实例目录后，仍然照常运行 `cxi work`。
