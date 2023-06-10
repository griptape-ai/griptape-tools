from typing import Optional
from attr import define, field
from griptape.artifacts import ListArtifact
from griptape.core import BaseTool
from griptape.core.decorators import activity
from griptape.loaders import SqlLoader
from schema import Schema


@define
class SqlClient(BaseTool):
    sql_loader: SqlLoader = field(kw_only=True)
    tables: list[tuple[Optional[str], str]] = field(kw_only=True) # (schema, table name)
    engine_name: Optional[str] = field(default=None, kw_only=True)
    description: Optional[str] = field(default=None, kw_only=True)

    def table_name(self, table_tuple: tuple[Optional[str], str]) -> str:
        return f"{table_tuple[0]}.{table_tuple[1]}" if table_tuple[0] else table_tuple[1]

    @property
    def schema_template_args(self) -> dict:
        return {
            "engine": self.engine_name,
            "table_schemas": [
                f"{self.table_name(t)} (schema: {self.sql_loader.sql_driver.get_table_schema(self.table_name(t))})"
                for t in self.tables
            ]
        }

    @activity(config={
        "description":
            "Can be used to execute SQL SELECT queries{% if engine %} ({{ engine }}){% endif %} "
            "in the following tables: {{ table_schemas|join(', ') }}",
        "schema": Schema({
            "sql_query": str
        })
    })
    def execute_query(self, params: dict) -> ListArtifact:
        query = params["values"]["sql_query"]

        return ListArtifact.from_list(self.sql_loader.load(query))
