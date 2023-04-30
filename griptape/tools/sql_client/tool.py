from typing import Optional
from attr import define, field
from griptape.core import BaseTool
from griptape.core.decorators import activity
from schema import Schema


@define
class SqlClient(BaseTool):
    engine_url: Optional[str] = field(default=None, kw_only=True, metadata={"env": "ENGINE_URL"})
    engine_name: str = field(kw_only=True)

    @property
    def schema_template_args(self) -> dict:
        return {
            "engine": self.engine_name
        }

    @activity(config={
        "name": "query",
        "description": "Can be used to execute SQL queries in {{ engine }}",
        "schema": Schema(
            str,
            description="SQL query to execute. For example, SELECT, CREATE, INSERT, DROP, DELETE, etc."
        )
    })
    def query(self, value: any) -> str:
        from sqlalchemy import create_engine, text

        engine = create_engine(self.env_value("ENGINE_URL"))

        try:
            with engine.connect() as con:
                results = con.execute(text(value))

                if results.returns_rows:
                    return str([row for row in results]).strip('[]')
                else:
                    return "query successfully executed"

        except Exception as e:
            return f"error executing SQL: {e}"
