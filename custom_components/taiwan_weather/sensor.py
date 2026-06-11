"""Support for Taiwan Weather sensors."""
from datetime import datetime, timedelta, timezone

from homeassistant.components.datetime import DateTimeEntity
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfLength, UnitOfSpeed, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN, MANUFACTURER
from .coordinator import CWADataUpdateCoordinator

SENSOR_TYPES = {
    "temperature": {
        "name": "溫度",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "api_name": "Temperature"
    },
    "dew_point": {
        "name": "露點溫度",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:water",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "api_name": "DewPoint"
    },
    "apparent_temperature": {
        "name": "體感溫度",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "api_name": "ApparentTemperature"
    },
    "comfort_index": {
        "name": "舒適度指數",
        "unit": None,
        "icon": "mdi:baby-face-outline",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "api_name": "ComfortIndex"
    },
    # "comfort_description": {
    #     "name": "Comfort Description",
    #     "unit": None,
    #     "icon": "mdi:text",
    #     "device_class": None,
    #     "api_name": "ComfortIndexDescription"
    # },
    "relative_humidity": {
        "name": "相對濕度",
        "unit": PERCENTAGE,
        "icon": "mdi:water-percent",
        "device_class": SensorDeviceClass.HUMIDITY,
        "state_class": SensorStateClass.MEASUREMENT,
        "api_name": "RelativeHumidity"
    },
    "wind_direction": {
        "name": "風向",
        "unit": None,
        "icon": "mdi:compass",
        "device_class": SensorDeviceClass.ENUM,
        "state_class": SensorStateClass.MEASUREMENT,
        "api_name": "WindDirection"
    },
    "wind_speed": {
        "name": "風速",
        "unit": UnitOfSpeed.METERS_PER_SECOND,
        "icon": "mdi:weather-windy",
        "device_class": SensorDeviceClass.WIND_SPEED,
        "state_class": SensorStateClass.MEASUREMENT,
        "api_name": "WindSpeed"
    },
    # "beaufort_scale": {
    #     "name": "Beaufort Scale",
    #     "unit": None,
    #     "icon": "mdi:weather-windy",
    #     "device_class": None,
    #     "api_name": "BeaufortScale"
    # },
    "precipitation_probability": {
        "name": "降雨機率",
        "unit": PERCENTAGE,
        "icon": "mdi:water",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "api_name": "ProbabilityOfPrecipitation"
    },
    # "weather_description": {
    #     "name": "Weather Description",
    #     "unit": None,
    #     "icon": "mdi:text-box",
    #     "device_class": None,
    #     "api_name": "WeatherDescription"
    # }
    "api_last_update_time": {
        "name": "API 最後更新時間",
        "unit": None,
        "icon": "mdi:clock-time-eight",
        "device_class": SensorDeviceClass.TIMESTAMP,
        "state_class": None,
        "api_name": "last_update_time"
    }
}

