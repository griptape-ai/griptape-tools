from __future__ import annotations
from typing import Optional
from attr import define, field, Factory
from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.core import BaseTool
from griptape.core.decorators import activity
from griptape.engines import CsvExtractionEngine, BaseSummaryEngine, PromptSummaryEngine
from griptape.memory.tool import TextToolMemory
from schema import Schema, Literal


@define
class TextMemoryBrowser(BaseTool):
    text_memory: Optional[TextToolMemory] = field(default=None, kw_only=True)
    summary_engine: BaseSummaryEngine = field(
        kw_only=True,
        default=Factory(lambda: PromptSummaryEngine())
    )
    csv_extraction_engine: CsvExtractionEngine = field(
        kw_only=True,
        default=Factory(lambda: CsvExtractionEngine())
    )
    top_n: int = field(default=5, kw_only=True)

    @activity(config={
        "description": "Can be used to extract and format content from memory artifacts into CSV output",
        "schema": Schema({
            "artifact_namespace": str,
            Literal(
                "column_names",
                description="Column names for the CSV file"
            ): list[str]
        })
    })
    def extract(self, params: dict) -> list[BaseArtifact] | BaseArtifact:
        artifact_namespace = params["values"]["artifact_namespace"]
        column_names = params["values"]["column_names"]

        return self.csv_extraction_engine.extract(
            self.text_memory.load_artifacts(artifact_namespace),
            column_names
        )

    @activity(config={
        "description": "Can be used to summarize memory artifacts in a namespace",
        "schema": Schema({
            "artifact_namespace": str
        })
    })
    def summarize(self, params: dict) -> TextArtifact:
        artifact_namespace = params["values"]["artifact_namespace"]

        return self.summary_engine.summarize_artifacts(
            self.text_memory.load_artifacts(artifact_namespace)
        )

    @activity(config={
        "description": "Can be used to search and query memory artifacts in a namespace",
        "schema": Schema({
            "artifact_namespace": str,
            Literal(
                "query",
                description="A natural language search query in the form of a question with enough "
                            "contextual information for another person to understand what the query is about"
            ): str
        })
    })
    def search(self, params: dict) -> TextArtifact:
        artifact_namespace = params["values"]["artifact_namespace"]
        query = params["values"]["query"]

        return self.text_memory.query_engine.query(
            query,
            top_n=self.top_n,
            metadata=self.text_memory.namespace_metadata.get(artifact_namespace),
            namespace=artifact_namespace
        )