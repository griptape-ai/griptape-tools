from __future__ import annotations
from attr import define
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact
from griptape.core import BaseTool
from griptape.core.decorators import activity
from schema import Schema


@define
class PdfReader(BaseTool):
    @activity(config={
        "name": "get_content",
        "description": "Can be used to get all text content from a PDF",
        "schema": Schema(
            str,
            description="Valid path to a PDF file"
        )
    })
    def get_content(self, value: str) -> BaseArtifact:
        from PyPDF2 import PdfReader

        # noinspection PyBroadException
        try:
            reader = PdfReader(value)
            text = " ".join([p.extract_text().strip("\n") for p in reader.pages])
            return TextArtifact(text)
        except Exception as e:
            return ErrorArtifact(f"Failed to read PDF", exception=e)
