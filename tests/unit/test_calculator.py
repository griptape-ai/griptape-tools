from griptape.tools import Calculator


class TestCalculator:
    def test_calculate(self):
        assert Calculator().calculate("5 * 5").value == "25"
