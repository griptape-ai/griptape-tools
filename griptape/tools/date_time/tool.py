from datetime import datetime
from griptape.artifacts import BaseArtifact, ErrorArtifact, TextArtifact
from griptape.core import BaseTool
from griptape.core.decorators import activity
from schema import Schema, Literal


class DateTime(BaseTool):
    @activity(config={
        "description": "Returns the current date and time",
        "schema": Schema({},ignore_extra_keys = True)
    })
    def get_current_datetime(self, params: dict) -> BaseArtifact:
        try:
            current_datetime = datetime.now()

            return TextArtifact(str(current_datetime))
        except Exception as e:
            return ErrorArtifact(f"error getting current datetime: {e}")
