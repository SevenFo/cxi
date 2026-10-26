# cxi

Run Codex with separate configurations, logins and session histories. Works with Bash and zsh on macOS and Linux.

[中文说明](README.zh-CN.md)

## Install

Install Codex CLI first, then:

```sh
curl -fsSLO https://github.com/SevenFo/cxi/releases/latest/download/install.sh
bash install.sh --shell both
```

Open a new terminal, or run the `source` command printed by the installer.

## Use

```sh
cxi new work
cxi add existing /absolute/path/to/codex-home
cxi login work
cxi work

cxi new personal --from work
cxi login personal
cxi personal --model YOUR_MODEL

cxi ls
cxi path work
cxi env work
```

Instances live in `~/.codex-instances` by default. Set `CXI_ROOT` to use another location. Each launch sets `CODEX_HOME` for that instance and keeps your current working directory.

`add` registers an existing directory; removing that registration keeps the directory. `--from` copies settings, instructions and skills. Logins and session histories stay separate. See `cxi help` for the remaining commands.

## With Magpie

[CXI for Magpie](https://github.com/SevenFo/magpie-multicodex) adds a page in Magpie for choosing a model per instance. Add the same instance directory there and keep using your usual `cxi` commands.
