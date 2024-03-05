"""Platform for Crestron Sensor integration."""

import voluptuous as vol
import logging

from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_NAME, CONF_DEVICE_CLASS, CONF_UNIT_OF_MEASUREMENT
import homeassistant.helpers.config_validation as cv

from .const import HUB, DOMAIN, CONF_VALUE_JOIN, CONF_DIVISOR

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_VALUE_JOIN): cv.positive_int,           
        vol.Required(CONF_DEVICE_CLASS): cv.string,
        vol.Required(CONF_UNIT_OF_MEASUREMENT): cv.string,
        vol.Required(CONF_DIVISOR): int,
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    hub = hass.data[DOMAIN][HUB]
    entity = [CrestronSensor(hub, config)]
    async_add_entities(entity)


class CrestronSensor(Entity):
    def __init__(self, hub, config):
        self._hub = hub
        self._name = config.get(CONF_NAME)
        self._join = config.get(CONF_VALUE_JOIN)
        self._device_class = config.get(CONF_DEVICE_CLASS)
        self._unit_of_measurement = config.get(CONF_UNIT_OF_MEASUREMENT)
        self._divisor = config.get(CONF_DIVISOR, 1)
        self._unique_id =  f"{self._hub}_sensor_{self._name}"

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
        return self._hub.get_analog(self._join) / self._divisor

    @property
    def device_class(self):
        return self._device_class

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def unique_id(self):
        return self._unique_id
