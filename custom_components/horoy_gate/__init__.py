"""Home Assistant integration for Horoy gate control."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, discovery

from .const import CONF_BASE_URL, DEFAULT_BASE_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BUTTON]

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


def _normalize_base_url(url: str) -> str:
    return url.rstrip("/")


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up Horoy Gate from YAML config."""
    conf = config.get(DOMAIN, {})
    base_url = _normalize_base_url(conf.get(CONF_BASE_URL, DEFAULT_BASE_URL))

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][CONF_BASE_URL] = base_url

    # YAML setup path: load button platform and build entities from door list.
    await discovery.async_load_platform(hass, Platform.BUTTON, DOMAIN, {}, config)

    _LOGGER.info("Horoy Gate initialized with base_url=%s", base_url)
    return True
