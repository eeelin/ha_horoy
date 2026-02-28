"""Horoy gate API client helpers."""
from __future__ import annotations

from typing import Any

import aiohttp


async def fetch_doors(base_url: str) -> list[dict[str, Any]]:
    """Fetch door list from Horoy API."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base_url}/doors", timeout=10) as resp:
            resp.raise_for_status()
            data = await resp.json()
            if not isinstance(data, list):
                raise ValueError("Invalid /doors response: expected list")
            return data


async def open_door(base_url: str, door: dict[str, Any]) -> dict[str, Any]:
    """Open a specific door via Horoy API."""
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
