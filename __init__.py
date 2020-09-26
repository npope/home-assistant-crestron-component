"""The Crestron Integration Component"""

import asyncio
import logging 
import time

from homeassistant.helpers.discovery import async_load_platform
from . import crestron

_LOGGER = logging.getLogger(__name__)

DOMAIN='crestron'

PLATFORMS = ["binary_sensor", "sensor", "switch", "light", "climate", "cover"]
PORT = 54321

async def async_setup(hass, config):
    """Set up a the crestron component."""
    hass.data[DOMAIN] = {}

    hub = crestron.CrestronHub()
    hass.data[DOMAIN]['hub'] = hub
    await hub.listen(hass, PORT)

    for platform in PLATFORMS:
        async_load_platform(hass, platform, DOMAIN, {}, config)

    return True
