import importlib
import sys
from io import StringIO
from schema import Schema, Literal
from griptape.core import BaseTool, action


class Calculator(BaseTool):
    schemas = {
        "calculate": Schema({
            Literal(
                "action_input",
                description="Arithmetic expression parsable in pure Python. Single line only. Don't use any "
                            "imports or external libraries."
            ): str
        })
    }

    @action(name="calculate", schema=schemas["calculate"])
    def calculate(self, action_input: bytes) -> str:
        try:
            return self._exec_python(action_input.decode())
        except Exception as e:
            return f"error calculating: {e}"

    def _exec_python(self, code: str, libs: dict[str, str] = {}) -> str:
        global_stdout = sys.stdout
        sys.stdout = local_stdout = StringIO()

        try:
            for lib, alias in libs.items():
                imported_lib = importlib.import_module(lib)
                globals()[alias] = imported_lib

            exec(f"print({code})", {}, {alias: eval(alias) for alias in libs.values()})

            output = local_stdout.getvalue()
        except Exception as e:
            output = str(e)
        finally:
            sys.stdout = global_stdout

        return output.strip()
