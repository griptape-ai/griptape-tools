from griptape.tools import DateTime
from datetime import datetime


class TestDateTime:
    def test_get_current_datetime(self):
        result = DateTime().get_current_datetime({})
        assert datetime.strptime(result.value, "%Y-%m-%d %H:%M:%S.%f").date() == datetime.now().date()
