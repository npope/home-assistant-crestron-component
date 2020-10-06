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
  - Restart Home Assistant

## On the control system
 - Add a TCP/IP Client device to the control system
 - Configure the client device with the IP address of Home Assistant
 - Set the port number on the TCP/IP client symbol to 16384 (TODO: make this configurable)
 - Add an "Intersystem Communication" symbol (quick key = xsig).
 - Attach your Analog and Digital signals to the inputs/outputs.
   - Note you can use multiple XSIGs attached to the same TCP/IP Client serials.  I found its simplest to use one for digitals and one for analogs to keep the numbering simpler (see below).
  
Note: Be careful when mixing analogs and digtals on the same XSIG symbol.  Even though the symbol starts numbering the digitals at "1", the XSIG will actually send the join number for where the symbol appears sequentially in the entire list of signals.  For example, if you have 25 analog signals followed by 10 digital signals attached to the same XSIG, the digitals will be sent as 26-35, not 1-10 (even though they are labeled dig_xx1 - digxx10 on the symbol).  You can either account for this in your configuration on the HA side, or just use one symbol for Analogs and another for Digitals to keep the numbering easy.
 
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

### Lights

```yaml
light:
  - platform: crestron
    name: "Dummy Light"
    brightness_join: 9
    type: brightness
```
 - _name_: The entity id will be derived from this string (lower-cased with _ for spaces).  The friendly name will be set to this string.
 - _brightness_join: The analog join on the XSIG symbol that represents the light's brightness.
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

### Binary Sensor

```yaml
binary_sensor:
  - platform: crestron
    name: "Air Compressor"
    is_on_join: 57
    device_class: power
```
- _name_: The entity id will be derived from this string (lower-cased with _ for spaces).  The friendly name will be set to this string.

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
- _name_: The entity id will be derived from this string (lower-cased with _ for spaces).  The friendly name will be set to this string.

### Switch

```yaml
switch:
  - platform: crestron
    name: "Dummy Switch"
    switch_join: 65
```
- _name_: The entity id will be derived from this string (lower-cased with _ for spaces).  The friendly name will be set to this string.

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
      8: "Crestron Streamer"```

- _name_: The entity id will be derived from this string (lower-cased with _ for spaces).  The friendly name will be set to this string.
