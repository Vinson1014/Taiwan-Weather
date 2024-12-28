"""CWA API Client for Home Assistant."""

from datetime import datetime, timedelta, timezone
import logging
from types import TracebackType
from typing import Any

import httpx

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
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client instance (lazy initialization)."""
        if self._client is None:
            self._client = httpx.AsyncClient()
        return self._client

    async def __aenter__(self) -> "CWAAPIClient":
        """Async enter context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Async exit context manager."""
        await self.async_close()


    async def async_get_weather(self, city: str, district: str | None, forecast_duration: str = "three_days", forecast_type: str = "鄉鎮天氣預報") -> dict[str, Any] | None:
        """Get weather data for a specified location.

        Args:
            city (str): The name of the city.
            district (str | None): The name of the district, if applicable. If not provided, it will default to None.
            forecast_duration (str): The duration of the forecast ("three_days", "weekly").
            forecast_type (str): The type of weather forecast. Defaults to "鄉鎮天氣預報".

        Returns:
            dict[str, Any]: A dictionary containing the weather data if the request is successful and data is found.
            None: If the request fails or no data is found.

        Raises:
            ValueError: If the forecast_type is invalid or the district is not found.

        """

        # 取得API endpoint
        try:
            if district is not None:
                location_data = API_LOCATION_MAPPING[forecast_type]["location"][city]
                endpoint = f"{location_data[forecast_duration]}"

                if district not in location_data["district"]:
                    raise ValueError(f"Invalid district {district} for city {city}")
            else:
                endpoint = API_LOCATION_MAPPING[forecast_type]["location"]["臺灣"][forecast_duration]


        except KeyError:
            _LOGGER.error("Invalid city: %s", city)
            return None

        url = f"{self.base_url}/{API_LOCATION_MAPPING[forecast_type]["id"]}-{endpoint}"

        params = {
            "Authorization": self._api_key,
            "LocationName": district if district else city
        }

        try:
            response = await self.client.get(url, params=params)

            if response.status_code != 200:
                _LOGGER.error("API request failed with status: %s", response.status)
                return None

            data = response.json()
            if data.get("success") != "true":
                _LOGGER.error("API request failed: %s", data.get("message"))
                return None
            self.last_update_time = datetime.now(tz=timezone(timedelta(hours=8)))
            self.api_response_data = data  # Store the API response data for later use.

            return data  # noqa: TRY300

        except httpx.RequestError as err:
            _LOGGER.error("Error accessing API: %s", err)
            return None

    async def async_close(self) -> None:
        """Close the API session."""
        if self.client:
            await self.client.aclose()  # Close the client session.



if __name__ == "__main__":
    pass
