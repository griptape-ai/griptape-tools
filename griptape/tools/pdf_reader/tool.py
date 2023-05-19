from attr import define
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact
from griptape.core import BaseTool
from griptape.core.decorators import activity
from schema import Schema, Literal


@define
class PdfReader(BaseTool):
    @activity(config={
        "description": "Can be used to get all text content from a PDF",
        "schema": Schema({
            Literal(
                "path",
                description="Valid POSIX path to a PDF file"
            ): str
        })
    })
    def get_content(self, params: dict) -> BaseArtifact:
        from PyPDF2 import PdfReader as PyPDF2PdfReader

        path = params["values"]["path"]

        try:
            reader = PyPDF2PdfReader(path)
            text = " ".join([p.extract_text().strip("\n") for p in reader.pages])

            return TextArtifact(text)
        except Exception as e:
            return ErrorArtifact(f"failed to read PDF: {e}")
