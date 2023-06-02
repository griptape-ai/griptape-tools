from typing import Optional
from griptape.engines import VectorQueryEngine
from schema import Schema, Literal
from attr import define, field
from griptape.artifacts import BaseArtifact, ErrorArtifact
from griptape.core import BaseTool
from griptape.core.decorators import activity


@define
class VectorStorageClient(BaseTool):
    DEFAULT_QUERY_RESULT_COUNT = 5

    description: str = field(kw_only=True)
    query_engine: VectorQueryEngine = field(kw_only=True)
    top_n: int = field(default=5, kw_only=True)
    namespace: Optional[str] = field(default=None, kw_only=True)

    @property
    def schema_template_args(self) -> dict:
        return {
            "description": self.description
        }

    @activity(config={
        "description":
            "Can be used to search a vector database. "
            "Database description: {{ description }}",
        "schema": Schema({
            Literal(
                "query",
                description="Vector database natural language query"
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
            return ErrorArtifact(f"error querying database: {e}")