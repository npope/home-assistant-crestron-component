# home-assistant-crestron-component
Integration for Home Assistant for the Crestron XSIG symbol

Currently supported devices:
  - Lights (represented as an Analog brightness value on the control system)
  - Thermostat (CHV-TSTAT/THSTAT for now)
  - Shades (I tested with CSM-QMTDC shades)
  - Binary Sensor (any digital signal on the control system - read only)
  - Sensor (any analog signal on the control system)
  - Switch (any digital signal on the contol system - read / write)

## On the control system
 - Add a TCP/IP Client device to the control system
 - Configure the client device with the IP address of Home Assistant
 - Add the port number to the TCP/IP client symbol
 - Add an "Intersystem Communication" symbol (quick key = xsig).
 - Attach your Analog and Digital signals to the inputs/outputs.
 
## Home Assistant configuration.yaml

Add the following to your configuration.yaml for the appropriate entity type in Home Assistant

### Lights

```yaml
light:
  - platform: crestron
    name: "Dummy Light"
    brightness_join: 9
    type: brightness
```

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

### Binary Sensor

```yaml
binary_sensor:
  - platform: crestron
    name: "Air Compressor"
    is_on_join: 57
    device_class: power
```

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

### Switch

```yaml
switch:
  - platform: crestron
    name: "Dummy Switch"
    switch_join: 65
```

## Adding the component to Home Assistant

  - Add the `crestron` directory to `config/custom_components`
  - Restart Home Assistant
