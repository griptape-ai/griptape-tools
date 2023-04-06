from griptape_tools import Calculator


class TestCalculator:
    def test_calculate(self):
        assert Calculator().calculate(b"5 * 5") == "25"
