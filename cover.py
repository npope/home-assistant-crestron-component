"""Platform for Crestron Shades integration."""

from homeassistant.helpers.event import call_later
from homeassistant.components.cover import (CoverEntity,
        DEVICE_CLASS_SHADE,
        SUPPORT_OPEN,
        SUPPORT_CLOSE,
        SUPPORT_SET_POSITION,
        SUPPORT_STOP,
        STATE_OPENING,
        STATE_OPEN,
        STATE_CLOSING,
        STATE_CLOSED)
    
import asyncio
import logging

DOMAIN='crestron'

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    hub = hass.data[DOMAIN]['hub']
    entity = [CrestronShade(hub, config)]
    async_add_entities(entity)

class CrestronShade(CoverEntity):

    def __init__(self, hub, config):
        self._hub = hub
        self._device_class = DEVICE_CLASS_SHADE
        self._supported_features = SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_SET_POSITION | SUPPORT_STOP
        self._should_poll = False

        self._name = config['name']
        self._is_opening_join = config['is_opening_join']
        self._is_closing_join = config['is_closing_join']
        self._is_closed_join = config['is_closed_join']
        self._stop_join = config['stop_join']
        self._pos_join = config['pos_join']

    async def async_added_to_hass(self):
        self._hub.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        self._hub.remove_callback(self.async_write_ha_state)

    @property
    def available(self):
        return self._hub.is_available()

    @property
    def name(self):
        return self._name

    @property
    def device_class(self):
        return self._device_class

    @property
    def supported_features(self):
        return self._supported_features

    @property
    def should_poll(self):
        return self._should_poll

    @property
    def current_cover_position(self):
        return self._hub.get_analog(self._pos_join)/655.35

    @property
    def is_opening(self):
        return self._hub.get_digital(self._is_opening_join)

    @property
    def is_closing(self):
        return self._hub.get_digital(self._is_closing_join)

    @property
    def is_closed(self):
        return self._hub.get_digital(self._is_closed_join)

    async def async_set_cover_position(self, **kwargs):
        self._hub.set_analog(self._pos_join, int(kwargs['position'])*655)

    async def async_open_cover(self, **kwargs):
        self._hub.set_analog(self._pos_join, 0xFFFF)

    async def async_close_cover(self, **kwargs):
        self._hub.set_analog(self._pos_join, 0)

    async def async_stop_cover(self, **kwargs):
        self._hub.set_digital(self._stop_join, 1)
        ## TODO: replace sleep with call_later
        #await asyncio.sleep(0.2)
        call_later(self.hass, 0.2, self._hub.set_digital(self._stop_join, 0))
