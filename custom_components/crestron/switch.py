"""Platform for Crestron Switch integration."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import (
    STATE_ON,
    STATE_OFF,
    CONF_NAME,
    CONF_DEVICE_CLASS
)
from .const import (
    HUB,
    DOMAIN,
    CONF_SWITCH_JOIN
)
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    hub = hass.data[DOMAIN][HUB]
    entity = [CrestronSwitch(hub, config)]
    async_add_entities(entity)

class CrestronSwitch(SwitchEntity):

    def __init__(self, hub, config):
        self._hub = hub
        self._name = config[CONF_NAME]
        self._switch_join = config[CONF_SWITCH_JOIN]
        if CONF_DEVICE_CLASS in config:
            self._device_class = config[CONF_DEVICE_CLASS]
        else:
            self._device_class = "switch"

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
    def should_poll(self):
        return False

    @property
    def device_class(self):
        return self._device_class

    @property
    def state(self):
         if self._hub.get_digital(self._switch_join):
             return STATE_ON
         else:
             return STATE_OFF

    @property
    def is_on(self):
         return self._hub.get_digital(self._switch_join)

    async def async_turn_on(self, **kwargs):
        self._hub.set_digital(self._switch_join, True)

    async def async_turn_off(self, **kwargs):
        self._hub.set_digital(self._switch_join, False)