RAINFALL_SENSOR_TYPES: dict[str, dict] = {
    "rainfall_now": {
        "name": "本日累積雨量",
        "period_key": "now",
        "unit": UnitOfLength.MILLIMETERS,
        "device_class": SensorDeviceClass.PRECIPITATION,
        "state_class": SensorStateClass.TOTAL,
        "icon": "mdi:weather-rainy",
    },
    "rainfall_10min": {
        "name": "過去 10 分鐘累積雨量",
        "period_key": "past_10min",
        "unit": UnitOfLength.MILLIMETERS,
        "device_class": SensorDeviceClass.PRECIPITATION,
        "state_class": None,
        "icon": "mdi:weather-rainy",
    },
    "rainfall_1hr": {
        "name": "過去 1 小時累積雨量",
        "period_key": "past_1hr",
        "unit": UnitOfLength.MILLIMETERS,
        "device_class": SensorDeviceClass.PRECIPITATION,
        "state_class": None,
        "icon": "mdi:weather-rainy",
    },
    "rainfall_3hr": {
        "name": "過去 3 小時累積雨量",
        "period_key": "past_3hr",
        "unit": UnitOfLength.MILLIMETERS,
        "device_class": SensorDeviceClass.PRECIPITATION,
        "state_class": None,
        "icon": "mdi:weather-rainy",
    },
    "rainfall_6hr": {
        "name": "過去 6 小時累積雨量",
        "period_key": "past_6hr",
        "unit": UnitOfLength.MILLIMETERS,
        "device_class": SensorDeviceClass.PRECIPITATION,
        "state_class": None,
        "icon": "mdi:weather-rainy",
    },
    "rainfall_12hr": {
        "name": "過去 12 小時累積雨量",
        "period_key": "past_12hr",
        "unit": UnitOfLength.MILLIMETERS,
        "device_class": SensorDeviceClass.PRECIPITATION,
        "state_class": None,
        "icon": "mdi:weather-rainy",
    },
    "rainfall_24hr": {
        "name": "過去 24 小時累積雨量",
        "period_key": "past_24hr",
        "unit": UnitOfLength.MILLIMETERS,
        "device_class": SensorDeviceClass.PRECIPITATION,
        "state_class": None,
        "icon": "mdi:weather-rainy",
    },
    "rainfall_2days": {
        "name": "前 2 日累積雨量",
        "period_key": "past_2days",
        "unit": UnitOfLength.MILLIMETERS,
        "device_class": SensorDeviceClass.PRECIPITATION,
        "state_class": None,
        "icon": "mdi:weather-rainy",
    },
    "rainfall_3days": {
        "name": "前 3 日累積雨量",
        "period_key": "past_3days",
        "unit": UnitOfLength.MILLIMETERS,
        "device_class": SensorDeviceClass.PRECIPITATION,
        "state_class": None,
        "icon": "mdi:weather-rainy",
    },
    "rainfall_obs_time": {
        "name": "雨量觀測時間",
        "period_key": "obs_time",
        "unit": None,
        "device_class": SensorDeviceClass.TIMESTAMP,
        "state_class": None,
        "icon": "mdi:clock-time-eight",
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Taiwan Weather sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities: list = [
        TaiwanWeatherSensor(coordinator, config_entry, sensor_type)
        for sensor_type in SENSOR_TYPES
    ]

    if coordinator.rainfall_client:
        entities += [
            TaiwanRainfallSensor(coordinator, config_entry, sensor_type)
            for sensor_type in RAINFALL_SENSOR_TYPES
        ]

    async_add_entities(entities)

class TaiwanWeatherSensor(CoordinatorEntity, SensorEntity, TextEntity, DateTimeEntity):
    """Implementation of a Taiwan Weather sensor."""

    def __init__(
        self,
        coordinator: CWADataUpdateCoordinator,
        config_entry: ConfigEntry,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config = config_entry
        self._sensor_type = sensor_type
        self._attr_unique_id = f"{config_entry.entry_id}_{sensor_type}"
        self._attr_name = f"{config_entry.data.get("district")} {SENSOR_TYPES[sensor_type]['name']}"
        self._attr_native_unit_of_measurement = SENSOR_TYPES[sensor_type]["unit"]
        self._attr_device_class = SENSOR_TYPES[sensor_type]["device_class"]
        self._attr_state_class = getattr(SENSOR_TYPES[sensor_type], "state_class", None)
        self._attr_icon = SENSOR_TYPES[sensor_type]["icon"]
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, f"{config_entry.entry_id}")},
            manufacturer=MANUFACTURER,
            name=DEFAULT_NAME,
        )

    @property
    def native_value(self) -> float | str | datetime | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        try:
            utc_plus_8 = timezone(timedelta(hours=8))
            now_time = datetime.now(tz=utc_plus_8).strftime("%Y-%m-%dT%H:%M:00+08:00")  # 台北時間
            # temperature
            if self._sensor_type == "temperature":
                return self.coordinator.parser.get_temperature(now_time)
            # humidity
            if self._sensor_type == "relative_humidity":
                return self.coordinator.parser.get_humidity(now_time)
            # apparent temperature
            if self._sensor_type == "apparent_temperature":
                return self.coordinator.parser.get_apparent_temperature(now_time)
            # wind speed
            if self._sensor_type == "wind_speed":
                return self.coordinator.parser.get_wind_speed(now_time)
            # wind direction
            if self._sensor_type == "wind_direction":
                return self.coordinator.parser.get_wind_direction(now_time)
            # precipitation probability
            if self._sensor_type == "precipitation_probability":
                return self.coordinator.parser.get_precipitation_probability(now_time)
            # dew point
            if self._sensor_type == "dew_point":
                return self.coordinator.parser.get_dew_point(now_time)
            # comfort index
            if self._sensor_type == "comfort_index":
                return self.coordinator.parser.get_comfort_index(now_time)
            # comfort index description
            if self._sensor_type == "comfort_index_description":
                return self.coordinator.parser.get_comfort_index_description(now_time)
            # weather_description
            if self._sensor_type == "weather_description":
                return self.coordinator.parser.get_weather_description(now_time)
            # api_last_update_time
            if self._sensor_type == "api_last_update_time":
                return self.coordinator.api.last_update_time

        except (KeyError, IndexError, ValueError):
            return None

        return None


class TaiwanRainfallSensor(CoordinatorEntity, SensorEntity):
    """Rainfall observation sensor sourced from the nearest CWA rainfall station."""

    def __init__(
        self,
        coordinator: CWADataUpdateCoordinator,
        config_entry: ConfigEntry,
        sensor_type: str,
    ) -> None:
        """Initialize the rainfall sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        sensor_config = RAINFALL_SENSOR_TYPES[sensor_type]
        self._attr_unique_id = f"{config_entry.entry_id}_{sensor_type}"
        self._attr_name = (
            f"{config_entry.data.get('district')} "
            f"{sensor_config['name']}"
        )
        self._attr_native_unit_of_measurement = sensor_config["unit"]
        self._attr_device_class = sensor_config["device_class"]
        self._attr_state_class = sensor_config["state_class"]
        self._attr_icon = sensor_config["icon"]
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, f"{config_entry.entry_id}")},
            manufacturer=MANUFACTURER,
            name=DEFAULT_NAME,
        )

    @property
    def native_value(self) -> float | datetime | None:
        """Return rainfall amount for this sensor's time period."""
        if not self.coordinator.rainfall_data:
            return None
        period_key = RAINFALL_SENSOR_TYPES[self._sensor_type]["period_key"]
        value = self.coordinator.rainfall_data.get(period_key)
        if period_key == "obs_time" and value:
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return None
        return value
