import pytest
from tests.utils import install_requirements
from tools.sql_client.tool import SqlClient
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

            assert isinstance(client.query(b"PRAGMA compile_options;"), str)
        