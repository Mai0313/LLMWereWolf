<center>

# Python 项目模板

[![PyPI version](https://img.shields.io/pypi/v/swebenchv2.svg)](https://pypi.org/project/swebenchv2/)
[![python](https://img.shields.io/badge/-Python_%7C_3.10%7C_3.11%7C_3.12%7C_3.13-blue?logo=python&logoColor=white)](https://www.python.org/downloads/source/)
[![uv](https://img.shields.io/badge/-uv_dependency_management-2C5F2D?logo=python&logoColor=white)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://docs.pydantic.dev/latest/contributing/#badges)
[![tests](https://github.com/Mai0313/repo_template/actions/workflows/test.yml/badge.svg)](https://github.com/Mai0313/repo_template/actions/workflows/test.yml)
[![code-quality](https://github.com/Mai0313/repo_template/actions/workflows/code-quality-check.yml/badge.svg)](https://github.com/Mai0313/repo_template/actions/workflows/code-quality-check.yml)
[![license](https://img.shields.io/badge/License-MIT-green.svg?labelColor=gray)](https://github.com/Mai0313/repo_template/tree/main?tab=License-1-ov-file)
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Mai0313/repo_template/pulls)
[![contributors](https://img.shields.io/github/contributors/Mai0313/repo_template.svg)](https://github.com/Mai0313/repo_template/graphs/contributors)

</center>

🚀 帮助 Python 开发者「快速建立新项目」的模板。内置现代化包管理、工具链、Docker 与完整 CI/CD 工作流程。

点击 [使用此模板](https://github.com/Mai0313/repo_template/generate) 后即可开始。

其他语言: [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## ✨ 重点特色

- 现代 `src/` 布局 + 全面类型注解
- `uv` 超快依赖管理
- pre-commit 包链：ruff、mdformat（含多插件）、codespell、nbstripout、mypy、uv hooks
- 类型严谨：mypy + Pydantic 插件设置
- pytest + coverage + xdist；PR 覆盖率摘要留言
  - 覆盖率门槛 80%，HTML/XML 报告输出至 `.github/`
- MkDocs Material + mkdocstrings（继承图）、markdown-exec、MathJax
  - 开发服务器 `0.0.0.0:9987`；双语文档脚手架
- 文档生成脚本：支持 class/文件两种模式、可选执行 notebook、可并发、保留目录结构
  - 使用 anyio 异步处理与 rich 进度条
- 打包：`uv build`、git-cliff 产 changelog
- CI 自动版本：以 `dunamai` 从 git 产 PEP 440 版本
- Dockerfile 多阶段（内含 uv/uvx 与 Node.js）；Compose 服务（Redis/Postgres/Mongo/MySQL）含 healthcheck 与 volume
- GitHub Actions：测试、质量、文档部署、包打包、Docker 推送（GHCR + buildx cache）、Release Drafter、自动标签、秘密扫描、语义化 PR、pre-commit 自动更新
  - pre-commit 同时挂载多个 git 阶段（pre-commit、post-checkout、post-merge、post-rewrite）
  - i18n 友善检查（允许中文标点等 confusables）
  - 文档列出可替代的环境管理（Rye、Conda）
  - 兼容旧式流程：可用 `uv pip` 导出 `requirements.txt`

## 🚀 快速开始

需求：

- Python 3.10–3.13
- `uv`（可用 `make uv-install` 安装）
- pre-commit hooks：`uv tool install pre-commit` 或 `uv sync --group dev`

本机安装：

```bash
make uv-install
uv sync                     # 安装基础依赖
uv tool install pre-commit  # 或：uv sync --group dev
make format
make test
```

执行示例 CLI：

```bash
uv run repo_template
```

作为模板使用（推荐）：

1. 点击「使用此模板」建立新仓库
2. 全局替换名称：

```bash
# 包/模块名称
find . -type f -name "*.py" -o -name "*.md" -o -name "*.toml" | xargs sed -i 's/repo_template/your_package_name/g'

# 项目显示标题
find . -type f -name "*.py" -o -name "*.md" -o -name "*.toml" | xargs sed -i 's/RepoTemplate/YourProjectTitle/g'
```

1. 更新 `pyproject.toml` 中的作者/描述等元数据

## 🧰 指令一览

```bash
# 开发
make help               # 显示 Makefile 命令列表
make clean              # 清理缓存、产物与产生的文档
make format             # 执行所有 pre-commit hooks
make test               # 执行 pytest
make gen-docs           # 从 src/ 与 scripts/ 生成文档

# Git 子模块（如有使用）
make submodule-init     # 初始化与更新所有子模块
make submodule-update   # 更新所有子模块至远端

# 依赖管理（uv）
make uv-install         # 安装 uv
uv add <pkg>            # 加入正式依赖
uv add <pkg> --dev      # 加入开发依赖
# 同步选用依赖群组
uv sync --group dev     # 安装开发用依赖（pre-commit、poe、notebook）
uv sync --group test    # 安装测试用依赖
uv sync --group docs    # 安装文档用依赖
```

## 📚 文档系统

- 使用 MkDocs Material
- 生成与预览：

```bash
uv sync --group docs
make gen-docs
uv run mkdocs serve    # http://localhost:9987
```

- 自动生成脚本：`scripts/gen_docs.py`（支持 .py 与 .ipynb）

```bash
# 以 class 为单位（默认）
uv run python ./scripts/gen_docs.py --source ./src --output ./docs/Reference gen_docs

# 以文件为单位
uv run python ./scripts/gen_docs.py --source ./src --output ./docs/Reference --mode file gen_docs
```

## 🐳 Docker 与本机服务

`docker-compose.yaml` 内提供本机开发常见服务：`redis`、`postgresql`、`mongodb`、`mysql`，以及演示 `app` 服务（执行 CLI）。

建立 `.env` 设置连接参数（默认如下）：

```bash
REDIS_PORT=6379
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5432
MONGO_PORT=27017
MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=mysql
MYSQL_USER=mysql
MYSQL_PASSWORD=mysql
MYSQL_PORT=3306
```

启动服务：

```bash
docker compose up -d redis postgresql mongodb mysql

# 或启动演示 app
docker compose up -d app
```

## 📦 打包与发布

以 uv 产出包（wheel/sdist 会放在 `dist/`）：

```bash
uv build
```

发布到 PyPI（需设置 `UV_PUBLISH_TOKEN`）：

```bash
UV_PUBLISH_TOKEN=... uv publish
```

CI 亦会在建立 `v*` 标签时自动打包多平台可执行文件与 Python 包，并上传到 GitHub Release。若要自动发布到 PyPI，请在 repository 设置中新增 `UV_PUBLISH_TOKEN` secret（`build_release.yml` 已设置自动发布）。

### 在本机与 PyPI 执行你的 CLI

- 本机（源码仓）：

```bash
uv run repo_template
uv run cli
```

- 发布到 PyPI 后，通过 `uvx`（临时安装后执行）：

```bash
# 若 console script 名称为 "repo_template"
uvx repo_template

# 或指定包/版本与入口名称
uvx --from your-package-name==0.1.0 your-entrypoint
```

## 🧭 选用任务管理（Poe the Poet）

`pyproject.toml` 中的 `[tool.poe.tasks]` 定义了便捷任务，安装 dev 群组（`uv sync --group dev`）或使用 `uvx` 后可用：

```bash
uv run poe docs        # 生成 + 启动文档预览（需 dev 群组）
uv run poe gen         # 生成 + 发布文档（gh-deploy）（需 dev 群组）
uv run poe main        # 执行 CLI（等同 uv run repo_template）

# 或使用 uvx（临时环境，无需本地安装）
uvx poe docs
```

## 🔁 CI/CD 工作流程总览

所有流程位于 `.github/workflows/`，以下为触发时机与用途：

- Tests（`test.yml`）

  - 触发：对 `main`、`release/*` 的 PR
  - 执行 pytest（3.10/3.11/3.12/3.13）并留下覆盖率摘要

- Code Quality（`code-quality-check.yml`）

  - 触发：PR
  - 执行 ruff 与其它 pre-commit hooks

- Docs Deploy（`deploy.yml`）

  - 触发：推送到 `main` 与 `v*` 标签
  - 构建并发布 MkDocs 网站到 GitHub Pages
  - 需在 GitHub 启用 Pages（Actions → Pages）

- Build and Release（`build_release.yml`）

  - 触发：`v*` 标签推送或手动触发
  - 构建多平台可执行文件（通过 PyInstaller）：
    - macOS（ARM64、x64）
    - Linux（x64 GNU、ARM64 GNU）
    - Windows（x64、ARM64）
  - 构建 Python 包（wheel & sdist）
  - 自动发布到 PyPI（需设置 `UV_PUBLISH_TOKEN` secret）
  - 上传所有产物至 GitHub Release
  - 注意：此为 template 示范流程，请依实际项目需求调整

- Publish Docker Image（`build_image.yml`）

  - 触发：推送到 `main` 与 `v*` 标签
  - 发布至 GHCR：`ghcr.io/<owner>/<repo>`（需 `docker/Dockerfile` 内有 `prod` target）

- Release Drafter（`release_drafter.yml`）

  - 触发：推送到 `main` 与 PR 事件
  - 基于 Conventional Commits 维护草稿发布

- PR Labeler（`auto_labeler.yml`）

  - 触发：PR 与 Push
  - 依 `.github/labeler.yml` 自动加标签

- Secret Scanning（`secret_scan.yml`）

  - 触发：Push 与 PR
  - 使用 gitleaks 扫描机密

- Semantic Pull Request（`semantic-pull-request.yml`）

  - 触发：PR 开启/更新
  - 强制 PR 标题符合 Conventional Commits

### CI/CD 设置清单

- PR 标题遵循 Conventional Commits
- （选用）发布到 PyPI：在 repository 设置中新增 `UV_PUBLISH_TOKEN` secret（Settings → Secrets and variables → Actions）
- （选用）启用 GitHub Pages 以发布文档（Settings → Pages → Source: GitHub Actions）
- （选用）发布 Docker 镜像：确认 GHCR 权限已启用（Settings → Actions → General → Workflow permissions: Read and write）

## 🧩 示例 CLI

`pyproject.toml` 内提供 `repo_template` 与 `cli` 两个入口点。目前演示返回简单 `Response` 模型，可依需求替换。

```bash
uv run repo_template
```

## 🤝 贡献

- 欢迎 Issue/PR
- 请遵循程序风格（ruff、类型）
- PR 标题遵循 Conventional Commits

## 📄 授权

MIT — 详见 `LICENSE`。
