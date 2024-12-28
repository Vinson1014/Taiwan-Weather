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

_LOGGER = logging.getLogger(__name__)

class CWAWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Taiwan  Weather."""

    # 版本號
    VERSION = 1
    MINOR_VERSION = 0

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
                data = await api.async_get_weather(
                    user_input["city"],
                    user_input["district"],
                    user_input.get("forecast_duration_type", "three_days")
                )
                await api.async_close()

                if data:
                    # 建立唯一ID，避免重複設定
                    unique_id = f"{user_input['city']}_{user_input['district']}"
                    await self.async_set_unique_id(unique_id)
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=user_input.get(CONF_NAME, user_input['district']),
                        data=user_input
                    )

                errors["base"] = "cannot_connect"

            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            finally:
                await api.async_close()

        # 取得所有縣市
        cities = list(API_LOCATION_MAPPING["鄉鎮天氣預報"]["location"].keys())
        # 如果已選擇縣市，取得其鄉鎮區列表
        districts = []
        # 因為weekly 資料格式與 three_days 稍微不一樣 所以暫時先不開放選擇
        # forcast_duration_type = list(API_LOCATION_MAPPING["鄉鎮天氣預報"]["forecast_duration_type"].keys())

        # 建立設定表單
        schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): str,
                vol.Required("city"): vol.In(cities),
                vol.Required("district", default=districts[0] if districts else ""):
                    vol.In(districts) if districts else str,
                vol.Optional(CONF_NAME): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
