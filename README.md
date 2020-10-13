# home-assistant-crestron-component
Integration for Home Assistant for the Crestron XSIG symbol

Currently supported devices:
  - Lights (Any device that can be represented as an Analog join for brightness on the control system)
  - Thermostat (Anything that looks like a CHV-TSTAT/THSTAT)
  - Shades (Any shade that uses an analog join for position plus digital joins for is_opening/closing, is_open/closed.  I tested with CSM-QMTDC shades)
  - Binary Sensor (any digital signal on the control system - read only)
  - Sensor (any analog signal on the control system - read only)
  - Switch (any digital signal on the contol system - read / write)
  - Media Player (Can represent a multi-zone switcher.  Tested with PAD8A)

## Adding the component to Home Assistant

  - Add the `crestron` directory to `config/custom_components`
  - Add the appropriate sections to `configuration.yaml` (see below)
  - Restart Home Assistant

## On the control system
 - Add a TCP/IP Client device to the control system
 - Configure the client device with the IP address of Home Assistant
 - Set the port number on the TCP/IP client symbol to 16384 (TODO: make this configurable)
 - Add an "Intersystem Communication" symbol (quick key = xsig).
 - Attach your Analog, Serial and Digital signals to the input/output joins.
   - Note you can use multiple XSIGs attached to the same TCP/IP Client serials.  I found its simplest to use one for digitals and one for analogs/serials to keep the numbering simpler (see below).
  
> Caution: Be careful when mixing analog/serials and digtals on the same XSIG symbol.  Even though the symbol starts numbering the digitals at "1", the XSIG will actually send the join number for where the symbol appears sequentially in the entire list of signals.
> For example, if you have 25 analog signals followed by 10 digital signals attached to the same XSIG, the digitals will be sent as 26-35, not 1-10 (even though they are labeled dig_xx1 - digxx10 on the symbol).  You can either account for this in your configuration on the HA side, or just use one symbol for Analogs and another for Digitals to keep the numbering easy.
> Since the XSIG lets you combine Analog/Serial joins on the same symbol, you can simply have one XSIG for Analog/Serial joins and another for digitals.  This keeps the join numbering simple.
 
## Home Assistant configuration.yaml

Add entries for each HA component/platform type to your configuration.yaml for the appropriate entity type in Home Assistant:

|Crestron Device|Home Assistant component type|
|---|---|
|Light|light|
|Thermostat|climate|
|Shades|cover|
|read-only Digital Join|binary_sensor|
|read-only Analog Join|sensor|
|read-write Digital Join|switch|
|Audio/Video Switcher|media_player|

If you want to make use of the control surface (touchpanels/kepads) syncing capability, you will need to add a `crestron` section as well, with either a `to_joins`, a `from_joins` section, or both (see below).

### Lights

```yaml
light:
  - platform: crestron
    name: "Dummy Light"
    brightness_join: 9
    type: brightness
```
 - _name_: The entity id will be derived from this string (lower-cased with _ for spaces).  The friendly name will be set to this string.
 - _brightness_join_: The analog join on the XSIG symbol that represents the light's brightness.
 - _type_: The only supported value for now is *brightness*.  TODO: add support for other HA light types.

### Thermostat

```yaml
climate:
  - platform: crestron
    name: "Upstairs Thermostat"
    heat_sp_join: 2
    cool_sp_join: 3
    reg_temp_join: 4
    mode_heat_join: 1
    mode_cool_join: 2
    mode_auto_join: 3
    mode_off_join: 4
    fan_on_join: 5
    fan_auto_join: 6
    h1_join: 7
    h2_join: 8
    c1_join: 9
    fa_join: 10
```

