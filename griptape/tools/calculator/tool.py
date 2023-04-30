from griptape.core import BaseTool
from griptape.core.decorators import activity
import griptape.utils as utils
from schema import Schema


class Calculator(BaseTool):
    @activity(config={
        "name": "calculate",
        "description": "Can be used for making simple calculations in Python",
        "schema": Schema(
            str,
            description="Arithmetic expression parsable in pure Python. Single line only. Don't use any "
                        "imports or external libraries"
        )
    })
    def calculate(self, value: any) -> str:
        try:
            return utils.PythonRunner().run(value)
        except Exception as e:
            return f"error calculating: {e}"
