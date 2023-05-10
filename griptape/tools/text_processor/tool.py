from typing import Optional, Union
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact, ListArtifact
from griptape.drivers import OpenAiPromptDriver
from griptape.summarizers import PromptDriverSummarizer
from schema import Schema, Literal
from griptape.core import BaseTool
from griptape.core.decorators import activity
from attr import define, field


@define
class TextProcessor(BaseTool):
    openai_api_key: Optional[str] = field(default=None, kw_only=True, metadata={"env": "OPENAI_API_KEY"})

    @activity(config={
        "name": "summarize",
        "description": "Can be used to generate a summaries of ramp artifacts",
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
                        driver=OpenAiPromptDriver(api_key=self.env_value("OPENAI_API_KEY"))
                    ).summarize_text(artifact.value)

                    list_artifact.value.append(TextArtifact(summary))
                except Exception as e:
                    return ErrorArtifact(f"error summarizing text: {e}")

            return list_artifact

    @activity(config={
        "name": "query",
        "description": "Can be used to query text ramp artifacts for any content",
        "schema": Schema({
            Literal(
                "query",
                description="A search query to run against text artifacts"
            ): str
        }),
        "pass_artifacts": True
    })
    def query(self, params: dict) -> BaseArtifact:
        from llama_index import GPTVectorStoreIndex, Document

        query = params["values"]["query"]
        artifacts = [a for a in self.artifacts if isinstance(a, TextArtifact)]

        if len(artifacts) == 0:
            return ErrorArtifact("text artifacts not found")
        else:
            list_artifact = ListArtifact()

            for artifact in artifacts:
                try:
                    index = GPTVectorStoreIndex.from_documents([Document(artifact.value)])
                    query_engine = index.as_query_engine()
                    result = str(query_engine.query(query)).strip()

                    list_artifact.value.append(TextArtifact(result))
                except Exception as e:
                    return ErrorArtifact(f"error querying text in {artifact}: {e}")

            return list_artifact
