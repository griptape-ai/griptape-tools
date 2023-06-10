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
    schema_name: Optional[str] = field(default=None, kw_only=True)
    table_name: str = field(kw_only=True)
    table_description: Optional[str] = field(default=None, kw_only=True)
    engine_name: Optional[str] = field(default=None, kw_only=True)

    @property
    def full_table_name(self) -> str:
        return f"{self.schema_name}.{self.table_name}" if self.schema_name else self.table_name

    @property
    def schema_template_args(self) -> dict:
        return {
            "engine": self.engine_name,
            "table_name": self.full_table_name,
            "table_description": self.table_description,
            "table_schema": self.sql_loader.sql_driver.get_table_schema(self.table_name, schema=self.schema_name)
        }

    @activity(config={
        "description":
            "Can be used to execute{% if engine %} {{ engine }}{% endif %} SQL SELECT queries "
            "in table {{ table_name }}.\n"
            "{{ table_name }} schema: {{ table_schema }}{% if table_description %}\n"
            "{{ table_name }} description: {{ table_description }}{% endif %}",
        "schema": Schema({
            "sql_query": str
        })
    })
    def execute_query(self, params: dict) -> ListArtifact:
        query = params["values"]["sql_query"]

        return ListArtifact.from_list(self.sql_loader.load(query))
