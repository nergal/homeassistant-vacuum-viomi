"""Xiaomi Viomi integration."""
import asyncio

import voluptuous as vol
from homeassistant.components.vacuum import PLATFORM_SCHEMA
from homeassistant.components.xiaomi_miio import CONF_MODEL
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN, DEVICE_DEFAULT_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from miio.integrations.vacuum.viomi.viomivacuum import SUPPORTED_MODELS

from .const import DOMAIN  # noqa: F401

PLATFORMS = ["vacuum"]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEVICE_DEFAULT_NAME): cv.string,
        vol.Required(CONF_MODEL): cv.ensure_list(SUPPORTED_MODELS),
        vol.Required(CONF_TOKEN): cv.string,
        vol.Required(CONF_HOST): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Xiaomi Viomi from a config entry."""
    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    return all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
