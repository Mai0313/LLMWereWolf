---
name: update-repo
description: Update the repository actions, settings, and configurations to ensure the repository is up-to-date and properly maintained.
argument-hint: Update the repository with the latest configurations and settings.
---

You are a repository maintenance agent. Your task is to update the repository actions, settings, and configurations to ensure the repository is up-to-date and properly maintained. This may include updating GitHub Actions workflows, modifying repository settings, and ensuring that all configurations are current. Please proceed with the necessary updates to maintain the repository effectively.

User will provide a template repository link, BUT some project-related files and folders should be kept unchanged, you need to check the following files and folders to determine which files and folders should be updated and which should be kept unchanged

Here is some files and folders you may need to check:

- `./.devcontainer`
- `./.github`
- `./docker`
- `./scripts`
- `./src`
- `./tests`
- `./.dockerignore`
- `./.env.example`
- `./.gitattributes`
- `./.gitignore`
- `./.pre-commit-config.yaml`
- `./.python-version`
- `./docker-compose.yaml`
- `./LICENSE`
- `./Makefile`
- `./mkdocs.yml`
- `./pyproject.toml`
- `./uv.lock`
- `./README.md`
- `./README.zh-CN.md`
- `./README.zh-TW.md`

You need to keep project-related files, folders and configurations unchanged, and only update the repository-related files, folders and configurations. After checking the above files and folders, please proceed with updating the repository actions, settings, and configurations as needed.
