"""CWA Rainfall Observation API Client (O-A0002-001)."""

import asyncio
import logging
import math
from pathlib import Path
from typing import Any

import requests

from .const import REQUEST_TIMEOUT

_LOGGER = logging.getLogger(__name__)

RAINFALL_API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001"


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two WGS84 coordinates."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _safe_float(value: str) -> float | None:
    """Convert string to float; return None for missing-data sentinels (< 0)."""
    try:
        f = float(value)
        return None if f < 0 else f
    except (ValueError, TypeError):
        return None


class CWARainfallClient:
    """Client for CWA rainfall observation API."""

    def __init__(self, api_key: str) -> None:
        """Initialize the client with SSL certificate matching the forecast API."""
        self._api_key = api_key
        self._session = requests.Session()
        cert_path = Path(__file__).parent / "opendata-cwa-gov-tw.pem"
        if cert_path.exists():
            self._session.verify = str(cert_path)
        else:
            _LOGGER.warning("TWCA certificate not found at %s", cert_path)

    async def get_all_stations(self) -> list[dict[str, Any]]:
        """Fetch metadata for all rainfall stations."""
        try:
            response = await asyncio.to_thread(
                self._session.get,
                RAINFALL_API_URL,
                params={"Authorization": self._api_key},
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            if data.get("success") != "true":
                _LOGGER.error("Rainfall station list request failed")
                return []
            return [
                self._parse_station_info(s)
                for s in data["records"]["Station"]
            ]
        except Exception as err:
            _LOGGER.error("Failed to fetch rainfall stations: %s", err)
            return []

    async def get_station_rainfall(self, station_id: str) -> dict[str, Any] | None:
        """Fetch current rainfall observations for a specific station."""
        try:
            response = await asyncio.to_thread(
                self._session.get,
                RAINFALL_API_URL,
                params={"Authorization": self._api_key, "StationId": station_id},
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            if data.get("success") != "true":
                return None
            stations = data["records"]["Station"]
            if not stations:
                return None
            return self._parse_rainfall(stations[0])
        except Exception as err:
            _LOGGER.error("Failed to fetch rainfall for station %s: %s", station_id, err)
            return None

    @staticmethod
    def find_nearest_stations(
        stations: list[dict[str, Any]],
        lat: float,
        lon: float,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Return up to `limit` stations sorted by distance from (lat, lon)."""
        for s in stations:
            s["distance_km"] = round(_haversine_km(lat, lon, s["lat"], s["lon"]), 1)
        return sorted(stations, key=lambda s: s["distance_km"])[:limit]

    @staticmethod
    def _parse_station_info(raw: dict[str, Any]) -> dict[str, Any]:
        coords = raw["GeoInfo"]["Coordinates"]
        wgs84 = next((c for c in coords if c["CoordinateName"] == "WGS84"), coords[-1])
        return {
            "station_id": raw["StationId"],
            "name": raw["StationName"],
            "lat": float(wgs84["StationLatitude"]),
            "lon": float(wgs84["StationLongitude"]),
            "county": raw["GeoInfo"]["CountyName"],
            "town": raw["GeoInfo"]["TownName"],
        }

    @staticmethod
    def _parse_rainfall(raw: dict[str, Any]) -> dict[str, Any]:
        r = raw["RainfallElement"]
        past_6hr = r.get("Past6hr") or r.get("Past6Hr") or {}
        return {
            "obs_time": raw["ObsTime"]["DateTime"],
            "now": _safe_float(r["Now"]["Precipitation"]),
            "past_10min": _safe_float(r["Past10Min"]["Precipitation"]),
            "past_1hr": _safe_float(r["Past1hr"]["Precipitation"]),
            "past_3hr": _safe_float(r["Past3hr"]["Precipitation"]),
            "past_6hr": _safe_float(past_6hr.get("Precipitation")),
            "past_12hr": _safe_float(r["Past12hr"]["Precipitation"]),
            "past_24hr": _safe_float(r["Past24hr"]["Precipitation"]),
            "past_2days": _safe_float(r["Past2days"]["Precipitation"]),
            "past_3days": _safe_float(r["Past3days"]["Precipitation"]),
        }

    def close(self) -> None:
        """Close the HTTP session."""
        self._session.close()
