"""Platform for Crestron Switch integration."""

from homeassistant.components.switch import SwitchEntity 
import logging

DOMAIN='crestron'

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    hub = hass.data[DOMAIN]['hub']
    entity = [CrestronSwitch(hub, config)]
    async_add_entities(entity)

class CrestronSwitch(SwitchEntity):

    def __init__(self, hub, config):
        self._hub = hub
        self._name = config['name']
        self._switch_join = config['switch_join']
        if 'device_class' in config:
            self._device_class = config['device_class']
        else:
            self._device_class = "switch"

    async def async_added_to_hass(self):
        self._hub.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        self._hub.remove_callback(self.async_write_ha_state)

    @property
    def available(self):
        return self._hub.available

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
         return self._hub.digital[self._switch_join]

    async def async_turn_on(self, **kwargs):
        self._hub.set_digital(self._switch_join, True)

    async def async_turn_off(self, **kwargs):
        self._hub.set_digital(self._switch_join, False)
