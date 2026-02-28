"""Button entities for Horoy doors."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_BASE_URL, DOMAIN
from .horoy_api import fetch_doors, open_door

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: dict[str, Any],
    async_add_entities: AddEntitiesCallback,
    discovery_info: dict[str, Any] | None = None,
) -> None:
    """Set up Horoy door buttons from YAML/discovery."""
    base_url: str = hass.data[DOMAIN][CONF_BASE_URL]

    try:
        doors = await fetch_doors(base_url)
    except Exception as err:  # noqa: BLE001
        _LOGGER.error("Failed to fetch Horoy doors during setup: %s", err)
        return

    entities = [HoroyDoorButton(base_url, door) for door in doors if _valid_door(door)]
    async_add_entities(entities)


def _valid_door(door: dict[str, Any]) -> bool:
    return bool(door.get("name") and door.get("code") and door.get("ekey"))


class HoroyDoorButton(ButtonEntity):
    """Represents one physical door as a button entity."""

    _attr_has_entity_name = True

    def __init__(self, base_url: str, door: dict[str, Any]) -> None:
        self._base_url = base_url
        self._door = door
        code = str(door["code"])
        name = str(door["name"])
        self._attr_name = name
        self._attr_unique_id = f"horoy_gate_{code}"
        self._attr_icon = "mdi:door-open"

    @property
    def device_info(self) -> dict[str, Any]:
        """Expose each door as a dedicated device."""
        code = str(self._door["code"])
        return {
            "identifiers": {(DOMAIN, code)},
            "name": str(self._door["name"]),
            "manufacturer": "Horoy",
            "model": "Community Gate",
        }

    async def async_press(self) -> None:
        """Open door when button is pressed."""
        result = await open_door(self._base_url, self._door)
        if result.get("succeed") is not True:
            raise RuntimeError(f"Failed to open door: {result}")
