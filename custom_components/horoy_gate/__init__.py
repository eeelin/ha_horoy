"""Home Assistant integration for Horoy gate control."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_BASE_URL,
    DEFAULT_BASE_URL,
    DOMAIN,
    SERVICE_LIST_DOORS,
    SERVICE_OPEN_DOOR,
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_BASE_URL, default=DEFAULT_BASE_URL): cv.url,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

OPEN_DOOR_SCHEMA = vol.Schema(
    {
        vol.Optional("name"): cv.string,
        vol.Optional("code"): cv.string,
        vol.Optional("ekey"): cv.string,
    }
)


def _normalize_base_url(url: str) -> str:
    return url.rstrip("/")


async def _fetch_doors(base_url: str) -> list[dict[str, Any]]:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base_url}/doors", timeout=10) as resp:
            resp.raise_for_status()
            data = await resp.json()
            if not isinstance(data, list):
                raise ValueError("Invalid /doors response: expected list")
            return data


async def _open_door(base_url: str, door: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "door": {
            "name": door["name"],
            "code": str(door["code"]),
            "ekey": door["ekey"],
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{base_url}/doors/open", json=payload, timeout=10) as resp:
            resp.raise_for_status()
            return await resp.json()


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up Horoy Gate from YAML config."""
    conf = config.get(DOMAIN, {})
    base_url = _normalize_base_url(conf.get(CONF_BASE_URL, DEFAULT_BASE_URL))
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][CONF_BASE_URL] = base_url

    async def handle_list_doors(call: ServiceCall) -> ServiceResponse:
        """List available doors from gateway API."""
        try:
            doors = await _fetch_doors(base_url)
            return {"success": True, "doors": doors}
        except Exception as err:  # noqa: BLE001
            _LOGGER.exception("Failed to list doors")
            return {"success": False, "error": str(err)}

    async def handle_open_door(call: ServiceCall) -> ServiceResponse:
        """Open a door by either full payload or by name lookup."""
        name = call.data.get("name")
        code = call.data.get("code")
        ekey = call.data.get("ekey")

        try:
            if name and code and ekey:
                door = {"name": name, "code": code, "ekey": ekey}
            else:
                if not name:
                    return {
                        "success": False,
                        "error": "Provide name, or provide name+code+ekey.",
                    }
                doors = await _fetch_doors(base_url)
                match = next((d for d in doors if d.get("name") == name), None)
                if not match:
                    return {"success": False, "error": f"Door not found: {name}"}
                door = match

            result = await _open_door(base_url, door)
            return {"success": True, "result": result, "door": door.get("name")}
        except Exception as err:  # noqa: BLE001
            _LOGGER.exception("Failed to open door")
            return {"success": False, "error": str(err)}

    hass.services.async_register(
        DOMAIN,
        SERVICE_LIST_DOORS,
        handle_list_doors,
        supports_response="only",
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_OPEN_DOOR,
        handle_open_door,
        schema=OPEN_DOOR_SCHEMA,
        supports_response="only",
    )

    _LOGGER.info("Horoy Gate initialized with base_url=%s", base_url)
    return True
