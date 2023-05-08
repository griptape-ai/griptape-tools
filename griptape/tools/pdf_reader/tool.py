from __future__ import annotations
import logging
import json
from typing import Union
from attr import define, field
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact
from schema import Schema
from griptape.core import BaseTool
from griptape.core.decorators import activity


@define
class PdfReader(BaseTool):
    include_links: bool = field(default=True, kw_only=True, metadata={"env": "INCLUDE_LINKS"})

    @activity(config={
        "name": "get_content",
        "description": "Can be used to get all text content from a PDF",
        "schema": Schema(
            str,
            description="Valid path to a PDF file"
        )
    })
    def get_content(self, value: str) -> BaseArtifact:
        from PyPDF2 import PdfReader as PDFR

        # noinspection PyBroadException
        try:
            reader = PDFR(value)
            text = " ".join([p.extract_text().strip("\n") for p in reader.pages])
            return TextArtifact(text)
        except Exception as e:
            return ErrorArtifact(f"Failed to read PDF", exception=e)
