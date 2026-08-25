# Dev Container for Python Project

This directory contains configuration for developing this project in a reproducible environment using [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers).

## What's Included?

There is no Dockerfile. The environment is assembled from a stock image plus [Dev Container Features](https://containers.dev/features), which keeps the image small and removes the base-image tag maintenance a hand-written Dockerfile carries.

- **Base image**: `python:3.10-slim`, matching `.python-version`.
- **Features**:
    - `common-utils`: git, curl, zsh, oh-my-zsh, and a non-root `vscode` user with passwordless sudo. zsh is the default shell.
    - `uv`: the Python package manager the `Makefile` and CI depend on.
- **devcontainer.json**: extension recommendations (Python, Pylance, debugpy, Jupyter, Docker, GitLens, YAML/TOML) and a zsh terminal profile.
- **updateContentCommand**: runs `uv sync && uv cache clean`, so the virtualenv is ready when the container opens.

## Git and SSH

Nothing is mounted for git or SSH, and nothing needs to be. VS Code Dev Containers copies your local `.gitconfig` into the container and forwards your local SSH agent automatically, so `git push` over SSH works with your private keys never leaving the host. GitHub Codespaces does the equivalent.

## Personal shell setup

The container ships a plain oh-my-zsh. Prompt themes, plugins and aliases are personal preference rather than project configuration, so they are deliberately not baked in here.

To get your own setup in every container you open, set `dotfiles.repository` in your VS Code settings once, or enable **Automatically install dotfiles** under [GitHub Settings > Codespaces](https://github.com/settings/codespaces). Either one applies to every container you create and affects nobody else working on this repository.

## Usage

1. Open this folder in VS Code with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) installed.
2. **Reopen in Container** when prompted, or run `Dev Containers: Reopen in Container` from the command palette.

## Customization

- **Change the Python version**: edit the `image` tag and keep `.python-version` in sync.
- **Add a tool**: prefer a feature from [containers.dev/features](https://containers.dev/features) over reintroducing a Dockerfile.
- **Add VS Code extensions**: update the `extensions` list in `devcontainer.json`.

## Troubleshooting

- **After editing `devcontainer.json`**: run `Dev Containers: Rebuild Container`.
- **SSH keys not working**: check that a local ssh-agent is running and that `ssh-add -l` lists your key. The container holds no keys of its own.
- **Permission issues**: the container runs as `vscode`; check file ownership if a write fails.
- For more, see the [VS Code Dev Containers documentation](https://code.visualstudio.com/docs/devcontainers/containers).
