from griptape.artifacts import BaseArtifact
from griptape.tools import SqlClient
import sqlite3


class TestSqlClient:
    def test_search(self):
        with sqlite3.connect(":memory:"):
            client = SqlClient(
                engine_url="sqlite:///:memory:",
                engine_name="sqlite"
            )

            assert isinstance(client.query({"values": {"query": "PRAGMA compile_options;"}}), BaseArtifact)
