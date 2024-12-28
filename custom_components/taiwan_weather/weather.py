"""Support for Taiwan Weather weather entity."""
from datetime import datetime, timedelta, timezone

from homeassistant.components.weather import (
    Forecast,
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfSpeed, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DEFAULT_NAME, DOMAIN, MANUFACTURER
from .coordinator import CWADataUpdateCoordinator

utc_plus_8 = timezone(timedelta(hours=8))

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Taiwan Weather weather entity based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([TaiwanWeather(coordinator, config_entry)], False)

class TaiwanWeather(CoordinatorEntity, WeatherEntity):
    """Implementation of Taiwan Weather weather entity."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = WeatherEntityFeature.FORECAST_HOURLY

    def __init__(
        self, coordinator: CWADataUpdateCoordinator, config_entry: ConfigEntry
    ) -> None:
        """Initialize the weather entity."""
        super().__init__(coordinator)
        self._config = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_weather"
        self._attr_name = config_entry.data.get("district")
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, f"{config_entry.entry_id}")},
            manufacturer=MANUFACTURER,
            name=DEFAULT_NAME,
        )

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        if not self.coordinator.data:
            return None

        try:
            now_time = datetime.now(tz=utc_plus_8).strftime("%Y-%m-%dT%H:%M:00+08:00")
            return self.coordinator.parser.get_condition(now_time)
        except (KeyError, IndexError):
            return None

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature."""
        if not self.coordinator.data:
            return None

        try:
            now_time = datetime.now(tz=utc_plus_8).strftime("%Y-%m-%dT%H:%M:00+08:00")
            return float(self.coordinator.parser.get_temperature(now_time))
        except (KeyError, IndexError, ValueError):
            return None

    @property
    def native_temperature_unit(self) -> str:
        """Return the unit of temperature."""
        return UnitOfTemperature.CELSIUS

    @property
    def humidity(self) -> float | None:
        """Return the humidity."""
        if not self.coordinator.data:
            return None

        try:
            now_time = datetime.now(tz=utc_plus_8).strftime("%Y-%m-%dT%H:%M:00+08:00")
            return float(self.coordinator.parser.get_humidity(now_time))
        except (KeyError, IndexError, ValueError):
            return None

    @property
    def native_apparent_temperature(self) -> float | None:
        """Return the apparent temperature."""
        if not self.coordinator.data:
            return None
        try:
            now_time = datetime.now(tz=utc_plus_8).strftime("%Y-%m-%dT%H:%M:00+08:00")
            return float(self.coordinator.parser.get_apparent_temperature(now_time))
        except (KeyError, IndexError, ValueError):
            return None

    @property
    def wind_bearing(self) -> str | None:
        """Return the wind bearing."""
        if not self.coordinator.data:
            return None
        try:
            now_time = datetime.now(tz=utc_plus_8).strftime("%Y-%m-%dT%H:%M:00+08:00")
            return self.coordinator.parser.get_wind_direction(now_time)
        except (KeyError, IndexError, ValueError):
            return None

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed."""
        if not self.coordinator.data:
            return None
        try:
            now_time = datetime.now(tz=utc_plus_8).strftime("%Y-%m-%dT%H:%M:00+08:00")
            return float(self.coordinator.parser.get_wind_speed(now_time))
        except (KeyError, IndexError, ValueError):
            return None

    @property
    def native_wind_speed_unit(self) -> str:
        """Return the wind speed unit."""
        return UnitOfSpeed.METERS_PER_SECOND

    @property
    def forecast(self) -> list[Forecast] | None:
        """Return the forecast."""
        if not self.coordinator.data:
            return None

        try:
            return self.coordinator.parser.parse_weather_data()

        except (KeyError, IndexError, ValueError):
            return None

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        """Return the hourly forecast in native units."""
        return self.forecast
