from typing import Union, Optional
import schema
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact, ListArtifact
from griptape.drivers import OpenAiPromptDriver
from griptape.engines import VectorQueryEngine
from griptape.summarizers import PromptDriverSummarizer
from schema import Schema, Literal
from griptape.core import BaseTool
from griptape.core.decorators import activity
from attr import define, field


@define
class MemoryProcessor(BaseTool):
    @activity(config={
        "description": "Can be used to generate summaries of memory artifacts",
        "load_artifacts": True
    })
    def summarize(self, params: dict) -> Union[ErrorArtifact, ListArtifact]:
        artifacts = [a for a in self.artifacts if isinstance(a, TextArtifact)]
            
        if len(artifacts) == 0:
            return ErrorArtifact("no artifacts found")
        else:
            list_artifact = ListArtifact()

            for artifact in self.artifacts:
                try:
                    summary = PromptDriverSummarizer(
                        driver=OpenAiPromptDriver()
                    ).summarize_text(artifact.value)

                    list_artifact.value.append(TextArtifact(summary))
                except Exception as e:
                    return ErrorArtifact(f"error summarizing text: {e}")

            return list_artifact

    @activity(config={
        "description": "Can be used to search memory artifacts",
        "schema": Schema({
            Literal(
                "query",
                description="A natural language search query"
            ): str,
            schema.Optional(
                Literal(
                    "context",
                    description="Any relevant information that could be useful in generating better search results: "
                                "the original search request, the original SQL query, hints from before, etc."
                )
            ): str
        }),
        "load_artifacts": True
    })
    def search(self, params: dict) -> BaseArtifact:
        query = params["values"]["query"]
        context = params["values"].get("context", None)
        artifacts = [a for a in self.artifacts if isinstance(a, TextArtifact)]

        if len(artifacts) == 0:
            return ErrorArtifact("no artifacts found")
        else:
            query_engine = VectorQueryEngine()

            [query_engine.vector_driver.upsert_text_artifact(a) for a in artifacts]

            return query_engine.query(query, context)