from schema import Schema, Literal
from griptape.core import BaseTool, action, utils


class Calculator(BaseTool):
    @action(config={
        "name": "calculate",
        "description": "Can be used for making simple calculations in Python",
        "value_schema": Schema({
            Literal(
                "value",
                description="Arithmetic expression parsable in pure Python. Single line only. Don't use any "
                            "imports or external libraries"
            ): str
        })
    })
    def calculate(self, value: bytes) -> str:
        try:
            return utils.PythonRunner().run(value.decode())
        except Exception as e:
            return f"error calculating: {e}"
