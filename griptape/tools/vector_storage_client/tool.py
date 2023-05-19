import importlib
from typing import Optional
import schema
from schema import Schema, Literal
from attr import define, field
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact, ListArtifact
from griptape.core import BaseTool
from griptape.core.decorators import activity
from griptape.drivers import BaseVectorStorageDriver


@define
class VectorStorageClient(BaseTool):
    DEFAULT_QUERY_RESULT_COUNT = 5

    description: Optional[str] = field(default=None, kw_only=True, metadata={"env": "VS_DESCRIPTION"})
    namespace: Optional[str] = field(default=None, kw_only=True, metadata={"env": "VS_NAMESPACE"})
    driver_class: Optional[str] = field(default=None, kw_only=True, metadata={"env": "VS_DRIVER_CLASS"})
    driver_fields: dict = field(factory=dict, kw_only=True, metadata={"env": "VS_DRIVER_FIELDS"})

    driver: BaseVectorStorageDriver = field(init=False)

    def __attrs_post_init__(self):
        module = importlib.import_module("griptape.drivers")
        driver_class = getattr(module, self.value("driver_class"))
        self.driver = driver_class(**self.value("driver_fields"))

    @property
    def schema_template_args(self) -> dict:
        return {
            "description": self.value("description")
        }

    @activity(config={
        "description":
            "Can be used to query a vector database for textual information."
            "{% if description %} Database description: {{ description }}{% endif %}",
        "schema": Schema({
            Literal(
                "query",
                description="Vector database natural language query"
            ): str,
            schema.Optional(
                Literal(
                    "count",
                    description=f"Optional results count. Default is {DEFAULT_QUERY_RESULT_COUNT}"
                ),
                default=DEFAULT_QUERY_RESULT_COUNT
            ): int
        })
    })
    def query(self, params: dict) -> BaseArtifact:
        query = params["values"]["query"]
        count = params["values"].get("count", self.DEFAULT_QUERY_RESULT_COUNT)

        try:
            results = self.driver.query(query, count=count, namespace=self.value("namespace"))

            return ListArtifact([
                TextArtifact(str(result.meta)) for result in results
            ])
        except Exception as e:
            return ErrorArtifact(f"error querying database: {e}")
