"""Platform for Crestron Thermostat integration."""

import voluptuous as vol
import logging

import homeassistant.helpers.config_validation as cv
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    SUPPORT_FAN_MODE,
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
    FAN_AUTO,
)

from homeassistant.const import CONF_NAME

from .const import (
    HUB,
    DOMAIN,
    CONF_HEAT_SP_JOIN,
    CONF_COOL_SP_JOIN,
    CONF_REG_TEMP_JOIN,
    CONF_MODE_HEAT_JOIN,
    CONF_MODE_COOL_JOIN,
    CONF_MODE_AUTO_JOIN,
    CONF_MODE_OFF_JOIN,
    CONF_FAN_ON_JOIN,
    CONF_FAN_AUTO_JOIN,
    CONF_H1_JOIN,
    CONF_H2_JOIN,
    CONF_C1_JOIN,
    CONF_C2_JOIN,
    CONF_FA_JOIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_HEAT_SP_JOIN): cv.positive_int,
        vol.Required(CONF_COOL_SP_JOIN): cv.positive_int,           
        vol.Required(CONF_REG_TEMP_JOIN): cv.positive_int,
        vol.Required(CONF_MODE_HEAT_JOIN): cv.positive_int,
        vol.Required(CONF_MODE_COOL_JOIN): cv.positive_int,
        vol.Required(CONF_MODE_AUTO_JOIN): cv.positive_int,
        vol.Required(CONF_MODE_OFF_JOIN): cv.positive_int,
        vol.Required(CONF_FAN_ON_JOIN): cv.positive_int,
        vol.Required(CONF_FAN_AUTO_JOIN): cv.positive_int,
        vol.Required(CONF_H1_JOIN): cv.positive_int,
        vol.Optional(CONF_H2_JOIN): cv.positive_int,
        vol.Required(CONF_C1_JOIN): cv.positive_int,
        vol.Optional(CONF_C2_JOIN): cv.positive_int,
        vol.Required(CONF_FA_JOIN): cv.positive_int,
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    hub = hass.data[DOMAIN][HUB]
    entity = [CrestronThermostat(hub, config, hass.config.units.temperature_unit)]
    async_add_entities(entity)


class CrestronThermostat(ClimateEntity):
    def __init__(self, hub, config, unit):
        self._hub = hub
        self._hvac_modes = [
            HVAC_MODE_HEAT_COOL,
            HVAC_MODE_HEAT,
            HVAC_MODE_COOL,
            HVAC_MODE_OFF,
        ]
        self._fan_modes = [FAN_ON, FAN_AUTO]
        self._supported_features = SUPPORT_FAN_MODE | SUPPORT_TARGET_TEMPERATURE_RANGE
        self._should_poll = False
        self._temperature_unit = unit

        self._name = config[CONF_NAME]
        self._heat_sp_join = config[CONF_HEAT_SP_JOIN]
        self._cool_sp_join = config[CONF_COOL_SP_JOIN]
        self._reg_temp_join = config[CONF_REG_TEMP_JOIN]
        self._mode_heat_join = config[CONF_MODE_HEAT_JOIN]
        self._mode_cool_join = config[CONF_MODE_COOL_JOIN]
        self._mode_auto_join = config[CONF_MODE_AUTO_JOIN]
        self._mode_off_join = config[CONF_MODE_OFF_JOIN]
        self._fan_on_join = config[CONF_FAN_ON_JOIN]
        self._fan_auto_join = config[CONF_FAN_AUTO_JOIN]
        self._h1_join = config[CONF_H1_JOIN]
        self._h2_join = config.get(CONF_H2_JOIN)
        self._c1_join = config[CONF_C1_JOIN]
        self._c2_join = config.get(CONF_C2_JOIN)
        self._fa_join = config[CONF_FA_JOIN]

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
        return self._hub.get_analog(self._reg_temp_join) / 10

    @property
    def target_temperature_high(self):
        return self._hub.get_analog(self._cool_sp_join) / 10

    @property
    def target_temperature_low(self):
        return self._hub.get_analog(self._heat_sp_join) / 10

    @property
    def hvac_mode(self):
        if self._hub.get_digital(self._mode_auto_join):
            return HVAC_MODE_HEAT_COOL
        if self._hub.get_digital(self._mode_heat_join):
            return HVAC_MODE_HEAT
        if self._hub.get_digital(self._mode_cool_join):
            return HVAC_MODE_COOL
        if self._hub.get_digital(self._mode_off_join):
            return HVAC_MODE_OFF

    @property
    def fan_mode(self):
        if self._hub.get_digital(self._fan_auto_join):
            return FAN_AUTO
        if self._hub.get_digital(self._fan_on_join):
            return FAN_ON

    @property
    def hvac_action(self):
        if self._hub.get_digital(self._h1_join) or self._hub.get_digital(self._h2_join):
            return CURRENT_HVAC_HEAT
        elif self._hub.get_digital(self._c1_join) or self._hub.get_digital(self._c2_join):
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
        self._hub.set_analog(self._heat_sp_join, int(kwargs["target_temp_low"]) * 10)
        self._hub.set_analog(self._cool_sp_join, int(kwargs["target_temp_high"]) * 10)
