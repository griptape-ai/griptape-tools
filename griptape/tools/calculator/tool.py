from griptape.core import BaseTool, action, utils
from schema import Schema


class Calculator(BaseTool):
    @action(config={
        "name": "calculate",
        "description": "Can be used for making simple calculations in Python",
        "schema": Schema(
            str,
            description="Arithmetic expression parsable in pure Python. Single line only. Don't use any "
                        "imports or external libraries"
        )
    })
    def calculate(self, value: bytes) -> str:
        try:
            return utils.PythonRunner().run(value.decode())
        except Exception as e:
            return f"error calculating: {e}"
