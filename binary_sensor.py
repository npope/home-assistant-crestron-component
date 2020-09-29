"""Platform for Crestron Binary Sensor integration."""

from homeassistant.helpers.entity import Entity
import logging

DOMAIN='crestron'

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    hub = hass.data[DOMAIN]['hub']
    entity = [CrestronBinarySensor(hub, config)]
    async_add_entities(entity)

class CrestronBinarySensor(Entity):

    def __init__(self, hub, config):
        self._hub = hub
        self._name = config['name']
        self._join = config['is_on_join']
        self._device_class = config['device_class']

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
    def state(self):
        return self._hub.get_digital(self._join)
