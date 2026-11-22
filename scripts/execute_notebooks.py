"""Run pure-Python notebooks without sockets, or optionally use a Jupyter kernel."""

import argparse
import ast
import json
import os
import sys
import tempfile
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[1]


def inprocess(notebook, path):
    """Actually execute each Python cell, capturing stdout and rich display output."""
    import matplotlib
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.core.pylabtools import select_figure_formats
    from IPython.display import display
    from IPython.utils.capture import capture_output

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    shell = InteractiveShell.instance()
    select_figure_formats(shell, {"png"})
    namespace = {"__name__": "__main__", "display": display}

    def show(*args, **kwargs):
        for number in plt.get_fignums():
            display(plt.figure(number))
        plt.close("all")

    original_show = plt.show
    plt.show = show
    try:
        count = 0
        for cell in notebook.cells:
            if cell.cell_type != "code":
                continue
            count += 1
            tree = ast.parse(cell.source, filename=f"{path.name}:cell-{count}")
            with capture_output() as captured:
                if tree.body and isinstance(tree.body[-1], ast.Expr):
                    expression = ast.Expression(tree.body[-1].value)
                    statements = ast.Module(body=tree.body[:-1], type_ignores=[])
                    exec(compile(statements, str(path), "exec"), namespace)
                    result = eval(compile(expression, str(path), "eval"), namespace)
                    if result is not None and not cell.source.rstrip().endswith(";"):
                        display(result)
                else:
                    exec(compile(tree, str(path), "exec"), namespace)
            outputs = []
            for stream in ["stdout", "stderr"]:
                value = getattr(captured, stream)
                if value:
                    outputs.append(nbformat.v4.new_output("stream", name=stream, text=value))
            for rich in captured.outputs:
                outputs.append(
                    nbformat.v4.new_output("display_data", data=rich.data, metadata=rich.metadata)
                )
            cell.outputs = outputs
            cell.execution_count = count
    finally:
        plt.show = original_show
        plt.close("all")


def jupyter(notebook, temp):
    from nbclient import NotebookClient

    kernel_path = Path(temp) / "kernels/portfolio"
    kernel_path.mkdir(parents=True, exist_ok=True)
    (kernel_path / "kernel.json").write_text(
        json.dumps(
            {
                "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
                "display_name": "Portfolio Python",
                "language": "python",
            }
        )
    )
    os.environ["JUPYTER_PATH"] = temp + os.pathsep + os.environ.get("JUPYTER_PATH", "")
    NotebookClient(
        notebook, timeout=180, kernel_name="portfolio", resources={"metadata": {"path": str(ROOT)}}
    ).execute()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=["inprocess", "jupyter"], default="inprocess")
    args = parser.parse_args()
    os.chdir(ROOT)
    with tempfile.TemporaryDirectory() as temp:
        for path in sorted((ROOT / "notebooks").glob("*.ipynb")):
            notebook = nbformat.read(path, as_version=4)
            if args.engine == "inprocess":
                inprocess(notebook, path)
            else:
                jupyter(notebook, temp)
            nbformat.validate(notebook)
            nbformat.write(notebook, path)
            print(f"Executed {path.name} ({args.engine})", flush=True)


if __name__ == "__main__":
    main()
