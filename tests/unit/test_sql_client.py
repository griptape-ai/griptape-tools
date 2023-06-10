import pytest
from griptape.drivers import SqlalchemySqlDriver
from griptape.loaders import SqlLoader
from griptape.tools import SqlClient
import sqlite3


class TestSqlClient:
    @pytest.fixture
    def driver(self):
        new_driver = SqlalchemySqlDriver(
            engine_url="sqlite:///:memory:"
        )

        new_driver.execute_query(
            "CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER, city TEXT);"
        )

        new_driver.execute_query(
            "INSERT INTO test_table (name, age, city) VALUES ('Alice', 25, 'New York');"
        )

        return new_driver

    def test_execute_query(self, driver):
        with sqlite3.connect(":memory:"):
            client = SqlClient(
                loader=SqlLoader(sql_driver=driver),
                engine_name="sqlite"
            )
            result = client.execute_query({"values": {"sql_query": "SELECT * from test_table;"}})

            assert len(result.value) == 1
            assert result.value[0].value == "1,Alice,25,New York"

    def test_get_schema(self, driver):
        with sqlite3.connect(":memory:"):
            client = SqlClient(
                loader=SqlLoader(sql_driver=driver),
                engine_name="sqlite"
            )
            result = client.get_schema({"values": {"table_name": "test_table"}})

            assert result.value == "[('id', INTEGER()), ('name', TEXT()), ('age', INTEGER()), ('city', TEXT())]"