This configuration is based on THV-TSTAT/THSTATs, but should work with any thermostat that can be represented by similar analog/digital joins.
- _name_: The entity id will be derived from this string (lower-cased with _ for spaces).  The friendly name will be set to this string.
- _heat_sp_join_: analog join that represents the heat setpoint
- _cool_sp_join_: analog join that represents the cool setpoint
- _reg_temp_join_: analog join that represents the room temperature read by the thermostat.  The CHV-TSTAT calls this the "regulation temperture" because it my be derived from averaging a bunch of room temperature sensors.  This is so called because it is the temperature used by the thermostat to decide when to make calls for heating or cooling.
- _mode_heat_join_: digital feedback (read-only) join that is high when the thermostat is in heating mode
- _mode_heat_join_: digital feedback (read-only) join that is high when the thermostat is in cooling mode
- _mode_auto_join_: digital feedback (read-only) join that is high when the thermostat is in auto mode
- _mode_off_join_: digital feedback (read-only) join that is high when the thermostat mode is set to off
- _fan_on_join_: digital feedback (read-only) join that is high when the thermostat fan mode is set to (always) on
- _fan_on_join_: digital feedback (read-only) join that is high when the thermostat fan mode is set to auto
- _h1_join_: digital feedback (read-only) join that represents the state of the stage 1 heat relay
- _h2_join_: digital feedback (read-only) join that represents the state of the stage 2 heat relay
- _c1_join_: digital feedback (read-only) join that represents the state of the stage 1 cool relay
- _fa_join_: digital feedback (read-only) join that represents the state of the stage fan relay

### Shades

```yaml
cover:
  - platform: crestron
    name: "Living Room Shades"
    type: shade
    pos_join: 26
    is_opening_join: 41
    is_closing_join: 42
    stop_join: 43
    is_closed_join: 44
```
- _name_: The entity id will be derived from this string (lower-cased with _ for spaces).  The friendly name will be set to this string.
- _pos_join_: analog join that represents the shade position.  The value follow the typical definition for a Crestron analog shade (0 = closed, 65535 = open).
- _is_opening_join_: digital feedback (read-only) join that is high when shade is in the process of opening
- _is_closing_join_: digital feedback (read-only) join that is high when shade is in the process of closed
- _is_closed_join_: digital feedback (read-only) join that is high when shade is fully closed
- _stop_join_: digital join that can be pulsed high to stop the shade opening/closing

### Binary Sensor

```yaml
binary_sensor:
  - platform: crestron
    name: "Air Compressor"
    is_on_join: 57
    device_class: power
```

