"""Platform for Crestron Light integration."""

from homeassistant.components.light import LightEntity, SUPPORT_BRIGHTNESS
from homeassistant.const import CONF_NAME, CONF_TYPE
from .const import HUB, DOMAIN, CONF_BRIGHTNESS_JOIN

import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    hub = hass.data[DOMAIN][HUB]
    entity = [CrestronLight(hub, config)]
    async_add_entities(entity)


class CrestronLight(LightEntity):
    def __init__(self, hub, config):
        self._hub = hub
        self._name = config[CONF_NAME]
        self._brightness_join = config[CONF_BRIGHTNESS_JOIN]
        if config[CONF_TYPE] == "brightness":
            self._supported_features = SUPPORT_BRIGHTNESS

    async def async_added_to_hass(self):
        self._hub.register_callback(self.process_callback)

    async def async_will_remove_from_hass(self):
        self._hub.remove_callback(self.process_callback)

    async def process_callback(self, cbtype, value):
        self.async_write_ha_state()

    @property
    def available(self):
        return self._hub.is_available()

    @property
    def name(self):
        return self._name

    @property
    def supported_features(self):
        return self._supported_features

    @property
    def should_poll(self):
        return False

    @property
    def brightness(self):
        if self._supported_features == SUPPORT_BRIGHTNESS:
            return int(self._hub.get_analog(self._brightness_join) / 255)

    @property
    def is_on(self):
        if self._supported_features == SUPPORT_BRIGHTNESS:
            if int(self._hub.get_analog(self._brightness_join) / 255) > 0:
                return True
            else:
                return False

    async def async_turn_on(self, **kwargs):
        if "brightness" in kwargs:
            self._hub.set_analog(self._brightness_join, int(kwargs["brightness"] * 255))
        else:
            self._hub.set_analog(self._brightness_join, 65535)

    async def async_turn_off(self, **kwargs):
        self._hub.set_analog(self._brightness_join, 0)
