from datetime import datetime
from griptape.artifacts import BaseArtifact, ErrorArtifact, TextArtifact
from griptape.core import BaseTool
from griptape.core.decorators import activity


class DateTime(BaseTool):
    @activity(config={
        "uses_default_memory": False,
        "description": "Can be used to return current date and time. Use it when a"
    })
    def get_current_datetime(self, params: dict) -> BaseArtifact:
        try:
            current_datetime = datetime.now()

            return TextArtifact(str(current_datetime))
        except Exception as e:
            return ErrorArtifact(f"error getting current datetime: {e}")
