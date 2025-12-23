
● LLM Werewolf - 完整命令列表和使用说明

  🎮 游戏运行命令

  基础游戏命令

  | 命令                    | 使用方法                           | 意义                                       |
  |-------------------------|------------------------------------|--------------------------------------------|
  | uv run llm-werewolf     | uv run llm-werewolf <配置文件>     | 控制台模式 - 自动运行游戏，显示文本日志    |
  | uv run llm-werewolf-tui | uv run llm-werewolf-tui <配置文件> | TUI模式 - 交互式终端界面，实时显示游戏状态 |
  | uv run werewolf         | uv run werewolf <配置文件>         | 上面命令的别名                             |
  | uv run werewolf-tui     | uv run werewolf-tui <配置文件>     | TUI命令的别名                              |

  示例配置文件

  # 使用Demo配置（无需API密钥）
  uv run llm-werewolf configs/demo.yaml
  uv run llm-werewolf-tui configs/demo.yaml

  # 使用GPT配置（需要API密钥）
  uv run llm-werewolf configs/gpt-5-chaos.yaml

  # 使用多模型配置
  uv run llm-werewolf configs/gaisf.yaml

  # 使用人格系统配置
  uv run llm-werewolf configs/personality_demo.yaml

  🔧 开发和测试命令

  依赖管理

  | 命令                 | 意义             |
  |----------------------|------------------|
  | uv sync              | 安装所有项目依赖 |
  | uv sync --group test | 安装测试依赖     |
  | uv sync --group dev  | 安装开发依赖     |

  测试命令

  | 命令                                              | 意义             |
  |---------------------------------------------------|------------------|
  | uv run python -m pytest                           | 运行所有测试     |
  | uv run python -m pytest tests/core/test_player.py | 运行特定测试文件 |
  | uv run python -m pytest -v                        | 详细输出模式     |
  | uv run python -m pytest --cov=src                 | 运行覆盖率测试   |
  | make test                                         | 运行测试的别名   |

  代码质量

  | 命令              | 意义                       |
  |-------------------|----------------------------|
  | make fmt          | 运行代码格式化和检查       |
  | pre-commit run -a | 手动运行所有pre-commit钩子 |
  | ruff check src/   | 代码检查                   |
  | ruff format src/  | 代码格式化                 |

  📚 文档生成命令

  | 命令                                                                       | 意义               |
  |----------------------------------------------------------------------------|--------------------|
  | make gen-docs                                                              | 生成项目文档       |
  | uv run python scripts/gen_docs.py --source ./src --output ./docs/Reference | 手动生成API文档    |
  | mkdocs serve                                                               | 本地运行文档服务器 |

  🏆 高级功能命令

● 快速启动

  | 命令                                  | 意义                                                |
  |---------------------------------------|-----------------------------------------------------|
  | uv run python quick_start_complete.py | 完整演示脚本 - 包含依赖检查、人格系统演示、锦标赛等 |

  注意: 目前高级功能（人格系统、竞技场等）因循环导入问题暂时不可用，但基础游戏功能完全正常。

  竞技场系统（开发中）

  | 命令                                                              | 意义               |
  |-------------------------------------------------------------------|--------------------|
  | uv run python src/llm_werewolf/arena_cli.py --help                | 查看竞技场命令帮助 |
  | uv run python src/llm_werewolf/arena_cli.py personalities         | 查看可用人格类型   |
  | uv run python src/llm_werewolf/arena_cli.py tournament <配置文件> | 运行锦标赛         |

  🛠 项目管理命令

  清理和维护

  | 命令                  | 意义                     |
  |-----------------------|--------------------------|
  | make clean            | 清理所有生成的文件和缓存 |
  | make uv-install       | 在系统上安装uv包管理器   |
  | make submodule-init   | 初始化Git子模块          |
  | make submodule-update | 更新Git子模块            |

  Poe任务（如果安装了poe）

  | 命令                   | 意义                   |
  |------------------------|------------------------|
  | uv run poe cli         | 运行控制台模式游戏     |
  | uv run poe tui         | 运行TUI模式游戏        |
  | uv run poe docs_gen    | 生成文档               |
  | uv run poe docs_deploy | 部署文档到GitHub Pages |
  | uv run poe docs        | 本地运行文档服务器     |

  📋 配置文件说明

  | 配置文件                      | 用途                     | 需要API密钥 |
  |-------------------------------|--------------------------|-------------|
  | configs/demo.yaml             | Demo配置，使用预设AI代理 | ❌ 不需要   |
  | configs/gpt-5-chaos.yaml      | GPT模型配置              | ✅ 需要     |
  | configs/gaisf.yaml            | 多模型配置（Azure/AWS）  | ✅ 需要     |
  | configs/personality_demo.yaml | 人格系统演示             | ❌ 不需要   |

  🔍 常用使用场景

  1. 快速测试游戏

  # 安装依赖
  uv sync

  # 运行Demo游戏
  uv run llm-werewolf configs/demo.yaml

  2. 开发环境设置

  # 安装所有依赖组
  uv sync --group test --group dev

  # 运行测试
  make test

  # 代码格式化
  make fmt

  3. 文档生成

  # 生成API文档
  make gen-docs

  # 本地查看文档
  mkdocs serve

  4. 依赖检查

  # 检查所有依赖是否正确安装
  uv run python quick_start_complete.py

  ⚠️ 当前状态

  - ✅ 基础游戏功能 - 完全可用
  - ✅ 依赖管理 - networkx 和 numpy 已添加并可用
  - ✅ 测试系统 - 完全可用
  - ✅ 文档生成 - 完全可用
  - ⚠️ 高级功能 - 人格系统和竞技场功能因循环导入暂时不可用
  - 🔄 正在开发 - 循环导入问题修复中

  所有标注 ✅ 的功能都可以正常使用！🎉