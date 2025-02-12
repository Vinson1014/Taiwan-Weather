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
        self.check_weather_response()
        return data

    def check_weather_response(self):
        """Check the weather response for errors."""
        if not self.api.api_response_data:
            raise CWAAPIClientError("無法獲取天氣資料")

    async def async_shutdown(self):
        """Shutdown the coordinator."""
        await super().async_shutdown()
        self.api.close()
