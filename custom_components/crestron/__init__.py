"""The Crestron Integration Component"""

import asyncio
import logging 
import time

from homeassistant.helpers.discovery import async_load_platform
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change
from homeassistant.core import callback

from .crestron import CrestronHub
from .const import PORT

_LOGGER = logging.getLogger(__name__)

DOMAIN='crestron'

PLATFORMS = ["binary_sensor", "sensor", "switch", "light", "climate", "cover", "media_player"]

async def async_setup(hass, config):
    """Set up a the crestron component."""
    hass.data[DOMAIN] = {}
    if DOMAIN in config:
        if "state_to_join" in config[DOMAIN]:
            hass.data[DOMAIN]['state_to_join'] = config[DOMAIN]['state_to_join']
        if "join_to_service" in config[DOMAIN]:
            hass.data[DOMAIN]['join_to_service'] = config[DOMAIN]['join_to_service']

    async def join_change_callback(cbtype, value):
        ''' Call service for tracked join change (join_to_service)'''
        if 'join_to_service' in hass.data[DOMAIN]:
            for join in hass.data[DOMAIN]['join_to_service']:
                if cbtype == join['join']:
                    # For digital joins, only call service for off>on transition (avoids double calls to service for momentary presses)
                    if cbtype[:1] == "d" and value == "0":
                        pass
                    else:
                        data = dict(join['data'])
                        _LOGGER.debug(f"calling service {join['service']} with data = {data} from join {cbtype} = {value}")
                        domain, service = join['service'].split('.')
                        await hass.services.async_call(domain, service, data);

    @callback
    def state_change_callback(entity_id, old_state, new_state):
        ''' Set join from tracked entity_ids (state to join)'''
        if 'state_to_join' in hass.data[DOMAIN]:
            # step through the config entries for the entities for which we want to track state
            for entity in hass.data[DOMAIN]['state_to_join']:
                # Does the config entry match the entity id in the callback?
                if entity['entity_id'] == entity_id:
                    join = entity['join']
                    # if the config entry specifies an attribute, then send that attribute
                    if "attribute" in entity: 
                        attribute = entity['attribute']
                        # Does new_state.attributes contain the attribute we want to send?
                        if attribute in new_state.attributes:
                            _LOGGER.debug(f"setting join {join} = {new_state.attributes[attribute]}: state from {entity_id}")
                            if join[:1] == "a":
                                hub.set_analog(int(join[1:]), new_state.attributes[attribute])
                            if join[:1] == "s":
                                if "prefix" in entity:
                                    hub.set_serial(int(join[1:]), f"{entity['prefix']}{new_state.attributes[attribute]}")
                                else:
                                    hub.set_serial(int(join[1:]), new_state.attributes[attribute])
                    # Otherwise just send the state
                    else:
                        _LOGGER.debug(f"settting join {join} = {new_state.state}: state from {entity_id}")
                        if join[:1] == "a":
                            hub.set_analog(int(join[1:]), new_state.state)
                        if join[:1] == "s":
                            hub.set_serial(int(join[1:]), new_state.state)

    def stop_logic(event):
        ''' remove callback(s) and stop/diconnect hub '''
        hub.remove_callback(join_change_callback)
        hub.stop()

    hub = crestron.CrestronHub()
    hass.data[DOMAIN]['hub'] = hub

    entities_to_track = set()
    if 'state_to_join' in hass.data[DOMAIN]:
        for entity in hass.data[DOMAIN]['state_to_join']:
            entities_to_track.add(entity['entity_id'])

    # Track configured entities' state from HA
    async_track_state_change(hass, entities_to_track, state_change_callback)

    # Track configured joins from control system
    hub.register_callback(join_change_callback)

    await hub.start(const.PORT)
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, stop_logic)

    for platform in PLATFORMS:
        async_load_platform(hass, platform, DOMAIN, {}, config)

    return True

