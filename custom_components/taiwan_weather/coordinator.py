"""Data update coordinator for Taiwan Weather."""

from datetime import datetime, timedelta, timezone
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import CWAAPIClient
from .const import DOMAIN, UPDATE_INTERVAL
from .cwa_data_parser import CWADataParser
from .observation_api import CWARainfallClient

_LOGGER = logging.getLogger(__name__)


class CWAAPIClientError(Exception):
    """Exception class for CWA API errors."""


class CWADataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching CWA Weather data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.api = CWAAPIClient(entry.data[CONF_API_KEY])
        self.parser = CWADataParser(self.api)
        self.city = entry.data["city"]
        self.district = (
            entry.data["district"] if entry.data["district"] else None
        )  # 如果district為空，則不傳遞district參數

        # 雨量站（選填）
        rainfall_station_id = entry.data.get("rainfall_station_id")
        if rainfall_station_id:
            self.rainfall_client = CWARainfallClient(entry.data[CONF_API_KEY])
            self.rainfall_station_id = rainfall_station_id
        else:
            self.rainfall_client = None
            self.rainfall_station_id = None
        self.rainfall_data: dict | None = None

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=UPDATE_INTERVAL),  # 每60分鐘更新一次
        )

    async def _async_setup(self):
        """Set up the coordinator."""
        try:
            await self.setup_weather_data()
        except CWAAPIClientError as err:
            _LOGGER.error("Failed to set up weather data: %s", err)
            return False

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            if self.should_poll() or self.api.api_response_data is None:
                data = await self.setup_weather_data()  # 更新天氣資料
            else:
                data = self.api.api_response_data  # 使用上次的資料，避免頻繁請求API
                _LOGGER.debug(
                    f"Time: {datetime.now(tz=timezone(timedelta(hours=8))).strftime('%Y-%m-%dT%H:%M:00+08:00')}, Using cached weather data"  # noqa: G004
                )

            if self.rainfall_client:
                await self.setup_rainfall_data()

            return data  # noqa: TRY300

        except Exception as err:
            _LOGGER.error("Error updating weather data: %s", err)
            raise

    def should_poll(self) -> bool:
        """Return True if polling should be enabled."""
        now = datetime.now(tz=timezone(timedelta(hours=8)))
        return now.hour in [0, 6, 12, 18]

    async def setup_weather_data(self) -> dict[str, Any] | None:
        """Set up weather data."""
        self.parser.clear_weather_element()
        data = await self.api.get_weather(self.city, self.district)
        if data is None:
            self.check_weather_response()
            _LOGGER.warning("Using cached weather data because the latest fetch failed")
            return self.api.api_response_data

        return data

    async def setup_rainfall_data(self) -> dict[str, Any] | None:
        """Set up rainfall observation data."""
        if self.rainfall_client:
            self.rainfall_data = await self.rainfall_client.get_station_rainfall(
                self.rainfall_station_id
            )

        return self.rainfall_data

    def check_weather_response(self):
        """Check the weather response for errors."""
        if not self.api.api_response_data:
            raise CWAAPIClientError("無法獲取天氣資料")

    async def async_shutdown(self):
        """Shutdown the coordinator."""
        await super().async_shutdown()
        self.api.close()
        if self.rainfall_client:
            self.rainfall_client.close()
