# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "anyio",
#     "fire",
#     "notebook",
#     "pydantic",
#     "rich",
# ]
# ///
import ast
import shutil
from typing import Literal
import asyncio
from pathlib import Path
from functools import cached_property

import anyio
import nbformat
from pydantic import Field, BaseModel, ConfigDict, computed_field
from nbconvert import MarkdownExporter
from rich.console import Console
from rich.progress import TaskID, Progress
from nbconvert.preprocessors import ExecutePreprocessor

console = Console()


class DocsGenerator(BaseModel):
    """DocsGenerator is a class that generates documentation for Python files or classes within a specified source directory.

    Attributes:
        source (str): The source directory or file path.
        output (str): The output directory path.
        exclude (str): Comma-separated list of folders or files to exclude.
        mode (Literal["file", "class"]): Mode of documentation generation, either by file or class.

    Methods:
        gen_docs() -> None:
            Generates documentation by file or class.

        __call__() -> None:
            Asynchronously calls the gen_docs method.

    Examples:
    === "Using CLI"
        ```bash
        python ./scripts/gen_docs.py --source ./src --output ./docs/Reference --exclude .venv gen_docs
        ```

    === "Using uv"
        ```bash
        uv run python ./scripts/gen_docs.py
        ```
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    source_path: Path = Field(
        ...,
        title="The Source File Path or Folder Path",
        description="This field can be a file path or folder path, if it is a folder path, it will automatically search for python and ipynb files.",
        examples=["./src"],
        alias="source",
        frozen=True,
    )
    output_path: Path = Field(
        ...,
        title="The Output Path",
        description="The output path for the generated documentation.",
        examples=["./docs/Reference"],
        alias="output",
        frozen=True,
    )
    exclude: str = Field(
        default=".venv",
        description="Exclude the folder or file, it should be separated by comma.",
        examples=[".venv,.git,.idea"],
    )
    mode: Literal["file", "class"] = Field(
        default="class",
        title="The Document Style",
        description="Generate docs by file or class.",
        examples=["file", "class"],
    )
    execute: bool = Field(
        default=False,
        title="Execute Notebook",
        description="Execute the notebook before generating the documentation.",
        examples=["True", "False"],
    )
    concurrency: int = Field(
        default=10,
        title="Concurrency Limit",
        description="Maximum number of files to process concurrently.",
        examples=[5, 10, 20],
    )

    def _get_all_files(self, suffix: str) -> list[Path]:
        targets = [s.strip() for s in suffix.split(",")]
        all_files: list[Path] = []
        for target in targets:
            filename = list(self.source_path.rglob(f"*.{target}"))
            all_files.extend(filename)
        return all_files

    @computed_field
    @cached_property
    def source_files(self) -> list[Path]:
        """Computed property that returns the source path as a Path object.

        Returns:
            Path: The source path.
        """
        if self.source_path.is_dir():
            if self.output_path.exists():
                shutil.rmtree(self.output_path.absolute())
            exclude_list = [ex.strip() for ex in self.exclude.split(",")]
            need_to_exclude = list({*exclude_list, ".venv", "__init__.py"})
            all_files = self._get_all_files(suffix="py,ipynb")
            all_files = [
                file for file in all_files if not any(f in file.parts for f in need_to_exclude)
            ]
        elif self.source_path.is_file():
            all_files = [self.source_path]
        else:
            all_files = []
            console.log(
                f"[red]Source path {self.source_path} does not exist or is not a valid file or directory."
            )
        return all_files

    async def _prepare_docs_path(self, file: Path) -> Path:
        # 因為多層結構的資料夾 我們希望他可以依然放在對應的資料夾內
        filename = file.with_suffix(".md").name
        if file.parent.as_posix() != ".":
            related_path = file.parent.relative_to(self.source_path)
            docs_path = Path(f"{self.output_path}/{related_path}/{filename}")
        else:
            docs_path = Path(f"{self.output_path}/{filename}")
        docs_path.parent.mkdir(parents=True, exist_ok=True)
        docs_path.unlink(missing_ok=True)
        return docs_path

    async def _gen_python_docs(self, file: Path) -> str:
        docs_path = await self._prepare_docs_path(file=file)
        if self.mode == "file":
            note_content = f"::: {file.with_suffix('').as_posix().replace('/', '.')}\n"
        elif self.mode == "class":
            async with await anyio.open_file(file, encoding="utf-8") as f:
                contents = await f.read()
                tree = ast.parse(source=contents, filename=file)

            note_content = ""
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    note_content += (
                        f"::: {file.with_suffix('').as_posix().replace('/', '.')}.{node.name}\n"
                    )
        else:
            raise ValueError("Invalid mode")
        if not note_content:
            note_content = f"::: {file.with_suffix('').as_posix().replace('/', '.')}\n"
        docs_path.write_text(data=note_content, encoding="utf-8")
        return docs_path.as_posix()

    async def _gen_notebook_docs(self, file: Path) -> str:
        docs_path = await self._prepare_docs_path(file=file)
        # 讀取 notebook 檔案
        async with await anyio.open_file(file, encoding="utf-8") as f:
            notebook_content = nbformat.reads(await f.read(), as_version=4)

        if self.execute:
            # 執行 notebook 中的所有 code block
            execute_preprocessor = ExecutePreprocessor(
                timeout=600,
                kernel_name="python3",
                allow_errors=True,
                store_widget_state=True,
                record_timing=True,
            )
            if not isinstance(execute_preprocessor, ExecutePreprocessor):
                raise TypeError("ExecutePreprocessor is not a valid type")
            execute_preprocessor.preprocess(
                notebook_content, {"metadata": {"path": file.parent.as_posix()}}
            )

        # 使用執行後的 notebook 內容轉換為 markdown
        markdown_exporter = MarkdownExporter(template_name="markdown")
        if not isinstance(markdown_exporter, MarkdownExporter):
            raise TypeError("TemplateExporter is not a valid type")
        markdown_output, _ = markdown_exporter.from_notebook_node(notebook_content)
        # 寫入轉換後的 markdown 內容到檔案
        async with await anyio.open_file(docs_path, "w", encoding="utf-8") as f:
            await f.write(markdown_output)
        return docs_path.as_posix()

    async def _process_file(self, file: Path, progress: Progress, task: TaskID) -> str:
        """Process a single file and update progress."""
        try:
            if file.suffix == ".ipynb":
                result = await self._gen_notebook_docs(file=file)
            elif file.suffix == ".py":
                result = await self._gen_python_docs(file=file)
            else:
                console.log(f"Unsupported file type: {file.suffix}")
                result = ""

            # Update progress
            progress.update(task, advance=1, description=f"[cyan]Processed {file.name}")
            return result
        except Exception as e:
            console.log(f"[red]Error processing {file}: {e!s}")
            progress.update(task, advance=1, description=f"[red]Failed {file.name}")
            return ""

    async def _process_batch(
        self, files: list[Path], progress: Progress, task: TaskID
    ) -> list[str]:
        """Process a batch of files concurrently with semaphore to control concurrency."""
        semaphore = asyncio.Semaphore(self.concurrency)

        async def process_with_semaphore(file: Path) -> str:
            async with semaphore:
                return await self._process_file(file, progress, task)

        tasks = [process_with_semaphore(file) for file in files]
        return await asyncio.gather(*tasks)

    async def gen_docs(self) -> None:
        with Progress() as progress:
            total_files = len(self.source_files)
            task = progress.add_task(f"[green]Generating {total_files}...", total=total_files)

            if not self.source_files:
                console.log("[yellow]No files found to process")
                return

            # Process all files concurrently with controlled concurrency
            results = await self._process_batch(self.source_files, progress, task)

            # Summarize results
            successful = len([r for r in results if r])
        console.log(
            f"[green]Documentation generation complete ({successful}/{total_files})!",
            highlight=True,
        )

    async def __call__(self) -> None:
        """Asynchronously calls the gen_docs method.

        This method is intended to be used as a callable object, which when called, will execute the gen_docs method asynchronously.

        Examples:
            >>> import asyncio
            >>> pair_list = {"./src": "./docs/Reference"}
            >>> for key, value in pair_list.items():
            ...     docs_generator = DocsGenerator(
            ...         source=key, output=value, exclude=".venv", mode="class"
            ...     )
            ...     asyncio.run(docs_generator())
        """
        await self.gen_docs()


if __name__ == "__main__":
    import fire

    fire.Fire(DocsGenerator)
