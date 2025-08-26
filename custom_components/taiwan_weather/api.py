"""CWA API Client for Home Assistant."""

import asyncio
from datetime import datetime, timedelta, timezone
import logging
from pathlib import Path
from types import TracebackType
from typing import Any

import requests

from .const import API_BASE_URL, API_LOCATION_MAPPING

_LOGGER = logging.getLogger(__name__)


class CWAAPIClient:
    """API Client for Central Weather Administration."""

    def __init__(self, api_key: str) -> None:
        """Initialize the API client."""
        assert isinstance(api_key, str), "API key is required"
        self._api_key = api_key
        self.base_url = API_BASE_URL
        self.api_response_data: dict[str, Any] | None = None
        self.last_update_time: datetime | None = None
        self._session = requests.Session()

        # 設置TWCA憑證路徑
        cert_path = Path(__file__).parent / "opendata-cwa-gov-tw.pem"
        if cert_path.exists():
            self._session.verify = str(cert_path)
        else:
            _LOGGER.warning("TWCA certificate not found at %s, using system default", cert_path)

    def __enter__(self) -> "CWAAPIClient":
        """Enter context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit context manager."""
        self.close()

    async def get_weather(
        self,
        city: str,
        district: str | None,
        forecast_duration: str = "three_days",
        forecast_type: str = "鄉鎮天氣預報",
    ) -> dict[str, Any] | None:
        """Get weather data for a specified location.

        Args:
            city (str): The name of the city to fetch weather data for.
            district (str | None): The name of the district within the city. If provided, this function will fetch weather data for the specific district. If not provided, it will fetch weather data for the entire city.
            forecast_duration (str): The duration of the weather forecast to retrieve. Valid options include: "three_days", "weekly". Defaults to "three_days".
            forecast_type (str): The type of weather forecast to retrieve. Defaults to "鄉鎮天氣預報".

        Returns:
            dict[str, Any] | None: A dictionary containing the weather data if the request is successful, or `None` if there is an error.

        Raises:
            ValueError: If the input parameters are invalid.

        """
        try:
            # 取得API endpoint
            try:
                if district is not None:
                    location_data = API_LOCATION_MAPPING[forecast_type]["location"][
                        city
                    ]
                    endpoint = f"{location_data[forecast_duration]}"

                    if district not in location_data["district"]:
                        raise ValueError(f"Invalid district {district} for city {city}")
                else:
                    endpoint = API_LOCATION_MAPPING[forecast_type]["location"]["臺灣"][
                        forecast_duration
                    ]

            except KeyError:
                _LOGGER.error("Invalid city: %s", city)
                return None

            url = f"{self.base_url}/{API_LOCATION_MAPPING[forecast_type]['id']}-{endpoint}"

            params = {
                "Authorization": self._api_key,
                "LocationName": district if district else city,
            }

            try:
                response = await asyncio.to_thread(
                    self._session.get, url, params=params
                )
                response.raise_for_status()

                data = response.json()
                if data.get("success") != "true":
                    _LOGGER.error("API request failed: %s", data.get("message"))
                    return None

                self.last_update_time = datetime.now(tz=timezone(timedelta(hours=8)))
                self.api_response_data = data
                return data

            except requests.RequestException as err:
                _LOGGER.error("Error accessing API: %s", err)
                return None

        except Exception as err:
            _LOGGER.error("Unexpected error: %s", err)
            return None

    def close(self) -> None:
        """Close the session."""
        self._session.close()


if __name__ == "__main__":
    # 快速測試CWAAPIClient
    # 如要測試請註解掉第12行的相對導入，並取消註解下面的測試程式碼
    # api_key = "your-api-key"  # 請替換為您的實際API金鑰

    # # API 相關資訊
    # API_BASE_URL  = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"

    # API_LOCATION_MAPPING = {
    #     "鄉鎮天氣預報": {
    #         "id": "F-D0047",
    #         "forecast_duration_type": {
    #             "three_days" : "三日預報",
    #             "weekly" : "一周預報"
    #         },
    #         "location": {
    #             "臺北市": {
    #                 "three_days": "061", # F-D0047-061
    #                 "weekly": "063", # F-D0047-063
    #                 "district": ["北投區", "士林區", "內湖區", "中山區", "大同區", "松山區", "南港區", "中正區", "萬華區", "信義區", "大安區", "文山區"]
    #             },
    #             "臺灣": {
    #                 "three_days": "089", # F-D0047-089
    #                 "weekly": "091", # F-D0047-091
    #                 "district": ["宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣", "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市", "基隆市", "新竹縣", "新竹市", "苗栗縣", "彰化縣", "南投縣", "雲林縣", "嘉義縣", "嘉義市", "屏東縣"]
    #             }
    #         }
    #     }
    # }

    # async def test_api():
    #     client = CWAAPIClient(api_key)
    #     city = "臺北市"
    #     district = "信義區"

    #     try:
    #         res = await client.get_weather(city=city, district=district)
    #         print("API Response:")
    #         print(res)
    #     except Exception as e:
    #         print(f"Error occurred: {e}")
    #     finally:
    #         client.close()

    # # 運行測試
    # asyncio.run(test_api())
    pass
