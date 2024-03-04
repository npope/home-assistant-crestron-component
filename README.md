# Credit

Fork based on the great work by npope@, all credit to the original author. Please refer to the original README for more details on how to use this.

Below are the changes I added:

# Manually setting joins
Added crestron.set_(digital/analog/serial) to allow manually setting the value of a join from automation.

For example, you can set this on a button to trigger a change of analgo join 52 to value 2 when the button is pressed:

```yaml
  tap_action:
      action: call-service
      service: crestron.set_analog
      data:
        join: 51
        value_join: 2
```

# Improvements to the media player
- Added volume up/down functiosn that pulse a digital join.
- Changed the mute function to be a toggle that pulses a digital join. This better suits my project.

# Improvements to lights
- Change the divider to 257, allowing full range (0-255 -> -=65535)
- Add an default brightness per light (otherwise default to 50%)
