"""Config flow for Taiwan Weather."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .api import CWAAPIClient
from .const import API_LOCATION_MAPPING, DOMAIN
from .observation_api import CWARainfallClient

_LOGGER = logging.getLogger(__name__)

RAINFALL_STATION_NONE = "none"


class CWAWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Taiwan  Weather."""

    # 版本號
    VERSION = 1
    MINOR_VERSION = 0

    def __init__(self) -> None:
        """Initialize config flow."""
        self._entry_data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by the user."""
        errors = {}

        if user_input is not None:
            # 檢查API金鑰和位置是否有效
            api = CWAAPIClient(user_input[CONF_API_KEY])
            try:
                # 如果district 資料中含有"台" 自動替換為"臺"
                if "台" in user_input["district"]:
                    user_input["district"] = user_input["district"].replace("台", "臺")

                # 取得天氣預報資料
                data = await api.get_weather(
                    user_input["city"],
                    user_input["district"],
                    user_input.get("forecast_duration_type", "three_days"),
                )

                if data:
                    # 建立唯一ID，避免重複設定
                    unique_id = f"{user_input['city']}_{user_input['district']}"
                    await self.async_set_unique_id(unique_id)
                    self._abort_if_unique_id_configured()

                    self._entry_data = user_input
                    return await self.async_step_rainfall_station()

                errors["base"] = "cannot_connect"

            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            finally:
                api.close()

        # 取得所有縣市
        cities = list(API_LOCATION_MAPPING["鄉鎮天氣預報"]["location"].keys())
        districts = []

        schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): str,
                vol.Required("city"): vol.In(cities),
                vol.Required(
                    "district", default=districts[0] if districts else ""
                ): vol.In(districts) if districts else str,
                vol.Optional(CONF_NAME): str,
            }
        )

        return self.async_show_form(
            step_id="user",
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
