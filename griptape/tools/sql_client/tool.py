from typing import Optional, Union
from attr import define, field
from griptape.artifacts import ListArtifact, TextArtifact, ErrorArtifact
from griptape.core import BaseTool
from griptape.core.decorators import activity
from griptape.loaders import SqlLoader
from schema import Schema


@define
class SqlClient(BaseTool):
    loader: SqlLoader = field(kw_only=True)
    engine_name: Optional[str] = field(default=None, kw_only=True)

    @property
    def schema_template_args(self) -> dict:
        return {
            "engine": self.engine_name
        }

    @activity(config={
        "description": "Can be used to execute SQL SELECT queries{% if engine %} in {{ engine }}{% endif %}",
        "schema": Schema({
            "sql_query": str
        })
    })
    def execute_query(self, params: dict) -> ListArtifact:
        query = params["values"]["sql_query"]

        return ListArtifact.from_list(self.loader.load(query))

    @activity(config={
        "description": "Can be used to get a SQL table schema",
        "schema": Schema({
            "table_name": str
        })
    })
    def get_schema(self, params: dict) -> Union[TextArtifact, ErrorArtifact]:
        table_name = params["values"]["table_name"]
        schema = self.loader.sql_driver.get_schema(table_name)

        if schema:
            return TextArtifact(schema)
        else:
            return ErrorArtifact(f"schema for {table_name} not found")
