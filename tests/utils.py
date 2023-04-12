import os
import subprocess
import sys
import griptape


def abs_tool_path(path: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(griptape.__file__)), "tools", path)


def install_requirements(tool: str) -> None:
    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        "-r",
        os.path.join(abs_tool_path(tool), "requirements.txt")
    ])

