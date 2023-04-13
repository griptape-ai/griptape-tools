from typing import Optional
from schema import Schema, Literal
from griptape.core import BaseTool, action
from attr import define, field


@define
class SqlClient(BaseTool):
    engine_url: Optional[str] = field(default=None, kw_only=True, metadata={"env": "ENGINE_URL"})
    engine_name: str = field(kw_only=True)

    @property
    def schema_template_args(self) -> dict:
        return {
            "engine": self.engine_name
        }

    @action(config={
        "name": "query",
        "description": "Can be used to execute SQL queries in {{ engine }}",
        "value_schema": Schema({
            Literal(
                "value",
                description="SQL query to execute. For example, SELECT, CREATE, INSERT, DROP, DELETE, etc."
            ): str
        })
    })
    def query(self, value: bytes) -> str:
        from sqlalchemy import create_engine, text

        engine = create_engine(self.env_value("ENGINE_URL"))

        try:
            with engine.connect() as con:
                results = con.execute(text(value.decode()))

                if results.returns_rows:
                    return str([row for row in results]).strip('[]')
                else:
                    return "query successfully executed"

        except Exception as e:
            return f"error executing SQL: {e}"