Use this for any digital join in the control system that you would like to represent as a binary sensor (on/off) in Home Assistant.
- _name_: The entity id will be derived from this string (lower-cased with _ for spaces).  The friendly name will be set to this string.
- _is_on_join_: digital feedback (read-only) join to represent as a binary sensor in Home Assistant
- _device_class_: any device class [supported by the binary_sensor](https://www.home-assistant.io/integrations/binary_sensor/) integration.  This mostly affects how the value will be expressed in various UIs.

### Sensor

```yaml
sensor:
  - platform: crestron
    name: "Outside Temperature"
    value_join: 1
    device_class: "temperature"
    unit_of_measurement: "F"
    divisor: 10
```
Use this for any analog join in the control system that you would like to represent as a sensor in Home Assistant.
- _name_: The entity id will be derived from this string (lower-cased with _ for spaces).  The friendly name will be set to this string.
- _value_join_: analog join to represent as a sensor in Home Assistant
- _device_class_: any device class [supported by the sensor](https://www.home-assistant.io/integrations/sensor/) integration.  This mostly affects how the value will be expressed in various UIs.
- _unit_of_measurement_: Unit of measurement appropriate for the device class as documented [here](https://developers.home-assistant.io/docs/core/entity/sensor/).
- _divisor_: (optional) number to divide the analog join by to get the correct sensor value.  For example, a crestron temperature sensor returns tenths of a degree (754 represents 75.4 degrees), so you would use a divisor of 10.  Defaults to 1.

### Switch

```yaml
switch:
  - platform: crestron
    name: "Dummy Switch"
    switch_join: 65
```
Use this for any digital join in the control system that you would like to control via a toggle (on/off) switch in Home Assistant.
- _name_: The entity id will be derived from this string (lower-cased with _ for spaces).  The friendly name will be set to this string.
- _switch_join_: digital join to represent as a switch in Home Assistant

### Media Player

```yaml
media_player:
  - platform: crestron
    name: "Kitchen Speakers"
    mute_join: 27
    volume_join: 19
    source_number_join: 13
    sources:
      1: "Android TV"
      2: "Roku"
      3: "Apple TV"
      4: "Chromecast"
      7: "Volumio"
      8: "Crestron Streamer"
```

You can use this to represent output channels of an AV switcher.  For example a PAD-8A is an 8x8 (8 inputs x 8 outputs) audio switcher.  This can be represented by 8 media player components (one for each output).  This component supported source selection (input selection) and volume+mute control.  So it is modeled as a "speaker" media player type in Home Assistant.
- _name_: The entity id will be derived from this string (lower-cased with _ for spaces).  The friendly name will be set to this string.
- _mute_join_: digital join that represents the mute state of the channel.  Note this is not a toggle. Both to and from the control system True = muted, False = not muted.  This might require some extra logic on the control system side if you only have logic that takes a toggle.
- _volume_join_: analog join that represents the volume of the channel (0-65535)
- _source_number_join_: analog join that represents the selected input for the output channel.  1 would correspond to input 1, 2 to input 2, and so on.
- _sources_: a dictionary of _input_ to _name_ mappings.  The input number is the actual input (corresponding to the source_number_join) number, whereas the name will be shown in the UI when selecting inputs/sources.  So when a user selects the _name_ in the UI, the _source_number_join_ will be set to _input_.

### Control Surface Sync

If you have Crestron touch panels or keypads, it can be useful to keep certain joins in sync with Home Assistant state and to be able to invoke Home Assistant functionality (via a script) when a join changes.  This functionality was added with v0.2.  There are two directions to sync: from HA to the control system and from the control system states to HA.

Since this functionality is not necessarily associated with any HA entity, the configuration will live under the root `crestron:` key in `configuration.yaml`.  There are two sections:
- `to_joins` for syncing HA state to control system joins
- `from_joins` for syncing control system joins to HA

```yaml
crestron:
  to_joins:
  ...
  from_joins:
  ...
```

 #### From HA to the Control System

The `to_joins` section will list all the joins you want to map HA state changes to.  For each join, you list either:
 - a simple `entity_id` with optional `attribute` to map entity state directly to a join.
 - a `value_template` that lets you map almost any combination of state values (including the full power of [template logic](https://www.home-assistant.io/docs/configuration/templating/)) to the listed join.

 ```yaml
 crestron:
  to_joins:
    - join: d12
      entity_id: switch.compressor
    - join: a35
      value_template: "{{value|int * 10}}"
    - join: s4
      value_template: "Current weather conditions: {{state('weather.home')}}"
    - join: a2
      entity_id: media_player.kitchen
      attribute: volume_level
    - join: s4
      value_template: "http://hassio:8123{{ state_attr('media_player.volumio', 'entity_picture') }}"
```  
 
 - _to_joins_: begins the section
 - _join_: for each join, list the join type and number.  The type prefix is 'a' for analog joins, 'd' for digital joins and 's' for serial joins.  So s32 would be serial join #32.  The value of this join will be set to either the state/attribute of the configured entity ID or the output of the configured template.
 - _entity_id_: the entity ID to sync this join to.  If no _attribute_ is listed the join will be set to entity's state value whenever the state changes.
 - _attribute_: use the listed attribute value for the join value instead of the entity's state.
 - _value_template_: used instead of _entity_id_/_attribute_ if you need more flexibility on how to set the value (prefix/suffix or math operations) or even to set the join value based on multiple entity IDs/state values.  You have the full power of [HA templating](https://www.home-assistant.io/docs/configuration/templating/) to work with here.

 >Note that when you specify an `entity_id`, all changes to that entity_id will result in a join update being sent to the control system.  When you specify a `value_template` a change to any referenced entity will trigger a join update.

 #### From Control System to HA
 
 The `from_joins` section will list all the joins you want to track from the control system.  When each join changes the configured functionality will be invoked.

 ```yaml
 from_joins:
    - join: a2
      script:
        service: input_text.set_value
        data:
          entity_id: input_text.test
          value: "Master BR temperature is {{value|int / 10}}"
```

 - _from_joins_: begins the section
 - _join_: for each join, list the join type and number.  The type prefix is 'a' for analog joins, 'd' for digital joins and 's' for serial joins.  So s32 would be serial join #32.  Any change in the listed join will invoke the configured behavior.
 - _script_: This is a standard HA script.  It follows the standard [HA scripting sytax](https://www.home-assistant.io/docs/scripts/).

