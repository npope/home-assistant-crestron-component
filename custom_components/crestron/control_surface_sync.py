"""Synchronize Joins with Home Assistant state/services"""

import asyncio
import logging 

from homeassistant.helpers.event import TrackTemplate, async_track_template_result
from homeassistant.helpers.template import Template
from homeassistant.helpers.script import Script
from homeassistant.core import callback, Context
from homeassistant.helpers import config_validation as cv
from homeassistant.const import (
    STATE_ON,
    STATE_OFF,
    CONF_VALUE_TEMPLATE,
    CONF_ATTRIBUTE,
    CONF_ENTITY_ID,
    CONF_SERVICE,
    CONF_SERVICE_DATA
)
from .const import (
    HUB,
    DOMAIN,
    CONF_TO_HUB,
    CONF_FROM_HUB,
    CONF_JOIN,
    CONF_SCRIPT
)

_LOGGER = logging.getLogger(__name__)

class ControlSurfaceSync:

    def __init__(self, hass, config):
        self.hass = hass
        self.hub = hass.data[DOMAIN][HUB]
        self.context = Context()
        self.to_hub = {}
        self.hub.register_sync_all_joins_callback(self.sync_joins_to_hub)
        if CONF_TO_HUB in config[DOMAIN]:
            track_templates = []
            for entity in config[DOMAIN][CONF_TO_HUB]:
                template_string = None
                if CONF_VALUE_TEMPLATE in entity:
                    template_string = entity[CONF_VALUE_TEMPLATE]
                elif CONF_ATTRIBUTE in entity and CONF_ENTITY_ID in entity:
                    template_string = "{{state_attr('" + entity[CONF_ENTITY_ID] + "','" + entity[CONF_ATTRIBUTE] + "')}}"
                elif CONF_ENTITY_ID in entity:
                    template_string = "{{states('" + entity[CONF_ENTITY_ID] + "')}}"
                if template_string:
                    template = Template(template_string, hass)
                    self.to_hub[entity[CONF_JOIN]] = template
                    track_templates.append(TrackTemplate(template, None))
            self.tracker = async_track_template_result(self.hass, track_templates, self.template_change_callback)
        if CONF_FROM_HUB in config[DOMAIN]:
            self.from_hub = config[DOMAIN][CONF_FROM_HUB]
            self.hub.register_callback(self.join_change_callback)

    async def join_change_callback(self, cbtype, value):
        ''' Call service for tracked join change (from_hub)'''
        for join in self.from_hub:
            if cbtype == join[CONF_JOIN]:
                # For digital joins, ignore on>off transitions  (avoids double calls to service for momentary presses)
                if cbtype[:1] == "d" and value == "0":
                    pass
                else:
                    if CONF_SERVICE in join and CONF_SERVICE_DATA in join:
                        data = dict(join[CONF_SERVICE_DATA])
                        _LOGGER.debug(f"join_change_callback calling service {join[CONF_SERVICE]} with data = {data} from join {cbtype} = {value}")
                        domain, service = join[CONF_SERVICE].split('.')
                        await self.hass.services.async_call(domain, service, data)
                    elif CONF_SCRIPT in join:
                        sequence = cv.SCRIPT_SCHEMA(join[CONF_SCRIPT])
                        script = Script(self.hass, sequence, "Crestron Join Change", DOMAIN)
                        await script.async_run({"value": value}, self.context)
                        _LOGGER.debug(f"join_change_callback calling script {join[CONF_SCRIPT]} from join {cbtype} = {value}")

    @callback
    def template_change_callback(self, event, updates):
        ''' Set join from value_template (to_hub)'''
        #track_template_result = updates.pop()
        for track_template_result in updates:
            update_result = track_template_result.result
            update_template = track_template_result.template
            if update_result != "None":
                for join, template in self.to_hub.items():
                    if template == update_template:
                        _LOGGER.debug(f"processing template_change_callback for join {join} with result {update_result}")
                        # Digital Join
                        if join[:1] == "d":
                            value = None
                            if update_result == STATE_ON or update_result == "True":
                                value = True
                            elif update_result == STATE_OFF or update_result == "False":
                                value = False
                            if value is not None:
                                _LOGGER.debug(f"template_change_callback setting digital join {int(join[1:])} to {value}")
                                self.hub.set_digital(int(join[1:]), value)
                        # Analog Join
                        if join[:1] == "a":
                            _LOGGER.debug(f"template_change_callback setting analog join {int(join[1:])} to {int(update_result)}")
                            self.hub.set_analog(int(join[1:]), int(update_result))
                        # Serial Join
                        if join[:1] == "s":
                            _LOGGER.debug(f"template_change_callback setting serial join {int(join[1:])} to {str(update_result)}")
                            self.hub.set_serial(int(join[1:]), str(update_result))

    async def sync_joins_to_hub(self):
        _LOGGER.debug("Syncing joins to control system")
        for join, template in self.to_hub.items():
            result = template.async_render()
            # Digital Join
            if join[:1] == "d":
                value = None
                if result == STATE_ON or result == "True":
                    value = True
                elif result == STATE_OFF or result == "False":
                    value = False
                if value is not None:
                    _LOGGER.debug(f"template_change_callback setting digital join {int(join[1:])} to {value}")
                    self.hub.set_digital(int(join[1:]), value)
            # Analog Join
            if join[:1] == "a":
                _LOGGER.debug(f"template_change_callback setting analog join {int(join[1:])} to {int(result)}")
                self.hub.set_analog(int(join[1:]), int(result))
            # Serial Join
            if join[:1] == "s":
                _LOGGER.debug(f"template_change_callback setting serial join {int(join[1:])} to {str(result)}")
                self.hub.set_serial(int(join[1:]), str(result))

    def stop(self):
        ''' remove callback(s) and template trackers '''
        self.hub.remove_callback(self.join_change_callback)
        self.tracker.async_remove()

