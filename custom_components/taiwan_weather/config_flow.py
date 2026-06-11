"""Config flow for Taiwan Weather."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_NAME
from homeassistant.data_entry_flow import AbortFlow, FlowResult

from .api import CWAAPIClient
from .const import API_LOCATION_MAPPING, DOMAIN
from .observation_api import CWARainfallClient

_LOGGER = logging.getLogger(__name__)

RAINFALL_STATION_NONE = "none"
LOCATION_CONFIG = API_LOCATION_MAPPING["鄉鎮天氣預報"]["location"]


class CWAWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Taiwan  Weather."""

    # 版本號
    VERSION = 1
    MINOR_VERSION = 0

    def __init__(self) -> None:
        """Initialize config flow."""
        self._entry_data: dict[str, Any] = {}

    def _get_districts(self, city: str) -> list[str]:
        """Return districts for a city."""
        return LOCATION_CONFIG.get(city, {}).get("district", [])

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by the user."""
        errors = {}

        if user_input is not None:
            self._entry_data = dict(user_input)
            return await self.async_step_district()

        # 取得所有縣市
        cities = list(LOCATION_CONFIG.keys())

        schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): str,
                vol.Required("city"): vol.In(cities),
                vol.Optional(CONF_NAME): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_district(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select a district based on the selected city."""
        errors = {}
        city = self._entry_data["city"]
        districts = self._get_districts(city)

        if user_input is not None:
            district = user_input["district"]

            # 檢查API金鑰和位置是否有效
            api = CWAAPIClient(self._entry_data[CONF_API_KEY])
            try:
                # 如果district 資料中含有"台" 自動替換為"臺"
                if "台" in district:
                    district = district.replace("台", "臺")

                if district not in districts:
                    errors["district"] = "invalid_district"
                else:
                    self._entry_data["district"] = district

                    # 取得天氣預報資料
                    data = await api.get_weather(
                        city,
                        district,
                        self._entry_data.get("forecast_duration_type", "three_days"),
                    )

                    if data:
                        # 建立唯一ID，避免重複設定
                        unique_id = f"{city}_{district}"
                        await self.async_set_unique_id(unique_id)
                        self._abort_if_unique_id_configured()

                        return await self.async_step_rainfall_station()

                    errors["base"] = "cannot_connect"

            except AbortFlow:
                raise
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            finally:
                api.close()

        if not districts:
            errors["base"] = "unknown"
            schema = vol.Schema({})
        else:
            schema = vol.Schema(
                {
                    vol.Required("district", default=districts[0]): vol.In(districts),
                }
            )

        return self.async_show_form(
            step_id="district",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_rainfall_station(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Optional step: select nearest rainfall observation station."""
        errors = {}
        if user_input is not None:
            station_id = user_input.get("rainfall_station_id")
            self._entry_data["rainfall_station_id"] = (
                None if station_id == RAINFALL_STATION_NONE else station_id
            )
            return self.async_create_entry(
                title=self._entry_data.get(CONF_NAME, self._entry_data["district"]),
                data=self._entry_data,
            )

        # 取得最近的雨量站清單
        client = CWARainfallClient(self._entry_data[CONF_API_KEY])
        try:
            all_stations = await client.get_all_stations()
        finally:
            client.close()

        if all_stations:
            home_lat = self.hass.config.latitude
            home_lon = self.hass.config.longitude
            nearest = CWARainfallClient.find_nearest_stations(
                all_stations, home_lat, home_lon, limit=5
            )
        else:
            errors["base"] = "cannot_connect"
            nearest = []

        options = {RAINFALL_STATION_NONE: "不啟用降雨觀測"}
        for s in nearest:
            label = f"{s['name']} ({s['county']}{s['town']}, {s['distance_km']} km)"
            options[s["station_id"]] = label

        schema = vol.Schema(
            {
                vol.Required("rainfall_station_id", default=RAINFALL_STATION_NONE): vol.In(options),
            }
        )

        return self.async_show_form(
            step_id="rainfall_station",
            data_schema=schema,
            errors=errors,
        )
