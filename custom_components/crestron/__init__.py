"""The Crestron Integration Component"""

import asyncio
import logging

import voluptuous as vol

from homeassistant.helpers.discovery import async_load_platform
from homeassistant.const import EVENT_HOMEASSISTANT_STOP

from .crestron import CrestronHub
from .const import CONF_PORT, HUB, DOMAIN, CONF_TO_HUB, CONF_FROM_HUB
from .control_surface_sync import ControlSurfaceSync

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = [
    "binary_sensor",
    "sensor",
    "switch",
    "light",
    "climate",
    "cover",
    "media_player",
]


async def async_setup(hass, config):
    """Set up a the crestron component."""
    hass.data[DOMAIN] = {}
    hub = CrestronHub()
    hass.data[DOMAIN][HUB] = hub

    if CONF_TO_HUB in config or CONF_TO_HUB in config:
        syncer = ControlSurfaceSync(hass, config)
    else:
        syncer = None

    def stop(event):
        hub.stop()
        if syncer:
            syncer.stop()

    await hub.start(config(CONF_PORT))
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, stop)

    for platform in PLATFORMS:
        async_load_platform(hass, platform, DOMAIN, {}, config)

    return True
