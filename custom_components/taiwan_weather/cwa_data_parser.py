"""Parse CWA weather data."""
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.weather import ATTR_CONDITION_EXCEPTIONAL

from .api import CWAAPIClient
from .const import CONDITION_MAP


class CWADataParser:
    """Class to parse CWA API response data."""

    def __init__(self, api_client: CWAAPIClient) -> None:
        """Initialize the parser with an API key."""
        self.api_client = api_client
        self.weather_element: list[dict[str, Any]] | None = None

    def parse_weather_data(self) -> list[dict[str, Any]]:
        """Parse the weather data from the API response."""
        if not self.weather_element:
            self._get_weather_element()

        forecast = []
        base_times = self._get_base_times()

        for time in base_times:
            weather = {
                "datetime": time,
                "condition": self.get_condition(time),
                "humidity": self.get_humidity(time),
                "native_temperature": self.get_temperature(time),
                "native_apparent_temperature": self.get_apparent_temperature(time),
                "wind_bearing": self.get_wind_direction(time),
                "native_wind_speed": self.get_wind_speed(time),
                "precipitation_probability": self.get_precipitation_probability(time),
            }
            forecast.append(weather)
        return forecast

    def clear_weather_element(self):
        """Clear the weather elements."""
        self.weather_element = None

    def _get_weather_element(self):
        """Get weather elements from the API response."""
        if self.api_client.api_response_data:
            self.weather_element = self._align_time(self.api_client.api_response_data)

    def _get_base_times(self):
        """Get base times for alignment."""
        temp = self._get_weather_data_by_name("溫度")
        return [time["DataTime"] for time in temp] if temp else []

    def _get_weather_data_by_name(self, element_name: str) -> list[dict[str, Any]] | None:
        """Get weather data by element name."""
        if not self.weather_element:
            self._get_weather_element()

        for element in self.weather_element:
            if element["ElementName"] == element_name:
                return element["Time"]
        return None

    def get_condition(self, time: str) -> str:
        """Get weather condition based on time."""
        weather_code = self._get_weather_data_by_name("天氣現象")
        return CONDITION_MAP.get(self._get_value(weather_code, time)[0]["WeatherCode"], ATTR_CONDITION_EXCEPTIONAL)

    def get_temperature(self, time: str) -> float:
        """Get temperature for a given time."""
        temp_data = self._get_weather_data_by_name("溫度")
        return float(self._get_value(temp_data, time)[0]["Temperature"])

    def get_apparent_temperature(self, time: str) -> float:
        """Get apparent temperature for a given time."""
        app_temp_data = self._get_weather_data_by_name("體感溫度")
        return float(self._get_value(app_temp_data, time)[0]["ApparentTemperature"])

    def get_humidity(self, time: str) -> int:
        """Get humidity for a given time."""
        humid_data = self._get_weather_data_by_name("相對濕度")
        return int(self._get_value(humid_data, time)[0]["RelativeHumidity"])

    def get_wind_direction(self, time: str) -> str:
        """Get wind direction for a given time."""
        wind_dir_data = self._get_weather_data_by_name("風向")
        return self._get_value(wind_dir_data, time)[0]["WindDirection"]

    def get_wind_speed(self, time: str) -> float:
        """Get wind speed for a given time."""
        wind_speed_data = self._get_weather_data_by_name("風速")
        return float(self._get_value(wind_speed_data, time)[0]["WindSpeed"])

    def get_precipitation_probability(self, time: str) -> int:
        """Get precipitation probability for a given time."""
        precip_data = self._get_weather_data_by_name("3小時降雨機率")
        return int(self._get_value(precip_data, time)[0]["ProbabilityOfPrecipitation"])

    def get_dew_point(self, time: str) -> float:
        """Get dew point for a given time."""
        dew_point_data = self._get_weather_data_by_name("露點溫度")
        return float(self._get_value(dew_point_data, time)[0]["DewPoint"])

    def get_comfort_index(self, time: str) -> float:
        """Get comfort index for a given time."""
        comfort_index_data = self._get_weather_data_by_name("舒適度指數")
        return float(self._get_value(comfort_index_data, time)[0]["ComfortIndex"])

    def get_comfort_index_description(self, time: str) -> str:
        """Get comfort index description for a given time."""
        comfort_index_data = self._get_weather_data_by_name("舒適度指數")
        return self._get_value(comfort_index_data, time)[0]["ComfortIndexDescription"]

    def get_weather_description(self, time: str) -> str:
        """Get weather description for a given time."""
        weather_description_data = self._get_weather_data_by_name("天氣預報綜合描述")
        return self._get_value(weather_description_data, time)[0]["WeatherDescription"]


    def _get_value(self, data: list[dict[str, Any]], time: str) -> list[dict[str, Any]]:
        """Get the value for a given time."""
        if data is None:
            return []

        # Convert input time to datetime object
        target_time = datetime.fromisoformat(time)

        # Initialize variables to track the closest match
        closest_data = None
        min_diff = timedelta.max

        for item in data:
            current_time_str = item["DataTime"]
            current_time = datetime.fromisoformat(current_time_str)
            diff = abs(target_time - current_time)

            if diff < min_diff:
                min_diff = diff
                closest_data = item

        return closest_data["ElementValue"] if closest_data else []

    def _align_time(self, api_response: dict[str, Any]) -> list[dict[str, Any]]:
        """重新對齊所有資料的時間以利後續使用."""
        # 找出資料中的weather elements
        weather_elements = api_response["records"]["Locations"][0]["Location"][0].get('WeatherElement', [])
        if not weather_elements:
            raise ValueError("找不到天氣元素")

        # 1. 找出溫度資料的時間點作為基準
        base_times = []
        for element in weather_elements:
            if element["ElementName"] == "溫度":
                base_times = [
                    data["DataTime"]
                    for data in element["Time"]
                ]
                break

        if not base_times:
            raise ValueError("找不到溫度資料作為時間基準")

        # 2. 建立新的資料結構，避免修改原始資料
        aligned_elements = []
        for element in weather_elements:
            aligned_element = {
                "ElementName": element["ElementName"],
                "Time": []
            }

            # 建立時間對照表，方便查找
            time_value_map = {}
            for time_data in element["Time"]:
                # 處理不同的時間格式
                time_key = (time_data.get("DataTime") or
                        time_data.get("StartTime"))
                time_value_map[time_key] = time_data["ElementValue"]

                # 如果是區間資料（有StartTime/EndTime），填充區間內的所有時間點 並將格式改為Datatime
                if "StartTime" in time_data and "EndTime" in time_data:
                    start = datetime.fromisoformat(time_data["StartTime"])
                    end = datetime.fromisoformat(time_data["EndTime"])
                    current = start
                    while current <= end:
                        time_str = current.isoformat()
                        time_value_map[time_str] = time_data["ElementValue"]
                        # 根據資料的時間間隔調整
                        current += timedelta(hours = 1)

            # 3. 對齊到基準時間點
            for base_time in base_times:
                value = time_value_map.get(base_time)
                if value is None:
                    # 如果沒有對應的值，使用最近的有效值
                    nearest_time = min(time_value_map.keys(),
                                    key=lambda x: abs(
                                        datetime.fromisoformat(x) -
                                        datetime.fromisoformat(base_time)
                                    ))
                    value = time_value_map[nearest_time]

                aligned_element["Time"].append({
                    "DataTime": base_time,
                    "ElementValue": value
                })

            aligned_elements.append(aligned_element)

        return aligned_elements
