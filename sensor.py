"""Platform for Crestron Sensor integration."""

from homeassistant.helpers.entity import Entity
import logging

DOMAIN='crestron'

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    hub = hass.data[DOMAIN]['hub']
    entity = [CrestronSensor(hub, config)]
    async_add_entities(entity)


class CrestronSensor(Entity):

    def __init__(self, hub, config):
        self._hub = hub
        self._name = config['name']
        self._join = config['value_join']
        self._device_class = config['device_class']
        self._unit_of_measurement = config['unit_of_measurement']
        if 'divisor' in config:
            self._divisor = config['divisor']
        else:
            self._divisor = 1

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
    def state(self):
        return self._hub.get_analog(self._join)/self._divisor

    @property
    def device_class(self):
        return self._device_class

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement
