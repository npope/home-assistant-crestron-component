"""Platform for Crestron Thermostat integration."""

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (SUPPORT_FAN_MODE,
    SUPPORT_TARGET_TEMPERATURE_RANGE,
    HVAC_MODE_OFF,
    HVAC_MODE_HEAT,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT_COOL,
    CURRENT_HVAC_OFF,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_IDLE,
    FAN_ON,
    FAN_AUTO)
    
import logging

DOMAIN='crestron'

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    hub = hass.data[DOMAIN]['hub']
    entity = [CrestronThermostat(hub, config, hass.config.units.temperature_unit)]
    async_add_entities(entity)

class CrestronThermostat(ClimateEntity):

    def __init__(self, hub, config, unit):
        self._hub = hub
        self._hvac_modes = [HVAC_MODE_HEAT_COOL, HVAC_MODE_HEAT, HVAC_MODE_COOL, HVAC_MODE_OFF]
        self._fan_modes = [FAN_ON, FAN_AUTO]
        self._supported_features = SUPPORT_FAN_MODE | SUPPORT_TARGET_TEMPERATURE_RANGE
        self._should_poll = False
        self._temperature_unit = unit

        self._name = config['name']
        self._heat_sp_join = config['heat_sp_join']
        self._cool_sp_join = config['cool_sp_join']
        self._reg_temp_join = config['reg_temp_join']
        self._mode_heat_join = config['mode_heat_join']
        self._mode_cool_join = config['mode_cool_join']
        self._mode_auto_join = config['mode_auto_join']
        self._mode_off_join = config['mode_off_join']
        self._fan_on_join = config['fan_on_join']
        self._fan_auto_join = config['fan_auto_join']
        self._h1_join = config['h1_join']
        self._h2_join = config['h2_join']
        self._c1_join = config['c1_join']
        self._fa_join = config['fa_join']


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
    def hvac_modes(self):
        return self._hvac_modes

    @property
    def fan_modes(self):
        return self._fan_modes

    @property
    def supported_features(self):
        return self._supported_features

    @property
    def should_poll(self):
        return self._should_poll

    @property
    def temperature_unit(self):
        return self._temperature_unit

    @property
    def current_temperature(self):
        return self._hub.analog[self._reg_temp_join]/10

    @property
    def target_temperature_high(self):
        return self._hub.analog[self._cool_sp_join]/10

    @property
    def target_temperature_low(self):
        return self._hub.analog[self._heat_sp_join]/10

    @property
    def hvac_mode(self):
        if self._hub.digital[self._mode_auto_join]:
            return HVAC_MODE_HEAT_COOL
        if self._hub.digital[self._mode_heat_join]:
            return HVAC_MODE_HEAT
        if self._hub.digital[self._mode_cool_join]:
            return HVAC_MODE_COOL
        if self._hub.digital[self._mode_off_join]:
            return HVAC_MODE_OFF

    @property
    def fan_mode(self):
        if self._hub.digital[self._fan_auto_join]:
            return FAN_AUTO
        if self._hub.digital[self._fan_on_join]:
            return FAN_ON

    @property
    def hvac_action(self):
        if self._hub.digital[self._h1_join]:
            return CURRENT_HVAC_HEAT
        elif self._hub.digital[self._h2_join]:
            return CURRENT_HVAC_HEAT
        elif self._hub.digital[self._c1_join]:
            return CURRENT_HVAC_COOL
        else:
            return CURRENT_HVAC_IDLE


    async def async_set_hvac_mode(self, hvac_mode):
        if hvac_mode == HVAC_MODE_HEAT_COOL:
            self._hub.set_digital(self._mode_cool_join, False)
            self._hub.set_digital(self._mode_off_join, False)
            self._hub.set_digital(self._mode_heat_join, False)
            self._hub.set_digital(self._mode_auto_join, True)
        if hvac_mode == HVAC_MODE_HEAT:
            self._hub.set_digital(self._mode_auto_join, False)
            self._hub.set_digital(self._mode_cool_join, False)
            self._hub.set_digital(self._mode_off_join, False)
            self._hub.set_digital(self._mode_heat_join, True)
        if hvac_mode == HVAC_MODE_COOL:
            self._hub.set_digital(self._mode_auto_join, False)
            self._hub.set_digital(self._mode_off_join, False)
            self._hub.set_digital(self._mode_heat_join, False)
            self._hub.set_digital(self._mode_cool_join, True)
        if hvac_mode == HVAC_MODE_OFF:
            self._hub.set_digital(self._mode_auto_join, False)
            self._hub.set_digital(self._mode_cool_join, False)
            self._hub.set_digital(self._mode_heat_join, False)
            self._hub.set_digital(self._mode_off_join, True)

    async def async_set_fan_mode(self, fan_mode):
        if fan_mode == FAN_AUTO:
            self._hub.set_digital(self._fan_on_join, False)
            self._hub.set_digital(self._fan_auto_join, True)
        if fan_mode == FAN_ON:
            self._hub.set_digital(self._fan_auto_join, False)
            self._hub.set_digital(self._fan_on_join, True)

    async def async_set_temperature(self, **kwargs):
        self._hub.set_analog(self._heat_sp_join, int(kwargs['target_temp_low'])*10)
        self._hub.set_analog(self._cool_sp_join, int(kwargs['target_temp_high'])*10)
