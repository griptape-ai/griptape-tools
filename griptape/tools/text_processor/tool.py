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
class TextProcessor(BaseTool):
    query_engine: Optional[VectorQueryEngine] = field(default=None, kw_only=True)

    @activity(config={
        "description": "Can be used to generate summaries of text content from memory and/or optional text_input",
        "schema": Schema({
            schema.Optional(
                Literal(
                    "text_input",
                    description="Optional text input in addition to memory artifacts"
                )
            ): str
        }),
        "pass_artifacts": True
    })
    def summarize(self, params: dict) -> Union[ErrorArtifact, ListArtifact]:
        text = params.get("values", {}).get("text_input", None)
        artifacts = [a for a in self.artifacts if isinstance(a, TextArtifact)]

        if text:
            artifacts.append(TextArtifact(text))
            
        if len(artifacts) == 0:
            return ErrorArtifact("no text supplied")
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
        "description": "Can be used to search text content from memory and/or optional text_input",
        "schema": Schema({
            Literal(
                "query",
                description="A search query to run on text"
            ): str,
            schema.Optional(
                Literal(
                    "text_input",
                    description="Optional text input in addition to memory artifacts"
                )
            ): str
        }),
        "pass_artifacts": True
    })
    def search(self, params: dict) -> BaseArtifact:
        text = params["values"].get("text_input", None)
        query = params["values"]["query"]
        artifacts = [a for a in self.artifacts if isinstance(a, TextArtifact)]

        if text:
            artifacts.append(TextArtifact(text))

        if len(artifacts) == 0:
            return ErrorArtifact("no text supplied")
        else:
            query_engine = self.query_engine if self.query_engine else VectorQueryEngine()

            query_engine.insert(artifacts)

            return query_engine.query(query)