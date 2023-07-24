from typing import Optional
from griptape.engines import VectorQueryEngine, BaseSummaryEngine, PromptSummaryEngine
from schema import Schema, Literal
from attr import define, field, Factory
from griptape.artifacts import BaseArtifact, ErrorArtifact, TextArtifact
from griptape.core import BaseTool
from griptape.core.decorators import activity


@define
class KnowledgeBaseClient(BaseTool):
    DEFAULT_QUERY_RESULT_COUNT = 5

    description: str = field(kw_only=True)
    query_engine: VectorQueryEngine = field(kw_only=True)
    summary_engine: BaseSummaryEngine = field(
        kw_only=True,
        default=Factory(lambda: PromptSummaryEngine())
    )
    top_n: int = field(default=5, kw_only=True)
    namespace: Optional[str] = field(default=None, kw_only=True)

    @property
    def schema_template_args(self) -> dict:
        return {
            "description": self.description
        }

    @activity(config={
        "description":
            "Can be used to search a Knowledge Base with the following description: {{ description }}",
        "schema": Schema({
            Literal(
                "query",
                description="A natural language search query in the form of a question with enough "
                            "contextual information for another person to understand what the query is about"
            ): str
        })
    })
    def search(self, params: dict) -> BaseArtifact:
        query = params["values"]["query"]

        try:
            return self.query_engine.query(
                query,
                top_n=self.top_n,
                namespace=self.namespace
            )
        except Exception as e:
            return ErrorArtifact(f"error querying knowledge base: {e}")
