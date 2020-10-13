"""The Crestron Integration Component"""

import asyncio
import logging 

from homeassistant.helpers.discovery import async_load_platform
from homeassistant.const import EVENT_HOMEASSISTANT_STOP

from .crestron import CrestronHub
from .const import PORT
from .control_surface_sync import ControlSurfaceSync

_LOGGER = logging.getLogger(__name__)

DOMAIN='crestron'

PLATFORMS = ["binary_sensor", "sensor", "switch", "light", "climate", "cover", "media_player"]

async def async_setup(hass, config):
    """Set up a the crestron component."""
    hass.data[DOMAIN] = {}
    hub = crestron.CrestronHub()
    hass.data[DOMAIN]['hub'] = hub

    if DOMAIN in config:
        syncer = ControlSurfaceSync(hass, config)
    else:
        syncer = None

    def stop(event):
        hub.stop()
        if syncer:
            syncer.stop()

    await hub.start(const.PORT)
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, stop)

    for platform in PLATFORMS:
        async_load_platform(hass, platform, DOMAIN, {}, config)

    return True

