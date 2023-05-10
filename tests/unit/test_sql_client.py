import pytest
from griptape.artifacts import BaseArtifact
from tests.utils import install_requirements
from griptape.tools import SqlClient
import sqlite3


@pytest.mark.usefixtures("install_requirements")
class TestSqlClient:
    @pytest.fixture(scope="class")
    def install_requirements(request):
        install_requirements("sql_client")

    def test_search(self):
        with sqlite3.connect(":memory:"):
            client = SqlClient(
                engine_url="sqlite:///:memory:",
                engine_name="sqlite"
            )

            assert isinstance(client.query({"values": {"query": "PRAGMA compile_options;"}}), BaseArtifact)
