from griptape.tools import AwsCli


class TestAwsCli:
    def test_execute(self):
        assert isinstance(AwsCli().execute(b"aws help"), str)
