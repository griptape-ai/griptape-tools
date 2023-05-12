from typing import Optional
from attr import define, field
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact
from griptape.core import BaseTool
from griptape.core.decorators import activity
from schema import Schema, Literal


@define
class SqlClient(BaseTool):
    engine_url: Optional[str] = field(default=None, kw_only=True, metadata={"env": "ENGINE_URL"})
    engine_name: Optional[str] = field(default=None, kw_only=True, metadata={"env": "ENGINE_NAME"})
    #engine_name: str = field(kw_only=True)

    # @property
    # def schema_template_args(self) -> dict:
    #     return {
    #         "engine": self.engine_name
    #     }

    @activity(config={
        "name": "query",
        "description": "Can be used to execute SQL queries in {{ engine }}",
        "schema": Schema({
            Literal(
                "query",
                description="SQL query to execute. For example, SELECT, CREATE, INSERT, DROP, DELETE, etc."
            ): str
        })
    })
    def query(self, params: dict) -> BaseArtifact:
        from sqlalchemy import create_engine, text

        query = params["values"]["query"]
        engine = create_engine(self.env_value("ENGINE_URL"))

        try:
            with engine.connect() as con:
                results = con.execute(text(query))

                if results.returns_rows:
                    return TextArtifact(str([row for row in results]).strip('[]'))
                else:
                    return TextArtifact("query successfully executed")

        except Exception as e:
            return ErrorArtifact(f"error executing SQL: {e}")
