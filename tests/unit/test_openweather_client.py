import unittest
from unittest.mock import patch
from griptape.tools.openweather_client.tool import OpenWeatherClient
from griptape.artifacts import TextArtifact, ErrorArtifact

class TestOpenWeatherClient(unittest.TestCase):

    def setUp(self):
        self.api_key = "YOUR_API_KEY"
        self.weather_client = OpenWeatherClient(api_key=self.api_key)

    @patch('griptape.tools.openweather_client.tool.requests.get')
    def test_get_weather_by_city(self, mock_get):
        mock_response_data = {
            "weather": [{
                "description": "clear sky"
            }],
            "main": {
                "temp": 67.73
            }
        }
        mock_get.return_value.json.return_value = mock_response_data
        mock_get.return_value.status_code = 200

        city_name = "London"
        response_artifact = self.weather_client._get_weather_by_city({"values": {"city_name": city_name}})

        self.assertIsInstance(response_artifact, TextArtifact)

        response_data = eval(response_artifact.to_text())

        self.assertEqual(response_data["weather"][0]["description"], "clear sky")
        self.assertEqual(response_data["main"]["temp"], 67.73)

    @patch('griptape.tools.openweather_client.tool.requests.get')
    def test_get_weather_by_city_error(self, mock_get):

        mock_get.return_value.status_code = 404

        city_name = "NonExistentCity"
        response_artifact = self.weather_client._get_weather_by_city({"values": {"city_name": city_name}})

        self.assertIsInstance(response_artifact, ErrorArtifact)
        self.assertIn("Error fetching weather data", response_artifact.value)

if __name__ == "__main__":
    unittest.main()
