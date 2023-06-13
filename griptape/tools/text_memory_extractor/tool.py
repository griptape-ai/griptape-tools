from typing import Union
import schema
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact, ListArtifact
from griptape.drivers import OpenAiPromptDriver
from griptape.memory.tool import TextToolMemory
from griptape.summarizers import PromptDriverSummarizer
from schema import Schema, Literal
from griptape.core import BaseTool
from griptape.core.decorators import activity
from attr import define, field


@define
class TextMemoryExtractor(BaseTool):
    tool_memory: TextToolMemory = field(kw_only=True)

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
            "artifact_namespace": str,
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
        })
    })
    def search(self, params: dict) -> BaseArtifact:
        artifact_namespace = params["values"]["artifact_namespace"]
        query = params["values"]["query"]
        context = params["values"].get("context", None)

        return self.tool_memory.query_engine.query(
            query,
            namespace=artifact_namespace,
            context=context
        )