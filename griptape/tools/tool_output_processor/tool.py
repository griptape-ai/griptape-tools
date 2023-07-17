from __future__ import annotations
from typing import Optional
from attr import define, field, Factory
from griptape.artifacts import TextArtifact, ErrorArtifact, InfoArtifact, BaseArtifact
from griptape.core import BaseTool
from griptape.core.decorators import activity
from griptape.engines import CsvExtractionEngine, BaseSummaryEngine, PromptSummaryEngine
from griptape.memory.tool import TextToolMemory
from schema import Schema, Literal


@define
class ToolOutputProcessor(BaseTool):
    # override parent
    denylist: Optional[list[str]] = field(default=Factory(lambda: ["extract"]), kw_only=True)
    # override parent
    input_memory: Optional[list[TextToolMemory]] = field(default=None, kw_only=True)
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
        "description": "Can be used to insert text into a memory artifact namespace",
        "schema": Schema({
            "memory_id": str,
            "artifact_namespace": str,
            "text": str
        })
    })
    def insert(self, params: dict):
        memory = self.find_input_memory(params["values"]["memory_id"])
        artifact_namespace = params["values"]["artifact_namespace"]
        text = params["values"]["text"]

        if memory:
            memory.query_engine.upsert_text_artifact(TextArtifact(text), artifact_namespace)

            return InfoArtifact("text was successfully inserted")
        else:
            return ErrorArtifact("memory not found")

    @activity(config={
        "description": "Can be used to extract and format content from memory artifacts into CSV output",
        "uses_default_memory": False,
        "schema": Schema({
            "memory_id": str,
            "artifact_namespace": str,
            Literal(
                "column_names",
                description="Column names for the CSV file"
            ): list[str]
        })
    })
    def extract(self, params: dict) -> list[BaseArtifact] | BaseArtifact:
        memory = self.find_input_memory(params["values"]["memory_id"])
        artifact_namespace = params["values"]["artifact_namespace"]
        column_names = params["values"]["column_names"]

        if memory:
            return self.csv_extraction_engine.extract(
                memory.load_artifacts(artifact_namespace),
                column_names
            )
        else:
            return ErrorArtifact("memory not found")

    @activity(config={
        "description": "Can be used to summarize memory artifacts in a namespace",
        "uses_default_memory": False,
        "schema": Schema({
            "memory_id": str,
            "artifact_namespace": str
        })
    })
    def summarize(self, params: dict) -> TextArtifact | ErrorArtifact:
        memory = self.find_input_memory(params["values"]["memory_id"])
        artifact_namespace = params["values"]["artifact_namespace"]

        if memory:
            return self.summary_engine.summarize_artifacts(
                memory.load_artifacts(artifact_namespace),
            )
        else:
            return ErrorArtifact("memory not found")

    @activity(config={
        "description": "Can be used to search and query memory artifacts in a namespace",
        "uses_default_memory": False,
        "schema": Schema({
            "memory_id": str,
            "artifact_namespace": str,
            Literal(
                "query",
                description="A natural language search query in the form of a question with enough "
                            "contextual information for another person to understand what the query is about"
            ): str
        })
    })
    def search(self, params: dict) -> TextArtifact | ErrorArtifact:
        memory = self.find_input_memory(params["values"]["memory_id"])
        artifact_namespace = params["values"]["artifact_namespace"]
        query = params["values"]["query"]

        if memory:
            return memory.query_engine.query(
                query,
                top_n=self.top_n,
                metadata=memory.namespace_metadata.get(artifact_namespace),
                namespace=artifact_namespace
            )
        else:
            return ErrorArtifact("memory not found")

    def find_input_memory(self, memory_id: str) -> Optional[TextToolMemory]:
        return next((m for m in self.input_memory if isinstance(m, TextToolMemory) and m.id == memory_id), None)
