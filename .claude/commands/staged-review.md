---
argument-hint: [language]
description: Review staged changes
tools: Bash, Edit, Glob, Grep, MultiEdit, NotebookEdit, NotebookRead, Read, Task, TodoWrite, WebFetch, WebSearch, Write
model: anthropic.claude-sonnet-4-5-20250929-v1:0
---

## Your task

Perform a comprehensive code review using subagents for key areas:

- code-reviewer
- code-debugger
- code-developer

You need to check all staged changes for potential issues, improvements, and adherence to best practices.
If there is any better way to implement a feature, please update it and provide a detailed explanation of the changes made.
Use $1 as the language for your review comments (default to zh-TW if not specified).
