from typing import Union
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact, ListArtifact
from griptape.drivers import OpenAiPromptDriver
from griptape.engines import QueryEngine
from griptape.summarizers import PromptDriverSummarizer
from schema import Schema, Literal
from griptape.core import BaseTool
from griptape.core.decorators import activity
from attr import define, field


@define
class TextProcessor(BaseTool):
    openai_api_key: str = field(kw_only=True)
    query_engine: QueryEngine = field(kw_only=True)

    @activity(config={
        "description": "Can be used to generate a summaries of memory artifacts",
        "pass_artifacts": True
    })
    def summarize(self, params: dict) -> Union[ErrorArtifact, ListArtifact]:
        artifacts = [a for a in self.artifacts]

        if len(artifacts) == 0:
            return ErrorArtifact("text artifacts not found")
        else:
            list_artifact = ListArtifact()

            for artifact in artifacts:
                try:
                    summary = PromptDriverSummarizer(
                        driver=OpenAiPromptDriver(api_key=self.openai_api_key)
                    ).summarize_text(artifact.value)

                    list_artifact.value.append(TextArtifact(summary))
                except Exception as e:
                    return ErrorArtifact(f"error summarizing text: {e}")

            return list_artifact

    @activity(config={
        "description": "Can be used to query memory artifacts for any content",
        "schema": Schema({
            Literal(
                "query",
                description="A search query to run against text artifacts"
            ): str
        }),
        "pass_artifacts": True
    })
    def query(self, params: dict) -> BaseArtifact:
        query = params["values"]["query"]
        artifacts = [a for a in self.artifacts if isinstance(a, TextArtifact)]

        if len(artifacts) == 0:
            return ErrorArtifact("text artifacts not found")
        else:
            list_artifact = ListArtifact()

            for artifact in artifacts:
                try:
                    result = self.query_engine.query(query)

                    list_artifact.value.append(result)
                except Exception as e:
                    return ErrorArtifact(f"error querying text in {artifact}: {e}")

            return list_artifact
